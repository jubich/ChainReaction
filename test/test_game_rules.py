#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tests Gamecalc."""

from __future__ import annotations
from typing import Dict

import pytest
import numpy as np

from game_rules import Gamecalc


def compare_positions(goal_pos: Dict[int, np.ndarray],
                      end_pos: Dict[int, np.ndarray]) -> bool:
    """Compares "goal_pos" with "end_pos".

    Args:
        goal_pos: Desired player positions ("player_pos").
        end_pos: Calculated player positions ("player_pos").

    Returns:
        Wether or not both are the same.
    """
    compare_arrays = [np.all(goal_pos[num] == end_pos[num])
                      for num in range(len(goal_pos))]
    return np.all(compare_arrays)



def test_corner_reaction_tl():
    start_pos = {0: np.array([[1, 0, 0],
                              [0, 0, 0],
                              [0, 0, 0]]),
                 1: np.array([[0, 0, 0],
                              [0, 0, 0],
                              [0, 0, 1]])}
    goal_pos = {0: np.array([[0, 1, 0],
                             [1, 0, 0],
                             [0, 0, 0]]),
                1: np.array([[0, 0, 0],
                             [0, 0, 0],
                             [0, 0, 1]])}
    g_calc = Gamecalc(2, 3, 3, 0, None, None, None)
    g_calc.player_pos = start_pos
    g_calc.update_player(0, [(0, 0)], [1], None, 0)
    assert compare_positions(goal_pos, g_calc.player_pos)


def test_corner_reaction_tr():
    start_pos = {0: np.array([[0, 0, 1],
                              [0, 0, 0],
                              [0, 0, 0]]),
                 1: np.array([[0, 0, 0],
                              [0, 0, 0],
                              [1, 0, 0]])}
    goal_pos = {0: np.array([[0, 1, 0],
                             [0, 0, 1],
                             [0, 0, 0]]),
                1: np.array([[0, 0, 0],
                             [0, 0, 0],
                             [1, 0, 0]])}
    g_calc = Gamecalc(2, 3, 3, 0, None, None, None)
    g_calc.player_pos = start_pos
    g_calc.update_player(0, [(0, 2)], [1], None, 0)
    assert compare_positions(goal_pos, g_calc.player_pos)


def test_corner_reaction_bl():
    start_pos = {0: np.array([[0, 0, 0],
                              [0, 0, 0],
                              [1, 0, 0]]),
                 1: np.array([[0, 0, 1],
                              [0, 0, 0],
                              [0, 0, 0]])}
    goal_pos = {0: np.array([[0, 0, 0],
                             [1, 0, 0],
                             [0, 1, 0]]),
                1: np.array([[0, 0, 1],
                             [0, 0, 0],
                             [0, 0, 0]])}
    g_calc = Gamecalc(2, 3, 3, 0, None, None, None)
    g_calc.player_pos = start_pos
    g_calc.update_player(0, [(2, 0)], [1], None, 0)
    assert compare_positions(goal_pos, g_calc.player_pos)


def test_corner_reaction_br():
    start_pos = {0: np.array([[0, 0, 0],
                              [0, 0, 0],
                              [0, 0, 1]]),
                 1: np.array([[1, 0, 0],
                              [0, 0, 0],
                              [0, 0, 0]])}
    goal_pos = {0: np.array([[0, 0, 0],
                             [0, 0, 1],
                             [0, 1, 0]]),
                1: np.array([[1, 0, 0],
                             [0, 0, 0],
                             [0, 0, 0]])}
    g_calc = Gamecalc(2, 3, 3, 0, None, None, None)
    g_calc.player_pos = start_pos
    g_calc.update_player(0, [(2, 2)], [1], None, 0)
    assert compare_positions(goal_pos, g_calc.player_pos)


def test_edge_reaction_tc():
    start_pos = {0: np.array([[0, 2, 0],
                              [0, 0, 0],
                              [0, 0, 0]]),
                 1: np.array([[0, 0, 0],
                              [0, 0, 0],
                              [0, 1, 0]])}
    goal_pos = {0: np.array([[1, 0, 1],
                             [0, 1, 0],
                             [0, 0, 0]]),
                1: np.array([[0, 0, 0],
                             [0, 0, 0],
                             [0, 1, 0]])}
    g_calc = Gamecalc(2, 3, 3, 0, None, None, None)
    g_calc.player_pos = start_pos
    g_calc.update_player(0, [(0, 1)], [1], None, 0)
    assert compare_positions(goal_pos, g_calc.player_pos)


def test_edge_reaction_rc():
    start_pos = {0: np.array([[0, 0, 0],
                              [0, 0, 2],
                              [0, 0, 0]]),
                 1: np.array([[0, 0, 0],
                              [1, 0, 0],
                              [0, 0, 0]])}
    goal_pos = {0: np.array([[0, 0, 1],
                             [0, 1, 0],
                             [0, 0, 1]]),
                1: np.array([[0, 0, 0],
                             [1, 0, 0],
                             [0, 0, 0]])}
    g_calc = Gamecalc(2, 3, 3, 0, None, None, None)
    g_calc.player_pos = start_pos
    g_calc.update_player(0, [(1, 2)], [1], None, 0)
    assert compare_positions(goal_pos, g_calc.player_pos)


