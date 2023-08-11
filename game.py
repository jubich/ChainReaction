#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# needed by player for visiuals (game + menu)


import pygame

class Gameboard():
    def __init__(self, width_num, height_num, player_num):
        self.inside = 60        # min size of box inside
        self.line_width = 3     # width of box seperator
        self.player_num = int(player_num)
        self.board_color = (0, 0, 0)
        self.width_num = int(width_num)
        self.height_num = int(height_num)
        self.width_min = width_num * self.inside + (height_num-1) * self.line_width
        self.height_min = height_num * self.inside + (height_num-1) * self.line_width
        self.window = self._create_window()
        self._first_setup()

    def _create_window(self):
        window = pygame.display.set_mode((self.width_min, self.height_min),
                                         pygame.RESIZABLE)
        pygame.display.set_caption("Client")
        window.fill(self.board_color)
        return window

    def _first_setup(self):
        self.box_size = self.inside
        self._meshing(self.width_min, self.height_min)
        self._draw_mesh(self._get_player_color(0))

    def _calc_box_size(self, width, height):
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

    def _calc_window_size(self):
        board_width = self.width_num * self.box_size + (self.width_num-1) * self.line_width
        board_height = self.height_num * self.box_size + (self.height_num-1) * self.line_width
        return board_width, board_height

    def _meshing(self, board_width, board_height):
        # mesh height
        v_lines = []
        for num in range(1, self.width_num + 1):
            x_pos = num * self.box_size + (num-1) * self.line_width
            v_lines.append((x_pos, 0, self.line_width, board_height))
        self.v_lines = v_lines
        h_lines = []
        # mesh width
        for num in range(1, self.height_num + 1):
            y_pos = num * self.box_size + (num-1) * self.line_width
            h_lines.append((0, y_pos, board_width, self.line_width))
        self.h_lines = h_lines

    def _draw_mesh(self, color):
        lines = self.v_lines + self.h_lines
        for line in lines:
            pygame.draw.rect(self.window, color, line)

    def rescale_window(self, new_width, new_height, player_pos, player_turn_num):
        if new_width >= self.width_min:
            width = new_width
        else:
            width = self.width_min
        if new_height >= self.height_min:
            height = new_height
        else:
            height = self.height_min
        self._calc_box_size(width, height)
        board_width, board_height = self._calc_window_size()
        self.window = pygame.display.set_mode((board_width, board_height),
                                              pygame.RESIZABLE)
        self.window.fill(self.board_color)
        self._meshing(board_width, board_height)
        self.update_window(player_pos, player_turn_num)

    def update_window(self, player_pos, player_turn_num):
        self.window.fill(self.board_color)
        for num in range(self.player_num):
            player_board = player_pos[num]
            player_color = self._get_player_color(num)
            self._draw_circle(player_board, self._get_player_color(num))
        self._draw_mesh(self._get_player_color(player_turn_num))

    def _draw_circle(self, player_pos, player_color):
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

                # lower left hand corner
                if column >= 4:
                    center = (x_pos - (3*circle_radius), y_pos -
                              (1*circle_radius))
                    pygame.draw.circle(self.window, player_color, center,
                                       circle_radius)

    def _get_player_color(self, player_num):
        color_l = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
                   (255, 0, 255), (0, 255, 255)]
        color_len = len(color_l)
        return color_l[player_num % color_len]


if __name__ == "__main__":
    # board test
    import numpy as np
    g = Gameboard(5, 5, 2)
    player_pos = {1:np.array([[0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 3]]),
                  0:np.array([[4, 2, 3, 0, 3],
                              [2, 2, 2, 2, 3],
                              [1, 1, 4, 1, 3],
                              [3, 3, 3, 3, 0],
                              [2, 3, 1, 2, 0]])}

    ii = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.VIDEORESIZE:
                g.rescale_window(event.w, event.h, player_pos, ii)
            if event.type == pygame.MOUSEBUTTONDOWN:
                ii += 1
                g.update_window(player_pos, ii)
        pygame.display.update()
