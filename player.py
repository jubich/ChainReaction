#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Used for input of player.


import pygame
import numpy as np

import network
import game


class Player():
    def __init__(self, gameboard):
        self.gameboard = gameboard

    def mouse_pos(self, mouse_x, mouse_y):
        column = None
        row = None
        for num_r in range(self.gameboard.height_num):
            if mouse_y <= self.gameboard.h_lines[num_r][1]:
                row = num_r
                break
        for num_c in range(self.gameboard.width_num):
            if mouse_x <= self.gameboard.v_lines[num_c][0]:
                column = num_c
                break
        if (column and row) is not None:
            return ("position", (row, column))
        button_w_min = self.gameboard._button_rect[0]
        button_w_max = self.gameboard._button_rect[0] + self.gameboard._button_rect[2]
        button_h_min = self.gameboard._button_rect[1]
        button_h_max = self.gameboard._button_rect[1] + self.gameboard._button_rect[3]
        if (mouse_x >= button_w_min) and (mouse_x <= button_w_max):
            if (mouse_y >= button_h_min) and (mouse_y <= button_h_max):
                return ("undo", None)
        return None
