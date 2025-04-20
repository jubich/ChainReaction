#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Main file to start for the game server process.

Every game needs to have a server running which deals with the game calculations
and the connection to and from clients.
"""


from __future__ import annotations
from typing import Dict, Any
import sys
import time
import socket
import select
import uuid
import logging

from network import Network_s
from game_rules import Gamecalc
from server_gui import server_gui, server_gui_restart
from configfile import load_config_s
from loggingsetup import setup_logging, formatted_traceback


def game_loop(logger: logging.Logger, session_uuid: str, conn_uuid: Dict[socket.socket, str],
              server: Network_s, game: Gamecalc, player: Dict[socket.socket, int], nicknames: Dict[int, str],
              handshake_dict: Dict[str, Any]) -> None:
    """Starts a game.

    Recieves inputs from players and spectators via sockets. Calulates new game starte
    and send the new gamestate back to connected sockets.

    Args:
        logger: Logs the progress and state of the game/function.
        session_uuid: Differentiates different games sessions in log-files.
        conn_uuid: Connects the sockets to their respective uuids for connection with
          client log-files.
        server: Main class for dealing with sending and recieving of data via sockets.
        game: Class containing the game logic.
        player: Connects the socket to their respective "player_number" similar to
          "conn_uuid" but "player_number" is easier to deal with then uuid for selecting colors,
          etc.
        nicknames: Connects "player_number" to the respective player nicknames.
        handshake_dict: Contains information for the handshake to new connections.
    """
    logger.debug("Game loop started!", extra={"session_uuid": session_uuid})
    round_num = 0
    last_round_num = round_num
    run = True
    while run:
        pos_l = []
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
                continue

            msg = server.recieve(read)
            if (msg[0] == "ByeBye") or (msg[0] == None):
                if player.get(read, 'spectator') != "spectator":
                    print(f"Closed conncetion to player {nicknames[player[read]]}")
                    game.set_eliminated(player[read])
                    game.set_state_for_undo()
                    last_round_num = round_num
                    player.pop(read)
                    writable.remove(read)
                    if len(player) == 1:
                        game.winner = list(player.values())[0]
                    for write in writable:
                        server.send(write, ("next player", (game.player_to_move(),
                                                            round_num)))
                else:
                    print(f"Closed conncetion to spectator at {read}")
                server.close_connection(read)
                logger.debug("Connection closed",
                             extra={"session_uuid": session_uuid,
                                    "client_uuid": conn_uuid.pop(read),
                                    "next_player": game.player_to_move(),
                                    "round_num": round_num,
                                    "alive": game.player_alive,
                                    "counter": game._counter,
                                    "recieved": msg[0]})

            elif msg[0] == "position":
                pos = msg[1]
                logger.debug("Recieved position",
                             extra={"session_uuid": session_uuid,
                                    "client_uuid": conn_uuid[read],
                                    "position": pos})
                if player.get(read, "spectator") == game.player_to_move():
                    pos_val, pos_player = game.get_pos(pos[0], pos[1], False, True)
                    if (pos_player == game.player_to_move()) or (pos_val == 0):
                        pos_l = [pos]

            elif msg[0] == "undo":
                logger.debug("Recieved undo",
                             extra={"session_uuid": session_uuid,
                                    "client_uuid": conn_uuid[read]})
                if player.get(read, "spectator") != "spectator":
                    round_num = last_round_num
                    game.undo(writable, round_num)

            elif msg[0] == "handshake":
                logger.info("Added spectator",
                            extra={"session_uuid": session_uuid,
                                   "client_uuid": msg[1][2]})
                conn_uuid[read] = msg[1][2]
                server.send(conn, ("handshake", handshake_dict))
                server.send(conn, ("spectator", None))

            else:
                logger.warning("Recieved unknown msg",
                               extra={"session_uuid": session_uuid,
                                      "client_uuid": conn_uuid[read],
                                      "recieved": msg})

        for error in errored:
            if player.get(error, 'spectator') == "spectator":
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
                                             "move": pos_l[0]})
            game.set_state_for_undo()
            last_round_num = round_num
            game.update_player(game.player_to_move(), pos_l, [1], writable, round_num)

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


def main(session_uuid: str, logger: logging.Logger) -> None:
    """Gathers necessarry information for starting "game_loop".

    Deals with loading the config file, getting user input and binding the ip.
    After that the "restart-loop" is entered which deals with the handshake process,
    starting of the "game_loop" and dealing with the user inputs after a game.
    Exits via "sys.exit" if problem occurred.

    Args:
        session_uuid: Differentiates different games sessions in log-files.
        logger: Logs the progress and state of the game/function.
    """
    # load config
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

    # get user input via gui
    try:
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
                                  "s_inputs": s_inputs})

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

        nicknames, player, handshake_dict, conn_uuid = server.handshake(s_inputs)
        logger.info("Handshake done!", extra={"session_uuid": session_uuid})

        # start game
        game = Gamecalc(s_inputs["player_num"], s_inputs["width"],
                        s_inputs["height"], config["reaction_time_step"],
                        server, logger, session_uuid)

        game_loop(logger, session_uuid, conn_uuid, server, game, player,
                  nicknames, handshake_dict)

        logger.debug("Game loop stopped!", extra={"session_uuid": session_uuid})

        # get user input via gui
        try:
            restart_gui = server_gui_restart(player_num=s_inputs["player_num"],
                                             width=s_inputs["width"],
                                             height=s_inputs["height"])
            s_inputs = restart_gui.get_inputs(s_inputs)
        except Exception as err:
            logger.exception("Error in restart gui input!",
                             extra={"session_uuid": session_uuid,
                                    "s_inputs": s_inputs,
                                    "traceback": formatted_traceback(err)})
            restart = False

    logger.debug("Server stopped!", extra={"session_uuid": session_uuid})


if __name__ == "__main__":
    session_uuid = str(uuid.uuid4())  # to differentiate sessions
    logger = setup_logging("server.log.jsonl")
    logger.debug("New session started!", extra={"session_uuid": session_uuid})
    try:
        main(session_uuid, logger)
    except Exception as err:
        logger.critical("Unexpected Error!",
                        extra={"session_uuid": session_uuid,
                               "traceback": formatted_traceback(err)})
        time.sleep(2)
