#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# needed by player for visiuals (game + menu)

import numpy as np
import pygame

class Gameboard():
    def __init__(self, width_num, height_num, player):
        self.inside = 10        # min size of box inside
        self.line_width = 3     # width of box seperator
        self.board_color = (0, 0, 0)
        self.width_num = int(width_num)
        self.height_num = int(height_num)
        self.width_min = width_num * self.inside + (height_num-1) * self.line_width
        self.height_min = height_num * self.inside + (height_num-1) * self.line_width
        self.player = int(player)
        self.window = self.create_window()

    def create_window(self):
        window = pygame.display.set_mode((self.width_min, self.height_min),
                                         pygame.RESIZABLE)
        pygame.display.set_caption("Client")
        window.fill(self.board_color)
        return window

    def calc_box_size(self, width, height):
        box_width_tot = width - (self.width_num-1) * self.line_width
        box_width = box_width_tot // self.width_num
        box_height_tot = height - (self.height_num-1) * self.line_width
        box_height = box_height_tot // self.height_num

        # update box_size only if bigger than min and then take the smallest
        # of both to make sure it fits on the screen
        box_size = self.inside
        if (box_width > box_size) and (box_width < box_height):
            box_size = box_width
        elif (box_height > box_size) and (box_height < box_width):
            box_size = box_height
        self.box_size = box_size

    def calc_window_size(self):
        board_width = self.width_num * self.box_size + (self.width_num-1) * self.line_width
        board_height = self.height_num * self.box_size + (self.height_num-1) * self.line_width
        return board_width, board_height

    def meshing(self, board_width, board_height):
        # mesh height
        v_lines = []
        for num in range(1, self.width_num + 1):
            x_pos = num * self.box_size + (num-1) * self.line_width
            v_lines.append((x_pos, 0, self.line_width, board_height))
        self.v_lines = v_lines
        h_lines = []
        for num in range(1, self.height_num + 1):
            y_pos = num * self.box_size + (num-1) * self.line_width
            h_lines.append((0, y_pos, board_width, self.line_width))
        self.h_lines = h_lines

    def draw_mesh(self, color):
        lines = self.v_lines + self.h_lines
        for line in lines:
            pygame.draw.rect(self.window, color, line)

    def rescale_window(self, new_width, new_height, player_pos, player_color):
        if new_width >= self.width_min:
            width = new_width
        else:
            width = self.width_min
        if new_height >= self.height_min:
            height = new_height
        else:
            height = self.height_min
        self.calc_box_size(width, height)
        board_width, board_height = self.calc_window_size()
        self.window = pygame.display.set_mode((board_width, board_height),
                                              pygame.RESIZABLE)
        self.window.fill(self.board_color)
        self.meshing(board_width, board_height)
        self.update_window(player_pos, player_color)

    def update_window(self, player_pos, player_color):
        self.draw_mesh(player_color)
        self.draw_circle(player_pos, player_color)

    def draw_circle(self, player_pos,
                    player_color):
        circle_radius = self.box_size // 4

        for num_r, row in enumerate(player_pos):
            for num_c, column, in enumerate(row):
                # pos of bottom right corner of box
                x_pos = self.v_lines[num_c][0]
                y_pos = self.h_lines[num_r][1]
                if column == 0:
                    continue
                # upper left hand corner
                if column >= 1:
                    center = (x_pos - (3*circle_radius), y_pos -
                              (3*circle_radius))
                    pygame.draw.circle(self.window, player_color, center,
                                       circle_radius)
                # upper right hand corner
                if column >= 2:
                    center = (x_pos - (1*circle_radius), y_pos -
                              (3*circle_radius))
                    pygame.draw.circle(self.window, player_color, center,
                                       circle_radius)
                # lower right hand corner
                if column >= 3:
                    center = (x_pos - (1*circle_radius), y_pos -
                              (1*circle_radius))
                    pygame.draw.circle(self.window, player_color, center,
                                       circle_radius)

if __name__ == "__main__":
    # board test
    g = Gameboard(5, 5, 1)
    g.calc_box_size(g.width_min, g.height_min)
    g.meshing(g.width_min, g.height_min)
    g.draw_mesh((255,255,255))

    player_pos = np.array([[1, 2, 3, 0, 3],
                           [2, 2, 2, 2, 3],
                           [1, 1, 1, 1, 3],
                           [3, 3, 3, 3, 3],
                           [2, 3, 1, 2, 3]])
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.VIDEORESIZE:
                g.rescale_window(event.w, event.h, player_pos, (255,255,255))
        pygame.display.update()
