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
from server_gui import server_gui


s_gui = server_gui(player_num=3, width=3, height=3,
                   ip=socket.gethostbyname(socket.gethostname()), port=5555)

s_inputs = s_gui.get_inputs()

server = Network_s(s_inputs["ip"], s_inputs["port"])

if not server.bind_address(2):
    print("Faild to bind server on", s_inputs["ip"], s_inputs["port"])
    time.sleep(2)
    sys.exit()
print("bound succesfull")

server.setblocking(False)

run = True

game = Gamecalc(s_inputs["player_num"], s_inputs["width"], s_inputs["height"],
                server)

player_num_list = [*range(s_inputs["player_num"])]

player = {}
round_num = 0
pos_l = []
while run:
    connections = server.connections
    readable, writable, errored = select.select(connections + [server.server],
                                                connections, connections, 0.5)

    for read in readable:
        if read == server.server:
            conn, addr = server.accept_connection(False)
            print(f"New connection to {conn}, {addr}")
            if len(player_num_list) != 0:
                player[player_num_list[0]] = {"conn": conn, "addr": addr}
                player[conn] = player_num_list[0]
                server.send(conn, ("your number", player_num_list[0]))
                print(f"player got number {player_num_list[0]}")
                player_num_list.pop(0)
            else:
                server.send(conn, ("viewer", None))

        else:
            msg = server.recieve(read)
            if msg[0] is None:
                continue
            elif msg[0] == "ByeBye":
                print(f"player {player.get(read, 'viewer')} left")
                if player.get(read, 'viewer') != "viewer":
                    game.set_eliminated(player[read])
                    for write in writable:
                        server.send(write, ("next player", game.player_to_move()))
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
            else:
                print(f"Unkown message: {msg}")
                msg = (None, None)

    if pos_l:
        print(f"Round {round_num} with player {game.player_to_move()} and move {pos_l}")
        game.update_player(game.player_to_move(), pos_l, [1], writable)
        pos_l = []
        for write in writable:
            server.send(write, ("next player", game.player_next_to_move()))
        game.increase_counter()
        round_num += 1

    for error in errored:
        if player.get(error, 'viewer') == "viewer":
            print(f"Closed conncetion to player 'viewer' at {error}")
        else:
            print(f"Closed conncetion to player {player[error]} at {player[player[error]]}")
        server.close_connection(error)
