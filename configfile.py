#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import os


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
