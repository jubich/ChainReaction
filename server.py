#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# deals with calc and player_pos
# recieves new player_pos -> check on server and on client
# sends player_arrays


import sys
import time
import socket
import select

from network import Network_s
from game_rules import Gamecalc
from server_gui import server_gui, server_gui_restart
from configfile import load_config, get_config, get_config_none, DEFAULTS

# load config
config = load_config()
player_num = get_config_none(config, DEFAULTS, "SERVER", "player_number", int)
width = get_config_none(config, DEFAULTS, "SERVER", "gameboard_width", int)
height = get_config_none(config, DEFAULTS, "SERVER", "gameboard_height", int)
port = int(get_config(config, DEFAULTS, "SERVER", "port"))
if get_config_none(config, DEFAULTS, "SERVER", "ip", str) is None:
    ip = socket.gethostbyname(socket.gethostname())
else:
    ip = get_config(config, DEFAULTS, "SERVER", "ip")
reaction_time_step = float(get_config(config, DEFAULTS, "SERVER", "reaction_time_step"))

# get user inputs via gui
s_gui = server_gui(player_num=player_num, width=width, height=height,
                   ip=socket.gethostbyname(socket.gethostname()), port=port)

s_inputs = s_gui.get_inputs()

# initial handshake
server = Network_s(s_inputs["ip"], s_inputs["port"])

if not server.bind_address(2):
    print("Failed to bind server on", s_inputs["ip"], s_inputs["port"])
    time.sleep(2)
    sys.exit()
print("Bound succesfull!")
server.setblocking(False)

restart = True

while restart:
    # restart loop

    nicknames, player, _, handshake_dict = server.handshake(s_inputs)
    print("Handshake done!")

    # start game

    run = True

    game = Gamecalc(s_inputs["player_num"], s_inputs["width"], s_inputs["height"],
                    reaction_time_step, server)

    round_num = 0
    last_round_num = round_num
    pos_l = []
    while run:
        # Game loop
        connections = server.connections
        readable, writable, errored = select.select(connections + [server.server],
                                                    connections, connections, 0.5)

        for read in readable:
            if read == server.server:
                conn, addr = server.accept_connection(False)
                print(f"New connection to {conn}, {addr}")
                server.send(conn, ("handshake", handshake_dict))
                server.send(conn, ("viewer", None))

            else:
                msg = server.recieve(read)
                if msg[0] is None:
                    continue
                elif msg[0] == "ByeBye":
                    print(f"player {player.get(read, 'viewer')} left")
                    if player.get(read, 'viewer') != "viewer":
                        game.set_eliminated(player[read])
                        game.set_state_for_undo()
                        last_round_num = round_num
                        for write in writable:
                            server.send(write, ("next player", (game.player_to_move(),
                                                                round_num)))
                    errored.append(read)
                elif msg[0] == "position":
                    msg = msg[1]
                    if player.get(read, "viewer") == game.player_to_move():
                        row, column = msg
                        pos_val, pos_player = game.get_pos(row, column, False, True)
                        if (pos_player == game.player_to_move()) or (pos_val == 0):
                            pos_l = [msg]
                        else:
                            pos_l = []
                    else:
                        pos_l = []
                    msg = (None, None)
                elif msg[0] == "undo":
                    round_num = last_round_num
                    game.undo(writable, round_num)
                else:
                    print(f"Unkown message: {msg}")
                    msg = (None, None)

        if pos_l:
            print(f"Round {round_num} with player {game.player_to_move()} and move {pos_l}")
            game.set_state_for_undo()
            last_round_num = round_num
            game.update_player(game.player_to_move(), pos_l, [1], writable)
            if game.winner is not None:
                print("finished")
                for write in writable:
                    server.send(write, ("finished", game.winner))
                    time.sleep(0.2)
                    server.close_connection(write)
                run = False
                break

            pos_l = []
            round_num += 1
            for write in writable:
                server.send(write, ("next player", (game.player_next_to_move(), round_num)))
            game.increase_counter()

        for error in errored:
            if player.get(error, 'viewer') == "viewer":
                print(f"Closed conncetion to player 'viewer' at {error}")
            else:
                print(f"Closed conncetion to player {player[error]}")
            server.close_connection(error)

    restart_gui = server_gui_restart(player_num=s_inputs["player_num"],
                                     width=s_inputs["width"],
                                     height=s_inputs["height"])
    restart_input = restart_gui.get_inputs()
    s_inputs["player_num"] = restart_input["player_num"]
    s_inputs["width"] = restart_input["width"]
    s_inputs["height"] = restart_input["height"]
