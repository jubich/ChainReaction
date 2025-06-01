#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Main file to start for a client process.

To play the game a player/spectator needs to start a client process. This deals with the
visualtisation of the game, the user inputs and the communication with the server.
"""


from __future__ import annotations
from typing import Dict, Any, Tuple, List
import sys
import time
import select
import uuid
import logging

import numpy as np
import pygame

from chainreaction.network import Network_c
from chainreaction.game import Gameboard
from chainreaction.client_gui import client_gui, client_quit_gui, client_gui_restart
from chainreaction.configfile import load_config_c
from chainreaction.loggingsetup import setup_logging, formatted_traceback


def _game_loop(logger: logging.Logger, session_uuid: str, client_uuid: str, network: Network_c,
               config: Dict[str, Any], handshake_infos: Dict[str, Any]) -> Tuple[int, Dict[int, List[List[int]]]] | None:
    """Starts a game.

    Communicates to the server via sockets. Visualizes the game and gathers user inputs
    to send to the server. Recieves game status from the server. Exits via
    "sys.exit" if problem occurred.

    Args:
        logger: Logs the progress and state of the game/function.
        session_uuid: Differentiates different games sessions in log-files.
        client_uuid: Differentiates different clients in log-files.
        network: Main class for dealing with sending and recieving of data via sockets.
        config: Contains infos loaded from config files.
        handshake_infos: Conatins infos from the handshake.

    Returns
        finish_message: Contains the "player_number" of the winner and a dictionary
          with the information about the game evolution ("time line").
          Is None if not recieved.
    """
    finish_message = None
    player_pos = {}
    for num in range(handshake_infos["player_num"]):
        player_pos[num] = np.zeros((handshake_infos["height"], handshake_infos["width"]), dtype=int)
    gameboard = Gameboard(config["box_min_size"], config["box_line_width"],
                          handshake_infos["player_num"], config["board_color"],
                          handshake_infos["width"], handshake_infos["height"],
                          config["player_colors"])

    clock = pygame.time.Clock()
    round_num = 0
    player_turn_num = 0
    logger.debug("Game loop started!", extra={"client_uuid": client_uuid,
                                              "session_uuid": session_uuid})
    run = True
    while run:
        # game loop
        pygame.display.update()
        clock.tick(config["fps_limit"])
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

            elif msg[0] == "spectator":
                logger.debug("Recieved spectator",
                             extra={"client_uuid": client_uuid,
                                    "session_uuid": session_uuid})
                pygame.display.set_caption("Spectator")

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
                    command = gameboard.mouse_pos(mouse_x, mouse_y)
                    if command is not None:
                        network.send(command)
                    logger.debug("Mouse click", extra={"client_uuid": client_uuid,
                                                       "session_uuid": session_uuid,
                                                       "pos": (mouse_x, mouse_y),
                                                       "command": command})

    pygame.display.quit()
    return finish_message


def _main(client_uuid: str, logger: logging.Logger) -> None:
    """Gathers necessarry information for starting "_game_loop".

    Deals with loading the config file, getting user input. After that the
    "restart-loop" is entered which deals with connecting to the server, the
    handshake process, starting of the "_game_loop" and dealing with the user
    inputs after a game. Exits via "sys.exit" if problem occurred.

    Args:
        client_uuid: Differentiates different clients in log-files.
        logger: Logs the progress and state of the game/function.
    """
    # load config
    try:
        config = load_config_c()
    except Exception as err:
        logger.error("Error in loading config!",
                     extra={"client_uuid": client_uuid,
                            "traceback": formatted_traceback(err)})
        sys.exit()
    logger.debug("Config loaded", extra={"client_uuid": client_uuid,
                                         "config": config})

    # get user input via gui
    try:
        c_gui = client_gui(nickname=config["nickname"], ip=config["ip"],
                           port=config["port"], be_player=config["be_player"])
        c_inputs = c_gui.get_inputs(client_uuid)
    except Exception as err:
        logger.exception("Error in gui input!",
                         extra={"client_uuid": client_uuid,
                                "traceback": formatted_traceback(err)})
        sys.exit()
    logger.debug("Inputs", extra={"client_uuid": client_uuid,
                                  "be_player": c_inputs["be_player"]})

    restart = True
    session_uuid = None
    while restart:
        if session_uuid is None:
            logger.debug("start", extra={"client_uuid": client_uuid})
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

        handshake_infos = network.handshake(c_inputs["nickname"], c_inputs["be_player"])
        session_uuid = handshake_infos["session_uuid"]

        logger.info("Handshake done!", extra={"client_uuid": client_uuid,
                                               "session_uuid": session_uuid,
                                               "player_num": handshake_infos["player_num"],
                                               "width_num": handshake_infos["width"],
                                               "height_num": handshake_infos["height"]})

        # start game
        finish_message = _game_loop(logger, session_uuid, client_uuid, network,
                                   config, handshake_infos)

        logger.debug("Game loop stopped!", extra={"client_uuid": client_uuid,
                                                  "session_uuid": session_uuid})

        # get user input via gui
        try:
            restart_gui = client_gui_restart(c_inputs["nickname"],
                                             c_inputs["be_player"],
                                             config["player_colors"],
                                             handshake_infos["player_num"],
                                             handshake_infos['nicknames'],
                                             finish_message)
            c_inputs = restart_gui.get_inputs(c_inputs, client_uuid)
        except Exception as err:
            logger.exception("Error in restart gui input!",
                             extra={"client_uuid": client_uuid,
                                    "be_player": c_inputs["be_player"],
                                    "traceback": formatted_traceback(err)})
            sys.exit()

    pygame.quit()
    logger.debug("Client stopped!", extra={"client_uuid": client_uuid,
                                           "session_uuid": session_uuid})


def main():
    """Starts a chainreaction client."""
    pygame.init()
    client_uuid = str(uuid.uuid4())  # to differentiate users
    logger = setup_logging("client.log.jsonl")
    logger.debug("New client started!", extra={"client_uuid": client_uuid})
    try:
        _main(client_uuid, logger)
    except Exception as err:
        logger.critical("Unexpected Error!",
                        extra={"client_uuid": client_uuid,
                               "traceback": formatted_traceback(err)})
        time.sleep(2)


if __name__ == "__main__":
    main()
