#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# combins visual and sending-> player_class controlling


import sys
import time
import socket
import select

import numpy as np
import pygame

from network import Network_c
from player import Player
from game import Gameboard
from client_gui import client_gui


# get user inputs via gui

c_gui = client_gui(nickname="user",
                   ip=socket.gethostbyname(socket.gethostname()), port=5555)

c_inputs = c_gui.get_inputs()


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

gameboard = Gameboard(WIDTH_NUM, HEIGHT_NUM, PLAYER_NUM)
player = Player(gameboard)

clock = pygame.time.Clock()

while run:
    clock.tick(60)
    connection = [network.client]
    readable, writable, errored = select.select(connection, connection,
                                                connection, 0.5)

    if readable:
        msg = network.recieve()
        if msg[0] == "positions":
            player_pos = msg[1]
            print("got player_pos")
        elif msg[0] == "next player":
            print("got next player")
            player_turn_num = msg[1]
        elif msg[0] == "your number":
            your_number = msg[1]
            print(f"my number: {your_number}")
            pygame.display.set_caption(f"Player {your_number}")
        elif msg[0] == "viewer":
            pygame.display.set_caption("Viewer")
        elif msg[0] is None:
            print("empty")
        else:
            print(f"Unkown message: {msg}")
    gameboard.update_window(player_pos, player_turn_num)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            network.send(("ByeBye", None))
            network.close()
        if event.type == pygame.VIDEORESIZE:
            gameboard.rescale_window(event.w, event.h, player_pos, player_turn_num)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            pos = player.mouse_pos(mouse_x, mouse_y)
            if writable:
                network.send(("position", pos))
    pygame.display.update()
