#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Deals with game calculations.


import time
import numpy as np
import copy


class Gamecalc():
    def __init__(self, player_num, width_num, height_num, reaction_time_step,
                 network, logger, session_uuid):
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

    def _create_boards(self):
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

    def update_player(self, player, pos_l, num_l, connections):
        # pos + num as list
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
            self._clear_chain_board(player, connections)
            alive = self.get_alive()
            if len(alive) == 1:
                self.winner = alive[0]

    def _update_chain_board(self, row, column):
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

    def get_pos(self, row, column, substract, get_player):
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

    def _clear_substract_board(self):
        for num in range(self.player_num):
            self.player_pos[num] -= self.substract_board[num]
            self.substract_board[num] = np.zeros((self.height_num, self.width_num), dtype=int)

    def _clear_chain_board(self, player, connections):
        pos_l = []
        num_l = []
        for num_r, row in enumerate(self.chain_board):
            for num_c, column in enumerate(row):
                if column != 0:
                    pos_l.append((num_r, num_c))
                    num_l.append(column)
        self.chain_board = np.zeros((self.height_num, self.width_num), dtype=int)
        self.update_player(player, pos_l, num_l, connections)

    def _check_elimination(self):
        for num in range(self.player_num):
            sum_p = np.sum(self.player_pos[num])
            if sum_p == 0:
                self.player_alive[num] = False

    def get_eliminated(self):
        self._check_elimination()
        eliminated = []
        for num in range(self.player_num):
            if not self.player_alive[num]:
                eliminated.append(num)
        return eliminated

    def get_alive(self):
        self._check_elimination()
        alive = []
        for num in range(self.player_num):
            if self.player_alive[num]:
                alive.append(num)
        return alive

    def set_eliminated(self, player):
        self.player_alive[player] = False

    def player_to_move(self):
        for num in range(self.player_num):
            # to be safe we can exit the while loop
            if self.player_alive[num]:
                player_move = self._counter % self.player_num
                while not self.player_alive[player_move]:
                    self._counter += 1
                    player_move = self._counter % self.player_num
                return player_move
        return None

    def player_next_to_move(self):
        # that way player next to move is alway the one after player_to_move()
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
        # "aka next round/player"
        self._counter += 1

    def set_state_for_undo(self):
        self.last_player_pos = copy.deepcopy(self.player_pos)
        self.last_player_alive = copy.deepcopy(self.player_alive)
        self._last_counter = copy.deepcopy(self._counter)

    def undo(self, connections, round_num):
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
