#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Contains the "Gamecalc" class for the server module to do the game calculations."""


from __future__ import annotations
from typing import List, Tuple
import time
import copy
import logging
import socket

import numpy as np

from chainreaction.network import Network_s


class Gamecalc():
    """Calculates the game."""
    def __init__(self, player_num: int, width_num: int, height_num: int, reaction_time_step: float,
                 network: Network_s, logger: logging.Logger | None, session_uuid: str) -> None:
        """Initializes the instance.

        Args:
            player_num: Number of players.
            width_num: Number of boxes in x-direction.
            height_num: Number of boxes in y-direction.
            reaction_time_step: Time in s between each reaction step.
            network: Main class for dealing with sending and recieving of data via sockets.
            logger: Logs the progress and state of the game/function or None for testing.
            session_uuid: Differentiates different games sessions in log-files.
        """
        self.player_num = int(player_num)
        self.width_num = int(width_num)
        self.height_num = int(height_num)
        self.reaction_time_step = reaction_time_step
        self.network = network
        self.logger = logger
        self.session_uuid = session_uuid
        self._counter = 0
        self._create_boards()
        self.winner = None
        self.time_line = {}

    def _create_boards(self) -> None:
        """Initializes the boards/arrays and variables needed for the game calculations."""
        self.player_pos = {}
        self.substract_board = {}
        self.player_alive = {}
        for num in range(self.player_num):
            self.player_pos[num] = np.zeros((self.height_num, self.width_num), dtype=int)
            self.substract_board[num] = np.zeros((self.height_num, self.width_num), dtype=int)
            self.player_alive[num] = True
        self.chain_board = np.zeros((self.height_num, self.width_num), dtype=int)
        self.last_player_pos = self.player_pos
        self.last_player_alive = self.player_alive
        self._last_counter = self._counter

    def update_player(self, player: int, pos_l: List[Tuple[int, int]],
                      num_l: List[int], connections: List[socket.socket] | None,
                      round_num: int) -> None:
        """Updates player positions and distributes those to the clients.

        Args:
            player: "Player_number" of current player.
            pos_l: Positions to be updated with corresponding number of circles.
            num_l: Number of circles to be added to corresponding position.
            connections: Sockets of connected clients or None for testing.
            round_num: Current round number.
        """
        chain_reaction = []
        for pos, num in zip(pos_l, num_l):
            row, column = pos
            self.player_pos[player][row][column] += num
            max_num = 4
            if (row == 0) or (row == self.height_num-1):
                max_num -= 1
            if (column == 0) or (column == self.width_num-1):
                max_num -= 1
            if self.player_pos[player][row][column] >= max_num:
                self._update_chain_board(row, column)
                chain_reaction.append((pos, max_num))

        if self.time_line.get(round_num, None) is None:
            self.time_line[round_num] = []
        reaction_list = []
        for num in range(self.player_num):
            reaction_list.append(np.sum(self.player_pos[num]))
        self.time_line[round_num].append(reaction_list)

        if connections is not None:
            for connection in connections:
                self.network.send(connection, ("positions", self.player_pos))
            self.logger.debug("Send positions",
                              extra={"session_uuid": self.session_uuid,
                                     "positions": self.player_pos})
        if chain_reaction:
            if len(self.get_alive()) == 1:
                if self.logger is not None:
                    self.logger.debug("Chain reaction stopped!",
                                      extra={"session_uuid": self.session_uuid})
                return
            time.sleep(self.reaction_time_step)
            for item in chain_reaction:
                pos, max_num = item
                row, column = pos
                self.player_pos[player][row][column] -= max_num
            self._clear_substract_board()
            self._clear_chain_board(player, connections, round_num)
            alive = self.get_alive()
            if len(alive) == 1:
                self.winner = alive[0]

    def _update_chain_board(self, row: int, column: int) -> None:
        """Updates the "chain_board".

        The "chain_board" is used to transfer the captured and "exploded" circles
        to their new postion and "owner".

        Args:
            row: Row at which the "explosion" takes place.
            column: Column at which the "explosion" takes place.
        """
        try:
            self.chain_board[row+1][column] += 1 + self.get_pos(row+1, column, True, False)
        except IndexError:
            pass
        row_neg = row-1
        if row_neg >= 0:
            self.chain_board[row_neg][column] += 1 + self.get_pos(row_neg, column, True, False)

        try:
            self.chain_board[row][column+1] += 1 + self.get_pos(row, column+1, True, False)
        except IndexError:
            pass
        column_neg = column-1
        if column_neg >= 0:
            self.chain_board[row][column_neg] += 1 + self.get_pos(row, column_neg, True, False)

    def get_pos(self, row: int, column:int, substract: bool, get_player: bool) -> int | Tuple[int, int]:
        """Return the number of circles (and "player_number") of a position.

        !!Warning: "substract" and "get_player" can not be used combined!!

        Args:
            row: Row at which the information is requested.
            column: Column at which the information is requested.
            substract: Wether the "substact_board" should be updated or not. Can not be used with
              "get_player"!
            get_player: Wether the "player_number" of the requested position should be returned.
              Can not be used with "substract"!

        Returns:
            By default ("substract" and "get_player" are "False") only the number of
            circles at the requested position is returned.

            If "substract" is "True" then "get_player" must be "False" and the
            "substract_board" will be updated. If the value in the "substract_board"
            is not "0" then "0" is returned, because the value at this position was
            already returned (would duplicated this circles otherwise, the
            "substract_board" is used for a better animation).

            If "get_player" it "True" then "substract" must be "False" and additionaly
            the "player_number" who ownes that circles is returned.
        """
        for num in range(self.player_num):
            pos_val = self.player_pos[num][row][column]
            if pos_val != 0:
                if substract:
                    if self.substract_board[num][row][column] != 0:
                        return 0
                    self.substract_board[num][row][column] = pos_val
                break
        if get_player:
            return pos_val, num
        return pos_val

    def _clear_substract_board(self) -> None:
        """Clears the "substract_board".

        The "substract_board" is used to clear the circles at captured positions
        for all palyers at the same time. It makes the animation look better.
        """
        for num in range(self.player_num):
            self.player_pos[num] -= self.substract_board[num]
            self.substract_board[num] = np.zeros((self.height_num, self.width_num), dtype=int)

    def _clear_chain_board(self, player: int, connections: List[socket.socket] | None,
                           round_num: int) -> None:
        """Clears the "chain_board".

        The "chain_board" is used to transfer the captured and "exploded" circles
        to their new postion and "owner".

        Args:
            player: "Player_number" of current player.
            connections: Sockets of connected clients or None for testing.
            round_num: Current round number.
        """
        pos_l = []
        num_l = []
        for num_r, row in enumerate(self.chain_board):
            for num_c, column in enumerate(row):
                if column != 0:
                    pos_l.append((num_r, num_c))
                    num_l.append(column)
        self.chain_board = np.zeros((self.height_num, self.width_num), dtype=int)
        self.update_player(player, pos_l, num_l, connections, round_num)

    def _check_elimination(self) -> None:
        """Checks for elimination and sets "self.player_alive".

        !! Should only be used after all player had at least one turn otherwise
        player will get falsely eliminated due to their "play_pos" sum beeing "0"!!
        """
        for num in range(self.player_num):
            sum_p = np.sum(self.player_pos[num])
            if sum_p == 0:
                self.player_alive[num] = False

    def get_eliminated(self) -> List[int]:
        """Returns a list with "player_numbers" of eliminated players.

        !! Should only be used after all player had at least one turn due to use
        of "self._check_elimination"!!
        """
        self._check_elimination()
        eliminated = []
        for num in range(self.player_num):
            if not self.player_alive[num]:
                eliminated.append(num)
        return eliminated

    def get_alive(self) -> List[int]:
        """Returns a list with "player_numbers" of alive players.

        !! Should only be used after all player had at least one turn due to use
        of "self._check_elimination"!!
        """
        self._check_elimination()
        alive = []
        for num in range(self.player_num):
            if self.player_alive[num]:
                alive.append(num)
        return alive

    def set_eliminated(self, player) -> None:
        """Sets a player as eliminated.

        Args:
            player: "Player_number" of player to be eliminated.
        """
        self.player_alive[player] = False

    def player_to_move(self) -> int | None:
        """Returns the "player_number" of the current player.

        Returns:
            "None" should in theory never be returned.
        """
        for num in range(self.player_num):
            # to be safe we can exit the while loop
            if self.player_alive[num]:
                player_move = self._counter % self.player_num
                while not self.player_alive[player_move]:
                    self._counter += 1
                    player_move = self._counter % self.player_num
                return player_move
        return None

    def player_next_to_move(self) -> int | None:
        """Returns the "player_number" of the next player after the current one.

        Returns:
            "None" should in theory never be returned.
        """
        # that way player next to move is always the one after player_to_move()
        _ = self.player_to_move()
        for num in range(self.player_num):
            # to be safe we can exit the while loop
            if self.player_alive[num]:
                offset = 1
                player_move = (self._counter + offset) % self.player_num
                while not self.player_alive[player_move]:
                    offset += 1
                    player_move = (self._counter + offset) % self.player_num
                return player_move
        return None

    def increase_counter(self):
        """Increases the "counter" which is used for determining the current and
        next "player_number"."""
        # "aka next round/player"
        self._counter += 1

    def set_state_for_undo(self) -> None:
        """Saves the current game state to be loaded when "undo" was pressed."""
        self.last_player_pos = copy.deepcopy(self.player_pos)
        self.last_player_alive = copy.deepcopy(self.player_alive)
        self._last_counter = copy.deepcopy(self._counter)

    def undo(self, connections: List[socket.socket], round_num: int) -> None:
        """Loades and distributes the saved game state thereby undoing the last move.

        Args:
            connections: Sockets of connected clients.
            round_num: Current round number.
        """
        self.time_line.pop(round_num)
        self.player_pos = copy.deepcopy(self.last_player_pos)
        self.player_alive = copy.deepcopy(self.last_player_alive)
        self._counter = copy.deepcopy(self._last_counter)
        next_player = self.player_to_move()
        if connections is not None:
            for connection in connections:
                self.network.send(connection, ("positions", self.player_pos))
                self.network.send(connection, ("next player", (next_player, round_num)))
        self.logger.debug("Undo position",
                          extra={"session_uuid": self.session_uuid,
                                 "round_num": round_num,
                                 "next_player": next_player,
                                 "positions": self.player_pos,
                                 "counter": self._counter})
