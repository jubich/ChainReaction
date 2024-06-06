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
        return row, column