def test_edge_reaction_bc():
    start_pos = {0: np.array([[0, 0, 0],
                              [0, 0, 0],
                              [0, 2, 0]]),
                 1: np.array([[0, 1, 0],
                              [0, 0, 0],
                              [0, 0, 0]])}
    goal_pos = {0: np.array([[0, 0, 0],
                             [0, 1, 0],
                             [1, 0, 1]]),
                1: np.array([[0, 1, 0],
                             [0, 0, 0],
                             [0, 0, 0]])}
    g_calc = Gamecalc(2, 3, 3, 0, None, None, None)
    g_calc.player_pos = start_pos
    g_calc.update_player(0, [(2, 1)], [1], None, 0)
    assert compare_positions(goal_pos, g_calc.player_pos)


def test_edge_reaction_lc():
    start_pos = {0: np.array([[0, 0, 0],
                              [2, 0, 0],
                              [0, 0, 0]]),
                 1: np.array([[0, 0, 0],
                              [0, 0, 1],
                              [0, 0, 0]])}
    goal_pos = {0: np.array([[1, 0, 0],
                             [0, 1, 0],
                             [1, 0, 0]]),
                1: np.array([[0, 0, 0],
                             [0, 0, 1],
                             [0, 0, 0]])}
    g_calc = Gamecalc(2, 3, 3, 0, None, None, None)
    g_calc.player_pos = start_pos
    g_calc.update_player(0, [(1, 0)], [1], None, 0)
    assert compare_positions(goal_pos, g_calc.player_pos)


def test_center_reaction_cc():
    start_pos = {0: np.array([[0, 0, 0],
                             [0, 3, 0],
                             [0, 0, 0]]),
                 1: np.array([[0, 0, 1],
                             [0, 0, 0],
                             [0, 0, 0]])}
    goal_pos = {0: np.array([[0, 1, 0],
                             [1, 0, 1],
                             [0, 1, 0]]),
                1: np.array([[0, 0, 1],
                             [0, 0, 0],
                             [0, 0, 0]])}
    g_calc = Gamecalc(2, 3, 3, 0, None, None, None)
    g_calc.player_pos = start_pos
    g_calc.update_player(0, [(1, 1)], [1], None, 0)
    assert compare_positions(goal_pos, g_calc.player_pos)


def test_capture_with_overloading_tl():
    start_pos = {0: np.array([[0, 2, 0, 0, 0],
                              [2, 3, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 1]]),
                 1: np.array([[1, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0]])}
    goal_pos = {0: np.array([[0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 1]]),
                1: np.array([[0, 2, 1, 0, 0],
                             [2, 1, 1, 0, 0],
                             [1, 1, 0, 0, 0],
                             [0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0]])}
    g_calc = Gamecalc(2, 5, 5, 0, None, None, None)
    g_calc.player_pos = start_pos
    g_calc.update_player(1, [(0, 0)], [1], None, 0)
    assert compare_positions(goal_pos, g_calc.player_pos)


def test_capture_with_overloading_tr():
    start_pos = {0: np.array([[0, 0, 0, 2, 0],
                              [0, 0, 0, 3, 2],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [1, 0, 0, 0, 0]]),
                 1: np.array([[0, 0, 0, 0, 1],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0]])}
    goal_pos = {0: np.array([[0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0],
                             [1, 0, 0, 0, 0]]),
                1: np.array([[0, 0, 1, 2, 0],
                             [0, 0, 1, 1, 2],
                             [0, 0, 0, 1, 1],
                             [0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0]])}
    g_calc = Gamecalc(2, 5, 5, 0, None, None, None)
    g_calc.player_pos = start_pos
    g_calc.update_player(1, [(0, 4)], [1], None, 0)
    assert compare_positions(goal_pos, g_calc.player_pos)


def test_capture_with_overloading_br():
    start_pos = {0: np.array([[1, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 3, 2],
                              [0, 0, 0, 2, 0]]),
                 1: np.array([[0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 1]])}
    goal_pos = {0: np.array([[1, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0]]),
                1: np.array([[0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0],
                             [0, 0, 0, 1, 1],
                             [0, 0, 1, 1, 2],
                             [0, 0, 1, 2, 0]])}
    g_calc = Gamecalc(2, 5, 5, 0, None, None, None)
    g_calc.player_pos = start_pos
    g_calc.update_player(1, [(4, 4)], [1], None, 0)
    assert compare_positions(goal_pos, g_calc.player_pos)


def test_capture_with_overloading_bl():
    start_pos = {0: np.array([[0, 0, 0, 0, 1],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [2, 3, 0, 0, 0],
                              [0, 2, 0, 0, 0]]),
                 1: np.array([[0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0],
                              [1, 0, 0, 0, 0]])}
    goal_pos = {0: np.array([[0, 0, 0, 0, 1],
                             [0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0]]),
                1: np.array([[0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0],
                             [1, 1, 0, 0, 0],
                             [2, 1, 1, 0, 0],
                             [0, 2, 1, 0, 0]])}
    g_calc = Gamecalc(2, 5, 5, 0, None, None, None)
    g_calc.player_pos = start_pos
    g_calc.update_player(1, [(4, 0)], [1], None, 0)
    assert compare_positions(goal_pos, g_calc.player_pos)
