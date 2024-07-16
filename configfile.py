#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import os
import socket
import ast

import pygame


DEFAULTS = {"info": "Changes in '[DEFAULT]' will be ignored. Changes should be done in '[CLIENT]' and/or '[SERVER]'.",
            "client.fps_limit": "60",
            "client.box_min_size": "60",
            "client.box_line_width": "3",
            "client.board_color": "(0,0,0)",
            "client.player_colors": str([(255, 0, 0), (0, 255, 0), (0, 0, 255),
                                         (255, 0, 255), (0, 255, 255), (102, 102, 0),
                                         (255, 178, 102), (51, 102, 0), (204, 0, 102)]),
            "client.nickname": "'None' -> 'user input'",
            "client.ip": "'None' -> 'user input'",
            "client.port": "5555",
            "client.be_player": "True",
            "server.reaction_time_step": "0.5",
            "server.player_number": "'None' -> 'user input'",
            "server.gameboard_height": "'None' -> 'user input'",
            "server.gameboard_width": "'None' -> 'user input'",
            "server.ip": "'None' -> 'socket.gethostbyname(socket.gethostname())'",
            "server.port": "5555"}

CLIENT = {"fps_limit": "60",
          "box_min_size": "60",
          "box_line_width": "3",
          "board_color": "(0,0,0)",
          "player_colors": str([(255, 0, 0), (0, 255, 0), (0, 0, 255),
                                (255, 0, 255), (0, 255, 255), (102, 102, 0),
                                (255, 178, 102), (51, 102, 0), (204, 0, 102)]),
          "nickname": "None",
          "ip": "None",
          "port": "5555",
          "be_player": "True"}

SERVER = {"reaction_time_step": "0.5",
          "player_number": "None",
          "gameboard_height": "None",
          "gameboard_width": "None",
          "ip": "None",
          "port": "5555"}


def load_config():
    config = configparser.ConfigParser()
    if not os.path.isfile('chain_reaction.ini'):
        config['DEFAULT'] = DEFAULTS
        config['SERVER'] = SERVER
        config['CLIENT'] = CLIENT
        with open('chain_reaction.ini', 'w', encoding="utf-8") as configfile:
            config.write(configfile)
    config.read('chain_reaction.ini', encoding="utf-8")
    return config


def get_config(config, default, section, key):
    # import ast
    # ast.literal_eval()
    if section in config:
        return config[section].get(key, default[f"{section.lower()}.{key}"])
    return default[f"{section.lower()}.{key}"]


def get_config_none(config, default, section, key, _type):
    value = get_config(config, default, section, key)
    if "none" in value.lower():
        return None
    return _type(value)

def get_config_bool(config, default, section, key):
    value = get_config(config, default, section, key)
    BOOLEAN_STATES = {'1': True, 'yes': True, 'true': True, 'on': True,
                      '0': False, 'no': False, 'false': False, 'off': False}
    return BOOLEAN_STATES[value.lower()]


def load_config_c():
    config_dict = {}
    config = load_config()
    config_dict["fps_limit"] = int(get_config(config, DEFAULTS, "CLIENT", "fps_limit"))
    config_dict["box_min_size"] = int(get_config(config, DEFAULTS, "CLIENT", "box_min_size"))
    config_dict["box_line_width"] = int(get_config(config, DEFAULTS, "CLIENT", "box_line_width"))
    config_dict["board_color"] = ast.literal_eval(get_config(config, DEFAULTS, "CLIENT", "board_color"))
    pygame.Color(config_dict["board_color"])  # tests for valid color
    config_dict["player_colors"] = ast.literal_eval(get_config(config, DEFAULTS, "CLIENT", "player_colors"))
    for player_color in config_dict["player_colors"]:
        pygame.Color(player_color)  # tests for valid player colors
    config_dict["nickname"] = get_config_none(config, DEFAULTS, "CLIENT", "nickname", str)
    if config_dict["nickname"] is not None:
        config_dict["nickname"].encode("utf-8", "strict")  # tests for valid uft-8 name
    config_dict["ip"] = get_config_none(config, DEFAULTS, "CLIENT", "ip", str)
    socket.inet_pton(socket.AF_INET, config_dict["ip"])  # tests for valid ip4
    config_dict["port"] = get_config_none(config, DEFAULTS, "CLIENT", "port", int)
    config_dict["be_player"] = get_config_bool(config, DEFAULTS, "CLIENT", "be_player")
    return config_dict


def load_config_s():
    config_dict = {}
    config = load_config()
    config_dict["player_num"] = get_config_none(config, DEFAULTS, "SERVER", "player_number", int)
    config_dict["width"] = get_config_none(config, DEFAULTS, "SERVER", "gameboard_width", int)
    config_dict["height"] = get_config_none(config, DEFAULTS, "SERVER", "gameboard_height", int)
    config_dict["port"] = get_config_none(config, DEFAULTS, "SERVER", "port", int)
    config_dict["ip"] = get_config_none(config, DEFAULTS, "SERVER", "ip", str)
    config_dict["reaction_time_step"] = float(get_config(config, DEFAULTS, "SERVER", "reaction_time_step"))
    return config_dict
