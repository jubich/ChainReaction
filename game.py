#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# needed by player for visiuals (game + menu)


import numpy as np
import pygame

class Gameboard():
    def __init__(self, min_box_size, line_width, player_num, board_color,
                 width_num, height_num, player_colors):
        self.inside = int(min_box_size)        # min size of box inside
        self.line_width = int(line_width)      # width of box seperator
        self.player_num = int(player_num)
        self.board_color = board_color
        self.width_num = int(width_num)
        self.height_num = int(height_num)
        self.player_colors = player_colors
        self._calc_min_inside()
        self.width_min_grid = width_num * self.inside + width_num * self.line_width
        self.height_min_grid = height_num * self.inside + (height_num-1) * self.line_width
        self.curr_grid_height = self.height_min_grid
        self.curr_grid_width = self.width_min_grid
        self.info_column_width = 180
        self.bar_width = 300
        self.end_column_width = 10
        self.window = self._create_window()
        self._first_setup()

    def _calc_min_inside(self):
        absolute_min_window_height = 262
        box_height_tot = absolute_min_window_height - (self.height_num-1) * self.line_width
        box_height = box_height_tot // self.height_num
        if self.inside < box_height:
            self.inside = box_height

    def _create_window(self):
        window = pygame.display.set_mode((self.width_min_grid +
                                          self.info_column_width +
                                          self.bar_width +
                                          self.end_column_width,
                                          self.height_min_grid),
                                         pygame.RESIZABLE)
        pygame.display.set_caption("Client")
        window.fill(self.board_color)
        return window

    def _first_setup(self):
        self.box_size = self.inside
        self._meshing(self.width_min_grid, self.height_min_grid)
        self._draw_mesh(self._get_player_color(0))

    def _calc_box_size(self, width, height):
        box_width_tot = width - self.width_num * self.line_width
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
        board_width = self.width_num * self.box_size + self.width_num * self.line_width
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

    def rescale_window(self, new_width, new_height, player_pos, player_turn_num,
                       nicknames, curr_round):
        if (new_width - self.info_column_width - self.bar_width - self.end_column_width) >= self.width_min_grid:
            width = new_width - self.info_column_width - self.bar_width - self.end_column_width
        else:
            width = self.width_min_grid
        if new_height >= self.height_min_grid:
            height = new_height
        else:
            height = self.height_min_grid
        self._calc_box_size(width, height)
        board_width, board_height = self._calc_window_size()
        self.curr_grid_height = board_height
        self.curr_grid_width = board_width
        self.window = pygame.display.set_mode((self.curr_grid_width
                                               + self.info_column_width
                                               + self.bar_width
                                               + self.end_column_width,
                                               self.curr_grid_height),
                                              pygame.RESIZABLE)
        self.window.fill(self.board_color)
        self._meshing(board_width, board_height)
        self.update_window(player_pos, player_turn_num, nicknames, curr_round)

    def update_window(self, player_pos, player_turn_num, nicknames, curr_round):
        self.window.fill(self.board_color)
        for num in range(self.player_num):
            player_board = player_pos[num]
            self._draw_circle(player_board, self._get_player_color(num))
        self._draw_mesh(self._get_player_color(player_turn_num))
        self._write_infos(player_pos, nicknames, curr_round,
                          nicknames[player_turn_num])
        self._draw_bar(player_pos, nicknames)

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
        color_len = len(self.player_colors)
        if player_num is None:
            return (0, 0, 0)
        return self.player_colors[player_num % color_len]

    def _draw_bar(self, player_pos, nicknames):
        total_count = 0
        for value in player_pos.values():
            total_count += np.sum(value)

        if total_count != 0:
            height_per_sphere = self.curr_grid_height / total_count
        else:
            height_per_sphere = 0

        last_height = 0
        for key, item in player_pos.items():
            count = np.sum(item)
            color = self._get_player_color(key)
            # left, top, width, height
            curr_height = round(height_per_sphere * count)
            rect = (self.curr_grid_width + self.info_column_width, last_height, self.bar_width, curr_height)
            font_size = self.get_value_in_range(6, 18, round(curr_height))
            font = pygame.font.SysFont('Arial', font_size)
            text_surface = font.render(f'{count} : {nicknames[key]}', False, (255, 255, 255))
            pygame.draw.rect(self.window, color, rect)
            self.window.blit(text_surface, (round(self.curr_grid_width
                                                  + self.info_column_width
                                                  + self.bar_width/2
                                                  - text_surface.get_width()/2),
                                            round(last_height + curr_height/2
                                                  - text_surface.get_height()/2)))
            last_height += curr_height

    def _write_infos(self, player_pos, nicknames, curr_round, next_pl):
        text_indent = 10
        font = pygame.font.SysFont('Arial', 24)
        h_pos = 10
        text_surface = font.render('Total:', False, (255, 255, 255))
        self.window.blit(text_surface, (self.curr_grid_width + text_indent, h_pos))
        total_count = 0
        for value in player_pos.values():
            total_count += np.sum(value)
        h_pos += 34
        text_surface = font.render(f'{total_count}', False, (255, 255, 255))
        self.window.blit(text_surface, (self.curr_grid_width + text_indent, h_pos))
        h_pos += 34
        text_surface = font.render('Round:', False, (255, 255, 255))
        self.window.blit(text_surface, (self.curr_grid_width + text_indent, h_pos))
        h_pos += 34
        text_surface = font.render(f'{curr_round}', False, (255, 255, 255))
        self.window.blit(text_surface, (self.curr_grid_width + text_indent, h_pos))
        h_pos += 34
        text_surface = font.render('Next:', False, (255, 255, 255))
        self.window.blit(text_surface, (self.curr_grid_width + text_indent, h_pos))
        h_pos += 34
        for size in range(24, 11, -1):
            pl_font = pygame.font.SysFont('Arial', size)
            text_surface = pl_font.render(f'{next_pl}', False, (255, 255, 255))
            if text_surface.get_width() <= self.info_column_width - text_indent - 5:
                break
        self.window.blit(text_surface, (self.curr_grid_width + text_indent,
                                        h_pos))
        h_pos += 34
        self._button_rect = (self.curr_grid_width + text_indent, h_pos, 80, 34)
        pygame.draw.rect(self.window, (255, 0, 0), self._button_rect)
        text_surface = font.render("Undo!", False, (255, 255, 255))
        h_pos += 5
        self.window.blit(text_surface, (self.curr_grid_width + 80 / 2
                                        + text_indent
                                        - text_surface.get_width()/2, h_pos))

    def mouse_pos(self, mouse_x, mouse_y):
        column = None
        row = None
        for num_r in range(self.height_num):
            if mouse_y <= self.h_lines[num_r][1]:
                row = num_r
                break
        for num_c in range(self.width_num):
            if mouse_x <= self.v_lines[num_c][0]:
                column = num_c
                break
        if (column and row) is not None:
            return ("position", (row, column))
        button_w_min = self._button_rect[0]
        button_w_max = self._button_rect[0] + self._button_rect[2]
        button_h_min = self._button_rect[1]
        button_h_max = self._button_rect[1] + self._button_rect[3]
        if (mouse_x >= button_w_min) and (mouse_x <= button_w_max):
            if (mouse_y >= button_h_min) and (mouse_y <= button_h_max):
                return ("undo", None)
        return None

    @staticmethod
    def get_value_in_range(min_v, max_v, value):
        if value < min_v:
            return min_v
        if value > max_v:
            return max_v
        return value
