#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# combins visual and sending-> player_class controlling


import sys
import time
import select
import socket
import ast
import uuid

import numpy as np
import pygame

from network import Network_c
from player import Player
from game import Gameboard
from client_gui import client_gui, client_quit_gui, client_gui_restart
from configfile import load_config, get_config, get_config_none, get_config_bool, DEFAULTS
from loggingsetup import setup_logging, formatted_traceback


pygame.init()
client_uuid = str(uuid.uuid4())  # to differentiate users
logger = setup_logging("client.log.jsonl")
logger.debug("New client started!", extra={"client_uuid": client_uuid})
try:
    try:
        # load config
        config = load_config()
        fps_limit = int(get_config(config, DEFAULTS, "CLIENT", "fps_limit"))
        box_min_size = int(get_config(config, DEFAULTS, "CLIENT", "box_min_size"))
        box_line_width = int(get_config(config, DEFAULTS, "CLIENT", "box_line_width"))
        board_color = ast.literal_eval(get_config(config, DEFAULTS, "CLIENT", "board_color"))
        pygame.Color(board_color)  # tests for valid color
        player_colors = ast.literal_eval(get_config(config, DEFAULTS, "CLIENT", "player_colors"))
        for player_color in player_colors:
            pygame.Color(player_color)  # tests for valid player colors
        nickname = get_config_none(config, DEFAULTS, "CLIENT", "nickname", str)
        if nickname is not None:
            nickname.encode("utf-8", "strict")  # tests for valid uft-8 name
        ip = get_config_none(config, DEFAULTS, "CLIENT", "ip", str)
        socket.inet_pton(socket.AF_INET, ip)  # tests for valid ip4
        port = int(get_config(config, DEFAULTS, "CLIENT", "port"))
        be_player = get_config_bool(config, DEFAULTS, "CLIENT", "be_player")
    except Exception as err:
        logger.error("Error in loading config!",
                     extra={"client_uuid": client_uuid,
                            "traceback": formatted_traceback(err)})
        sys.exit()

    logger.debug("Config loaded", extra={"client_uuid": client_uuid,
                                         "fps_limit": fps_limit,
                                         "box_min_size": box_min_size,
                                         "box_line_width": box_line_width})
    try:
        # get user inputs via gui
        c_gui = client_gui(nickname=nickname, ip=ip, port=port, player=be_player)
        c_inputs = c_gui.get_inputs()
        c_inputs["nickname"] = c_inputs["nickname"] if not len(c_inputs["nickname"].strip()) == 0 else client_uuid[:20]
    except Exception as err:
        logger.exception("Error in gui input!",
                         extra={"client_uuid": client_uuid,
                                "traceback": formatted_traceback(err)})
        sys.exit()

    restart = True
    session_uuid = None
    while restart:
        finish_message = None
        if session_uuid is None:
            logger.debug("restart", extra={"client_uuid": client_uuid})
        else:
            logger.debug("restart", extra={"client_uuid": client_uuid,
                                           "session_uuid": session_uuid})
        if not pygame.display.get_init():
            pygame.display.init()

        # initial handshake
        network = Network_c(c_inputs["ip"], c_inputs["port"], logger, client_uuid)
        if not network.connect():
            sys.exit()
        network.setblocking(False)
        logger.info("Connected!", extra={"client_uuid": client_uuid})

        handshake_infos = network.handshake(c_inputs["nickname"], c_inputs["player"])
        PLAYER_NUM = handshake_infos["player_num"]
        WIDTH_NUM = handshake_infos["width"]
        HEIGHT_NUM = handshake_infos["height"]
        session_uuid = handshake_infos["session_uuid"]

        logger.info("Handshake done!", extra={"client_uuid": client_uuid,
                                              "session_uuid": session_uuid})
        logger.debug("Handshake done!", extra={"client_uuid": client_uuid,
                                               "session_uuid": session_uuid,
                                               "player_num": PLAYER_NUM,
                                               "width_num": WIDTH_NUM,
                                               "height_num": HEIGHT_NUM})

        # start game
        player_turn_num = 0
        player_pos = {}
        for num in range(PLAYER_NUM):
            player_pos[num] = np.zeros((HEIGHT_NUM, WIDTH_NUM), dtype=int)
        run = True

        gameboard = Gameboard(box_min_size, box_line_width, PLAYER_NUM, board_color,
                              WIDTH_NUM, HEIGHT_NUM, player_colors)
        player = Player(gameboard)

        clock = pygame.time.Clock()

        round_num = 0
        logger.debug("Game loop started!", extra={"client_uuid": client_uuid,
                                                  "session_uuid": session_uuid})
        while run:
            # game loop
            pygame.display.update()
            clock.tick(fps_limit)
            connection = [network.client]
            readable, writable, errored = select.select(connection, connection,
                                                        connection, 0.5)

            if readable:
                msg = network.recieve()
                if msg[0] == "positions":
                    player_pos = msg[1]
                    logger.debug("Recieved player positions",
                                 extra={"client_uuid": client_uuid,
                                        "session_uuid": session_uuid,
                                        "player_pos": player_pos})
                elif msg[0] == "next player":
                    player_turn_num, round_num = msg[1]
                    logger.debug("Recieved next player",
                                 extra={"client_uuid": client_uuid,
                                        "session_uuid": session_uuid,
                                        "player_turn_num": player_turn_num,
                                        "round_num": round_num})
                elif msg[0] == "your number":
                    your_number = msg[1]
                    logger.debug("Recieved own number",
                                 extra={"client_uuid": client_uuid,
                                        "session_uuid": session_uuid,
                                        "your_number": your_number})
                    pygame.display.set_caption(f"{handshake_infos['nicknames'][your_number]}")
                elif msg[0] == "viewer":
                    logger.debug("Recieved spectator",
                                 extra={"client_uuid": client_uuid,
                                        "session_uuid": session_uuid})
                    pygame.display.set_caption("Viewer")
                elif msg[0] == "finished":
                    run = False
                    network.close()
                    logger.debug("Recieved finished",
                                 extra={"client_uuid": client_uuid,
                                        "session_uuid": session_uuid,
                                        "winner": msg[1][0],
                                        "time_line": msg[1][1]})
                    print(f"winner: {handshake_infos['nicknames'][msg[1][0]]}")
                    finish_message = msg[1]
                    break
                elif msg[0] == None:
                    logger.info("Connection closed by server!",
                                 extra={"client_uuid": client_uuid,
                                        "session_uuid": session_uuid})
                    run = False
                    network.close()
                    break
                else:
                    logger.warning("Recieved unknown msg",
                                   extra={"client_uuid": client_uuid,
                                          "session_uuid": session_uuid,
                                          "recieved": msg})
            if errored:
                run = False
                network.close()
                logger.error("Connection failed!",
                             extra={"client_uuid": client_uuid,
                                    "session_uuid": session_uuid})
                sys.exit()

            gameboard.update_window(player_pos, player_turn_num,
                                    handshake_infos["nicknames"], round_num)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_gui = client_quit_gui()
                    if quit_gui.quit:
                        run = False
                        network.send(("ByeBye", None))
                        network.close()
                        logger.debug("Game closed!",
                                     extra={"client_uuid": client_uuid,
                                            "session_uuid": session_uuid})
                if event.type == pygame.VIDEORESIZE:
                    gameboard.rescale_window(event.w, event.h, player_pos, player_turn_num,
                                             handshake_infos["nicknames"], round_num)
                    logger.debug("Resized", extra={"client_uuid": client_uuid,
                                                   "session_uuid": session_uuid,
                                                   "width": event.w,
                                                   "height": event.h})
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        command = player.mouse_pos(mouse_x, mouse_y)
                        if command is not None:
                            network.send(command)
                        logger.debug("Mouse click", extra={"client_uuid": client_uuid,
                                                           "session_uuid": session_uuid,
                                                           "pos": (mouse_x, mouse_y),
                                                           "command": command})

        logger.debug("Game loop stopped!", extra={"client_uuid": client_uuid,
                                                  "session_uuid": session_uuid})
        pygame.display.quit()

        try:
            restart_gui = client_gui_restart(c_inputs["nickname"],
                                             c_inputs["player"],
                                             player_colors, PLAYER_NUM,
                                             handshake_infos['nicknames'],
                                             finish_message)
            restart_input = restart_gui.get_inputs()
            c_inputs["nickname"] = restart_input["nickname"]
            c_inputs["player"] = restart_input["player"]
        except Exception as err:
            logger.exception("Error in restart gui input!",
                             extra={"client_uuid": client_uuid,
                                    "traceback": formatted_traceback(err)})
            sys.exit()

    pygame.quit()
    logger.debug("Client stopped!", extra={"client_uuid": client_uuid,
                                           "session_uuid": session_uuid})
except Exception as err:
    logger.critical("Unexpected Error!",
                    extra={"client_uuid": client_uuid,
                           "traceback": formatted_traceback(err)})
    time.sleep(2)
