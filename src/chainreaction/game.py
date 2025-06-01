#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Contains the "Gameboard" class for the client module to visualize the gameboard."""


from __future__ import annotations
from typing import List, Tuple, Dict

import numpy as np
import pygame


class Gameboard():
    """Visualizes gameboard."""
    def __init__(self, min_box_size: int, line_width: int, player_num: int,
                 board_color: Tuple[int, int, int], width_num: int,
                 height_num: int, player_colors: List[Tuple[int, int, int]]) -> None:
        """Initializes the instance.

        Args:
            min_box_size: Minimum size of bix in pixel.
            line_width: Thickness of the line around the box in pixel.
            player_num: Number of players.
            board_color: Background color of the gameboard.
            width_num: Number of boxes in x-direction.
            height_num: Number of boxes in y-direction.
            player_colors: Colors for the players.
        """
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

    def _calc_min_inside(self) -> None:
        """Calculates the minimum size of the box in pixel.

        Prevents the window to be to small to fit all informations.
        """
        absolute_min_window_height = 262
        box_height_tot = absolute_min_window_height - (self.height_num-1) * self.line_width
        box_height = box_height_tot // self.height_num
        if self.inside < box_height:
            self.inside = box_height

    def _create_window(self) -> pygame.surface.Surface:
        """Creates the pygame window.

        Returns:
            window: Pygame window for gameboard.
        """
        window = pygame.display.set_mode((self.width_min_grid +
                                          self.info_column_width +
                                          self.bar_width +
                                          self.end_column_width,
                                          self.height_min_grid),
                                         pygame.RESIZABLE)
        pygame.display.set_caption("Client")
        window.fill(self.board_color)
        return window

    def _first_setup(self) -> None:
        """Creates the initial game grid on the window."""
        self.box_size = self.inside
        self._meshing(self.width_min_grid, self.height_min_grid)
        self._draw_mesh(self._get_player_color(0))

    def _calc_box_size(self, width: int, height: int) -> None:
        """Calculates new "self.box_size" when resizing.

        Args:
            width: New width in pixel.
            height: New height in pixel.
        """
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

    def _calc_board_size(self) -> Tuple[int, int]:
        """Calculates the new board size.

        Returns:
            board_width: New board width in pixel.
            board_height: New board height in pixel.
        """
        board_width = self.width_num * self.box_size + self.width_num * self.line_width
        board_height = self.height_num * self.box_size + (self.height_num-1) * self.line_width
        return board_width, board_height

    def _meshing(self, board_width: int, board_height: int) -> None:
        """Creates new grid lines for board.

        Args:
            board_width: Board width in pixel.
            board_height: Board height in pixel.
        """
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

    def _draw_mesh(self, color: Tuple[int, int, int]) -> None:
        """Drawes the grid onto the window.

        Args:
            color: Color of the current player for the grid lines.
        """
        lines = self.v_lines + self.h_lines
        for line in lines:
            pygame.draw.rect(self.window, color, line)

    def rescale_window(self, new_width: int, new_height: int,
                       player_pos: Dict[int, np.ndarray], player_turn_num: int,
                       nicknames: Dict[int, str], round_num: int) -> None:
        """Rescales the window.

        Args:
            new_width: New board width in pixel.
            new_height: New board height in pixel.
            player_pos: Contains the number and locations of circles corresponding
              to the "player_numbers".
            player_turn_num: "Player_number" of current player.
            nicknames: Connects "player_number" to the respective player nicknames.
            round_num: Number of the current round.
        """
        if (new_width - self.info_column_width - self.bar_width - self.end_column_width) >= self.width_min_grid:
            width = new_width - self.info_column_width - self.bar_width - self.end_column_width
        else:
            width = self.width_min_grid
        if new_height >= self.height_min_grid:
            height = new_height
        else:
            height = self.height_min_grid
        self._calc_box_size(width, height)
        board_width, board_height = self._calc_board_size()
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
        self.update_window(player_pos, player_turn_num, nicknames, round_num)

    def update_window(self, player_pos: Dict[int, np.ndarray], player_turn_num: int,
                      nicknames: Dict[int, str], round_num: int) -> None:
        """Updates the window.

        Args:
            player_pos: Contains the number and locations of circles corresponding
              to the "player_numbers".
            player_turn_num: "Player_number" of current player.
            nicknames: Connects "player_number" to the respective player nicknames.
            round_num: Number of the current round.
        """
        self.window.fill(self.board_color)
        for num in range(self.player_num):
            player_board = player_pos[num]
            self._draw_circle(player_board, self._get_player_color(num))
        self._draw_mesh(self._get_player_color(player_turn_num))
        self._write_infos(player_pos, nicknames, round_num,
                          nicknames[player_turn_num])
        self._draw_bar(player_pos, nicknames)

    def _draw_circle(self, player_pos: Dict[int, np.ndarray],
                     player_color: Tuple[int, int, int]) -> None:
        """Draw cirles on gameboard.

        Args:
            player_pos: Contains the number and locations of circles corresponding
              to the "player_numbers".
            player_color: Color of the circles of the player currently drawn to the window.
        """
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

    def _get_player_color(self, player_num: int) -> Tuple[int, int, int]:
        """Returns the color of the player requested.

        Args:
            player_num: "Player_number" of the player who's color is requested.

        Returns:
            Color of the "player_number" requested.
        """
        color_len = len(self.player_colors)
        if player_num is None:
            return (0, 0, 0)
        return self.player_colors[player_num % color_len]

    def _draw_bar(self, player_pos: Dict[int, np.ndarray],
                  nicknames: Dict[int, str]) -> None:
        """Draws the current ratio of player circles as bar diagramm.

        Args:
            player_pos: Contains the number and locations of circles corresponding
              to the "player_numbers".
            nicknames: Connects "player_number" to the respective player nicknames.
        """
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

    def _write_infos(self, player_pos: Dict[int, np.ndarray],
                     nicknames: Dict[int, str], round_num: int,
                     next_pl: str) -> None:
        """Draws infos and undo-button to window.

        Args:
            player_pos: Contains the number and locations of circles corresponding
              to the "player_numbers".
            nicknames: Connects "player_number" to the respective player nicknames.
            round_num: Current round number.
            next_pl (str): Name of the player to take turn.
        """
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
        text_surface = font.render(f'{round_num}', False, (255, 255, 255))
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

    def mouse_pos(self, mouse_x: int, mouse_y: int) -> Tuple[str, Tuple[int, int] | None] | None:
        """Convertes mouse input into command send to server.

        Args:
            mouse_x: Mouse position in pixel (x-direction).
            mouse_y: Mouse position in pixel (y-direction).

        Return:
            Retruns None if the mouse input is not valid/"usefull". If mouse click
            was on undo-button than "("undo",None)" will be returned. Otherwise
            "("position", (row, column))" will be returned with row and column
            corresponding to the box position of the clicked box.
        """
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
    def get_value_in_range(min_v: float, max_v: float, value: float) -> float:
        """Returns a value between "min_v" and "max_v" including.

        Args:
            min_v: Smallest value returned.
            max_v: Biggest value returned.
            value: Value to be checked for beeing in range.

        Returns:
            Value between "min_v" and "max_v" including.
        """
        if value < min_v:
            return min_v
        if value > max_v:
            return max_v
        return value
