#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Deals with game calculations.


import numpy as np

class Gamecalc():
    def __init__(self, player_num, width_num, height_num, network):
        self.player_num = int(player_num)
        self.width_num = int(width_num)
        self.height_num = int(height_num)
        self.network = network
        self.create_boards()

    def create_boards(self):
        self.player_pos = {}
        self.substract_board = {}
        for num in range(self.player_num):
            self.player_pos[num] = np.zeros((self.height_num, self.width_num), dtype=int)
            self.substract_board[num] = np.zeros((self.height_num, self.width_num), dtype=int)
        self.chain_board = np.zeros((self.height_num, self.width_num), dtype=int)

    def update_player(self, player, pos_l, num_l):
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
                self.update_chain_board(row, column)
                chain_reaction.append(pos)
        # still missing!!!send boards
        # print("player",self.player_pos)
        # print("chain",self.chain_board)
        # print("sub",self.substract_board)
        if chain_reaction:
            for pos in chain_reaction:
                row, column = pos
                self.player_pos[player][row][column] = 0
            self.clear_substract_board()
            self.clear_chain_board(player)
            return True
        return False

    def update_chain_board(self, row, column):
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

    def clear_substract_board(self):
        for num in range(self.player_num):
            self.player_pos[num] -= self.substract_board[num]
            self.substract_board[num] = np.zeros((self.height_num, self.width_num), dtype=int)

    def clear_chain_board(self, player):
        pos_l = []
        num_l = []
        for num_r, row in enumerate(self.chain_board):
            for num_c, column in enumerate(row):
                if column != 0:
                    pos_l.append((num_r, num_c))
                    num_l.append(column)
        self.chain_board = np.zeros((self.height_num, self.width_num), dtype=int)
        self.update_player(player, pos_l, num_l)

    def check_elimination(self):
        eliminated = []
        for num in range(self.player_num):
            sum_p = np.sum(self.player_pos[num])
            if sum_p == 0:
                eliminated.append(num)
        return eliminated



# g = Gamecalc(3, 3, 3, None)
# g.player_pos[0] = np.array([[1, 0, 0],
#                             [0, 0, 0],
#                             [0, 0, 0]], dtype=int)
# g.player_pos[1] = np.array([[0, 2, 0],
#                             [2, 0, 0],
#                             [0, 0, 0]], dtype=int)
# g.player_pos[2] = np.array([[0, 0, 0],
#                             [0, 2, 0],
#                             [0, 0, 0]], dtype=int)

# pos_l = [(0,0)]
# num_l = [1]
# g.update_player(0, pos_l, num_l)
# print("final pos",g.player_pos)
# print("eliminated",g.check_elimination())

# g = Gamecalc(3, 3, 3, None)
# g.player_pos[1] = np.array([[1, 0, 0],
#                             [0, 0, 0],
#                             [0, 0, 0]], dtype=int)
# g.player_pos[2] = np.array([[0, 2, 0],
#                             [2, 0, 0],
#                             [0, 0, 0]], dtype=int)
# g.player_pos[0] = np.array([[0, 0, 0],
#                             [0, 2, 0],
#                             [0, 0, 0]], dtype=int)

# pos_l = [(0,0)]
# num_l = [1]
# g.update_player(1, pos_l, num_l)
# print("final pos",g.player_pos)
# print("eliminated",g.check_elimination())

# g = Gamecalc(3, 3, 3, None)
# g.player_pos[2] = np.array([[1, 0, 0],
#                             [0, 0, 0],
#                             [0, 0, 0]], dtype=int)
# g.player_pos[0] = np.array([[0, 2, 0],
#                             [2, 0, 0],
#                             [0, 0, 0]], dtype=int)
# g.player_pos[1] = np.array([[0, 0, 0],
#                             [0, 2, 0],
#                             [0, 0, 0]], dtype=int)

# pos_l = [(0,0)]
# num_l = [1]
# g.update_player(2, pos_l, num_l)
# print("final pos",g.player_pos)
# print("eliminated",g.check_elimination())

# g = Gamecalc(3, 3, 3, None)
# g.player_pos[0] = np.array([[0, 0, 0],
#                             [0, 0, 0],
#                             [0, 0, 1]], dtype=int)
# g.player_pos[1] = np.array([[0, 0, 0],
#                             [0, 0, 2],
#                             [0, 2, 0]], dtype=int)
# g.player_pos[2] = np.array([[0, 0, 0],
#                             [0, 2, 0],
#                             [0, 0, 0]], dtype=int)

# pos_l = [(2,2)]
# num_l = [1]
# g.update_player(0, pos_l, num_l)
# print("final pos",g.player_pos)
# print("eliminated",g.check_elimination())
