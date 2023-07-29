#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Used for input of player.


import pygame
import numpy as np

import network
import game


class Player():
    def __init__(self, gameboard, network):
        self.gameboard = gameboard
        self.network = network

    def mouse_pos(self, mouse_x, mouse_y):
        for num_r in range(self.gameboard.height_num):
            if mouse_y <= self.gameboard.h_lines[num_r][1]:
                row = num_r
                break
        for num_c in range(self.gameboard.width_num):
            if mouse_x <= self.gameboard.v_lines[num_c][0]:
                column = num_c
                break
        return row, column


if __name__ == "__main__":
    g = game.Gameboard(5, 5, 1)
    g.calc_box_size(g.width_min, g.height_min)
    g.meshing(g.width_min, g.height_min)
    g.draw_mesh((255,255,255))

    player_pos = np.array([[1, 2, 3, 0, 3],
                           [2, 2, 2, 2, 3],
                           [1, 1, 1, 1, 3],
                           [3, 3, 3, 3, 3],
                           [2, 3, 1, 2, 3]])


    p = Player(g, None)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.VIDEORESIZE:
                print("resize")
                g.rescale_window(event.w, event.h, player_pos, (255,255,255))
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                print(p.mouse_pos(mouse_x, mouse_y))
        pygame.display.update()
