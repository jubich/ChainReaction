#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# combins visual and sending-> player_class controlling


import sys
import time
import socket
import select
import ast

import numpy as np
import pygame

from network import Network_c
from player import Player
from game import Gameboard
from client_gui import client_gui, client_quit_gui, client_gui_restart
from configfile import load_config, get_config, get_config_none, DEFAULTS

pygame.init()

# load config
config = load_config()
fps_limit = int(get_config(config, DEFAULTS, "CLIENT", "fps_limit"))
box_min_size = int(get_config(config, DEFAULTS, "CLIENT", "box_min_size"))
box_line_width = int(get_config(config, DEFAULTS, "CLIENT", "box_line_width"))
board_color = ast.literal_eval(get_config(config, DEFAULTS, "CLIENT", "board_color"))
player_colors = ast.literal_eval(get_config(config, DEFAULTS, "CLIENT", "player_colors"))
nickname = get_config_none(config, DEFAULTS, "CLIENT", "nickname", str)
ip = get_config_none(config, DEFAULTS, "CLIENT", "ip", str)
port = int(get_config(config, DEFAULTS, "SERVER", "port"))

# get user inputs via gui
c_gui = client_gui(nickname=nickname, ip=ip, port=port)

c_inputs = c_gui.get_inputs()

restart = True
while restart:
    if not pygame.display.get_init():
        pygame.display.init()

    # initial handshake
    network = Network_c(c_inputs["ip"], c_inputs["port"])
    if not network.connect():
        print("Connection failed")
        time.sleep(2)
        sys.exit()
    network.setblocking(False)

    handshake_infos = network.handshake(c_inputs["nickname"])
    print("Handshake done!")
    PLAYER_NUM = handshake_infos["player_num"]
    WIDTH_NUM = handshake_infos["width"]
    HEIGHT_NUM = handshake_infos["height"]

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
                print("got player_pos")
            elif msg[0] == "next player":
                player_turn_num, round_num = msg[1]
                print("Next player:", handshake_infos["nicknames"][player_turn_num])
            elif msg[0] == "your number":
                your_number = msg[1]
                print(f"my number: {your_number}")
                pygame.display.set_caption(f"{handshake_infos['nicknames'][your_number]}")
            elif msg[0] == "viewer":
                pygame.display.set_caption("Viewer")
            elif msg[0] == "finished":
                run = False
                network.close()
                print(f"winner: {handshake_infos['nicknames'][msg[1]]}")
                time.sleep(1)
                # winner screen
                break
            elif msg[0] is None:
                print("empty")
            else:
                print(f"Unkown message: {msg}")
        gameboard.update_window(player_pos, player_turn_num,
                                handshake_infos["nicknames"], round_num)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_gui = client_quit_gui()
                if quit_gui.quit:
                    run = False
                    network.send(("ByeBye", None))
                    network.close()
            if event.type == pygame.VIDEORESIZE:
                gameboard.rescale_window(event.w, event.h, player_pos, player_turn_num,
                                         handshake_infos["nicknames"], round_num)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                command = player.mouse_pos(mouse_x, mouse_y)
                if command is not None:
                    network.send(command)

    pygame.display.quit()
    restart_gui = client_gui_restart(c_inputs["nickname"])
    restart_input = restart_gui.get_inputs()
    c_inputs["nickname"] = restart_input["nickname"]

pygame.quit()
