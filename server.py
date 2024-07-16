#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# deals with calc and player_pos
# recieves new player_pos -> check on server and on client
# sends player_arrays


import sys
import time
import socket
import select
import uuid

from network import Network_s
from game_rules import Gamecalc
from server_gui import server_gui, server_gui_restart
from configfile import load_config_s
from loggingsetup import setup_logging, formatted_traceback

session_uuid = str(uuid.uuid4())  # to differentiate sessions
logger = setup_logging("server.log.jsonl")
logger.debug("New session started!", extra={"session_uuid": session_uuid})

try:
    try:
        config = load_config_s()
        if config["ip"] is None:
            config["ip"] = socket.gethostbyname(socket.gethostname())
            logger.debug("IP from socket", extra={"session_uuid": session_uuid})
    except Exception as err:
        logger.error("Error in loading config!",
                     extra={"session_uuid": session_uuid,
                            "traceback": formatted_traceback(err)})
        sys.exit()
    logger.debug("Config loaded", extra={"session_uuid": session_uuid,
                                         "config": config})

    try:
        # get user inputs via gui
        s_gui = server_gui(player_num=config["player_num"],
                           width=config["width"], height=config["height"],
                           ip=config["ip"], port=config["port"])
        s_inputs = s_gui.get_inputs()
    except Exception as err:
        logger.error("Error in gui input!",
                     extra={"session_uuid": session_uuid,
                            "traceback": formatted_traceback(err)})
        sys.exit()

    logger.debug("Inputs", extra={"session_uuid": session_uuid,
                                  "player_num": s_inputs["player_num"],
                                  "width": s_inputs["width"],
                                  "height": s_inputs["height"]})

    # initial handshake
    server = Network_s(s_inputs["ip"], s_inputs["port"], logger, session_uuid)

    if not server.bind_address(2):
        sys.exit()
    logger.info("Bound succesfull!", extra={"session_uuid": session_uuid})
    server.setblocking(False)

    restart = True

    while restart:
        # restart loop
        logger.debug("restart", extra={"session_uuid": session_uuid})

        nicknames, player, _, handshake_dict, conn_uuid = server.handshake(s_inputs)
        logger.info("Handshake done!", extra={"session_uuid": session_uuid})

        # start game

        run = True

        game = Gamecalc(s_inputs["player_num"], s_inputs["width"],
                        s_inputs["height"], config["reaction_time_step"],
                        server, logger, session_uuid)

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
                    logger.debug("New connection",
                                 extra={"session_uuid": session_uuid})
                else:
                    msg = server.recieve(read)
                    if (msg[0] == "ByeBye") or (msg[0] == None):
                        if player.get(read, 'viewer') != "viewer":
                            game.set_eliminated(player[read])
                            game.set_state_for_undo()
                            last_round_num = round_num
                            for write in writable:
                                server.send(write, ("next player", (game.player_to_move(),
                                                                    round_num)))
                        logger.debug("Connection closed",
                                     extra={"session_uuid": session_uuid,
                                            "client_uuid": conn_uuid.pop(read),
                                            "next_player": game.player_to_move(),
                                            "round_num": round_num,
                                            "alive": game.player_alive,
                                            "counter": game._counter,
                                            "recieved": msg[0]})
                        if player.get(read, 'viewer') == "viewer":
                            print(f"Closed conncetion to spectator at {read}")
                        else:
                            print(f"Closed conncetion to player {nicknames[player[read]]}")
                            player.pop(read)
                            writable.remove(read)
                            if len(player) == 1:
                                game.winner = list(player.values())[0]
                        server.close_connection(read)
                    elif msg[0] == "position":
                        msg = msg[1]
                        logger.debug("Recieved position",
                                     extra={"session_uuid": session_uuid,
                                            "client_uuid": conn_uuid[read],
                                            "position": msg})
                        if player.get(read, "viewer") == game.player_to_move():
                            row, column = msg
                            pos_val, pos_player = game.get_pos(row, column, False, True)
                            if (pos_player == game.player_to_move()) or (pos_val == 0):
                                pos_l = [msg]
                            else:
                                pos_l = []
                        else:
                            pos_l = []
                    elif msg[0] == "undo":
                        logger.debug("Recieved undo",
                                     extra={"session_uuid": session_uuid,
                                            "client_uuid": conn_uuid[read]})
                        if player.get(read, "viewer") != "viewer":
                            round_num = last_round_num
                            game.undo(writable, round_num)
                    elif msg[0] == "handshake":
                        logger.info("Added spectator",
                                    extra={"session_uuid": session_uuid,
                                           "client_uuid": msg[1][2]})
                        conn_uuid[read] = msg[1][2]
                        server.send(conn, ("handshake", handshake_dict))
                        server.send(conn, ("viewer", None))
                    else:
                        logger.warning("Recieved unknown msg",
                                       extra={"session_uuid": session_uuid,
                                              "client_uuid": conn_uuid[read],
                                              "recieved": msg})

            for error in errored:
                writable.remove(error)
                if player.get(error, 'viewer') == "viewer":
                    print(f"Closed conncetion to spectator at {error}")
                else:
                    print(f"Closed conncetion to player {nicknames[player[error]]}")
                    player.pop(error)
                    if len(player) == 1:
                        game.winner = list(player.values())[0]
                logger.error("Connection failed!",
                             extra={"session_uuid": session_uuid,
                                    "client_uuid": conn_uuid.pop(error)})
                server.close_connection(error)

            if pos_l:
                logger.debug("Make move", extra={"session_uuid": session_uuid,
                                                 "player_to_move": game.player_to_move(),
                                                 "round_num": round_num,
                                                 "move": pos_l})
                game.set_state_for_undo()
                last_round_num = round_num
                game.update_player(game.player_to_move(), pos_l, [1], writable, round_num)
                pos_l = []

                if game.winner is None:
                    round_num += 1
                    for write in writable:
                        server.send(write, ("next player", (game.player_next_to_move(), round_num)))
                    logger.debug("Next player", extra={"session_uuid": session_uuid,
                                                       "next_player": game.player_next_to_move(),
                                                       "round_num": round_num})
                    game.increase_counter()

            if game.winner is not None:
                logger.info("Game finished!",
                            extra={"session_uuid": session_uuid,
                                   "winner": game.winner,
                                   "time_line": game.time_line})
                for write in writable:
                    server.send(write, ("finished", (game.winner, game.time_line)))
                    time.sleep(0.2)
                    server.close_connection(write)
                    conn_uuid.pop(write)
                run = False
                break

        logger.debug("Game loop stopped!", extra={"session_uuid": session_uuid})
        try:
            restart_gui = server_gui_restart(player_num=s_inputs["player_num"],
                                             width=s_inputs["width"],
                                             height=s_inputs["height"])
            restart_input = restart_gui.get_inputs()
            s_inputs["player_num"] = restart_input["player_num"]
            s_inputs["width"] = restart_input["width"]
            s_inputs["height"] = restart_input["height"]
        except Exception as err:
            logger.exception("Error in restart gui input!",
                             extra={"session_uuid": session_uuid,
                                    "traceback": formatted_traceback(err)})
            sys.exit()

    logger.debug("Server stopped!", extra={"session_uuid": session_uuid})
except Exception as err:
    logger.critical("Unexpected Error!",
                    extra={"session_uuid": session_uuid,
                           "traceback": formatted_traceback(err)})
    time.sleep(2)
