#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# combins visual and sending-> player_class controlling


import pygame
import socket
import select
import numpy as np
from network import Network_c
from player import Player
from game import Gameboard

ip = socket.gethostbyname(socket.gethostname())
port = 5555

PLAYER_NUM = 3
WIDTH_NUM = 3
HEIGHT_NUM = 3

def main():
    player_turn_num = 0
    player_pos = {}
    for num in range(PLAYER_NUM):
        player_pos[num] = np.zeros((HEIGHT_NUM, WIDTH_NUM), dtype=int)
    run = True
    network = Network_c(ip, port)
    if not network.connect():
        print("fail")
        return False
    network.setblocking(False)
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
            if isinstance(msg, dict):
                player_pos = msg
                print("got player_pos")
            elif isinstance(msg, str):
                if "next player:" in msg:
                    print("got next player")
                    player_turn_num = int(msg.split("next player:")[1])
                if "your number:" in msg:
                    your_number = int(msg.split("your number:")[1])
                    pygame.display.set_caption(f"Player {your_number}")
                if msg == "viewer":
                    pygame.display.set_caption("Viewer")

            elif msg == "":
                print("empty")
            else:
                print(f"msg has wrong type. msg: {msg}, type: {type(msg)}")
        gameboard.update_window(player_pos, player_turn_num)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                network.send("ByeBye")
                network.close()
            if event.type == pygame.VIDEORESIZE:
                gameboard.rescale_window(event.w, event.h, player_pos, player_turn_num)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                pos = player.mouse_pos(mouse_x, mouse_y)
                if writable:
                    network.send(pos)
        pygame.display.update()


if __name__ == "__main__":
    main()
