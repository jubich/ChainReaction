#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Handles sending and recieving of data via sockets as well as the handshake for client and server processes."""


from __future__ import annotations
from typing import Dict, Tuple, Any, Optional
import sys
import time
import socket
import pickle
import select
import random
import logging

from chainreaction.loggingsetup import formatted_traceback

HEADERSIZE = 20


class Network_c:
    """Deals with the client side socket connection to the server."""
    def __init__(self, ip: str, port: int, logger: logging.Logger, client_uuid: str) -> None:
        """Initializes the instance.

        Args:
            ip: Ip to bind.
            port: Port to bind.
            logger: Logs the progress and state of the game/function.
            client_uuid: Differentiates different clients in log-files.
        """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.addr = (self.ip, self.port)
        self.logger = logger
        self.client_uuid = client_uuid

    def connect(self) -> bool:
        """Connects to the server.

        Returns:
            "True" if connection succeeded else "False".
        """
        try:
            self.client.connect(self.addr)
            return True
        except (OSError, UnboundLocalError) as err:
            self.logger.error("Connection failed!",
                              extra={"client_uuid": self.client_uuid,
                                     "traceback": formatted_traceback(err)})
            return False

    def send(self, data: Tuple[str, Any]) -> None:
        """Sends "data" to the server, exits with "sys.exit()" if an error occurse.

        Args:
            data: Will be send to the server.
        """
        msg = pickle.dumps(data)
        msg = bytes(f"{len(msg):<{HEADERSIZE}}", "utf-8") + msg
        try:
            self.client.sendall(msg)
        except (OSError, UnboundLocalError) as err:
            self.logger.error("Error while sending!",
                              extra={"session_uuid": self.client_uuid,
                                     "traceback": formatted_traceback(err),
                                     "data": data})
            self.close()
            sys.exit()

    def recieve(self) -> Tuple[str|None, Any]:
        """Recieves data from the server.

        Returns:
            Data send by the server.
        """
        try:
            msg = self.client.recv(HEADERSIZE).decode("utf-8")
            if msg != "":
                msg_len = int(msg)
                recv = pickle.loads(self.client.recv(msg_len))
                return recv
        except (OSError, UnboundLocalError) as err:
            self.logger.error("Error while sending!",
                              extra={"session_uuid": self.client_uuid,
                                     "traceback": formatted_traceback(err)})
        return (None, None)

    def close(self) -> None:
        """Closes connection to the server."""
        try:
            self.client.close()
        except (OSError, UnboundLocalError) as err:
            self.logger.error("Error while closing connection!",
                              extra={"session_uuid": self.client_uuid,
                                     "traceback": formatted_traceback(err)})

    def setblocking(self, flag: bool) -> None:
        """Set blocking or non-blocking mode of the socket.

        Args:
            flag: Wether the socket is blocking or not.
        """
        self.client.setblocking(flag)

    def handshake(self, nickname: str, be_player: Optional[bool]=True) -> Dict[str, Any]:
        """Deals with the "handshake" between server and client.

        After 100 sec the handshake will be aborted and the client process will be
        closed via "sys.exit()".

        Args:
            nickname: Nickname of the client.
            be_player: Whether the client is "player" or "spectator". Defaults to True.

        Returns:
            Dictionary containing the information from the handshake.
        """
        tries = 0
        if be_player:
            self.send(("handshake", ("player", nickname, self.client_uuid)))
            self.logger.debug("Handshake player",
                              extra={"client_uuid": self.client_uuid})
        else:
            self.send(("handshake", ("spectator", None, self.client_uuid)))
            self.logger.debug("Handshake spectator",
                              extra={"client_uuid": self.client_uuid})
        while tries < 100:
            time.sleep(1)
            tries += 1
            print("Waiting for players ...")
            readable, _, errored = select.select([self.client], [self.client],
                                                 [self.client], 1)
            if readable:
                msg = self.recieve()
                if msg[0] == "handshake":
                    return msg[1]
                else:
                    self.logger.warning("Handshake, Unkown message",
                                        extra={"client_uuid": self.client_uuid,
                                               "recieved": msg})
                    self.send(("ByeBye", None))
                    self.close()
                    sys.exit()

            if errored:
                self.logger.error("Connection failed!",
                                  extra={"client_uuid": self.client_uuid})
                self.close()
                sys.exit()
        self.logger.warning("Handshake took to long, connection closed!",
                            extra={"client_uuid": self.client_uuid})
        self.send(("ByeBye", None))
        self.close()
        sys.exit()


class Network_s:
    """Deals with the server side socket connection to the clients."""
    def __init__(self, ip: str, port: int, logger: logging.Logger, session_uuid: str) -> None:
        """Initializes the instance.

        Args:
            ip: Ip to bind.
            port: Port to bind.
            logger: Logs the progress and state of the game/function.
            session_uuid: Differentiates different games sessions in log-files.
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.addr = (self.ip, self.port)
        self.connections = []
        self.logger = logger
        self.session_uuid = session_uuid

    def bind_address(self, listen: int) -> bool:
        """Binds the "ip" and "port" and defines the maximum of unaccepted connections.

        Args:
            listen: Number of unaccepted connections before refusing further connections.

        Returns:
            Wether the binding was successful or not.
        """
        try:
            self.server.bind(self.addr)
            self.server.listen(listen)
            return True
        except (OSError, UnboundLocalError) as err:
            self.logger.error("Failed binding!",
                              extra={"session_uuid": self.session_uuid,
                                     "traceback": formatted_traceback(err)})
            return False

    def accept_connection(self, blocking_flag: bool) -> Tuple[socket.socket, socket.AddressInfo]:
        """Accepts new connection of clients and sets blocking or non-blocking mode
        of the new socket.

        Args:
            blocking_flag: Wether the socket is blocking or not.

        Returns:
            connection: Socket connection with new client.
            addr: Address info to new client connection.
        """
        connection, addr = self.server.accept()
        connection.setblocking(blocking_flag)
        self.connections.append(connection)
        return connection, addr

    def send(self, connection: socket.socket, data: Tuple[str, Any]) -> None:
        """Sends "data" to "connection", closes connection if an error occurse.

        Args:
            connection: Client which should receive the data.
            data: Will be send to "connection".
        """
        msg = pickle.dumps(data)
        msg = bytes(f"{len(msg):<{HEADERSIZE}}", "utf-8") + msg
        try:
            connection.sendall(msg)
        except (OSError, UnboundLocalError) as err:
            self.logger.error("Error while sending!",
                              extra={"session_uuid": self.session_uuid,
                                     "traceback": formatted_traceback(err),
                                     "data": data})
            self.close_connection(connection)

    def recieve(self, connection: socket.socket) -> Tuple[str|None, Any]:
        """Recieves data from "connection".

        Args:
            connection: Connection who send data.

        Returns:
            Data send by "connection".
        """
        try:
            msg = connection.recv(HEADERSIZE).decode("utf-8")
            if msg != "":
                msg_len = int(msg)
                recv = pickle.loads(connection.recv(msg_len))
                return recv
        except (OSError, UnboundLocalError) as err:
            self.logger.error("Error while sending!",
                              extra={"session_uuid": self.session_uuid,
                                     "traceback": formatted_traceback(err)})
        return (None, None)

    def close_connection(self, connection: socket.socket) -> None:
        """Closes connection to "connection".

        Args:
            connection: Connection which should be closed.
        """
        self.connections.remove(connection)
        try:
            connection.close()
        except (OSError, UnboundLocalError) as err:
            self.logger.error("Error while closing connection!",
                              extra={"session_uuid": self.session_uuid,
                                     "traceback": formatted_traceback(err)})

    def setblocking(self, flag: bool) -> None:
        """Set blocking or non-blocking mode of the socket.

        Args:
            flag: Wether the socket is blocking or not.
        """
        self.server.setblocking(flag)

    def handshake(self, s_inputs: Dict[str, int|str]) -> Tuple[Dict[int, str],
                                                               Dict[socket.socket, int],
                                                               Dict[str, Any],
                                                               Dict[socket.socket, str]]:
        """Deals with the "handshake" between server and client.

        Args:
            s_inputs: Inputs collected via the gui.

        Returns:
            nicknames_dict: Connects "player_number" to the respective player nicknames.
            player_dict: Connects the socket to their respective "player_number" similar to
              "conn_uuid" but "player_number" is easier to deal with then uuid for selecting colors,
              etc.
            handshake_dict: Dictionary containing the information from the handshake.
            conn_uuid: Connects the sockets to their respective uuids for connection with
              client log-files.
        """
        finished = False
        players = {}
        spectators = []
        conn_uuid = {}
        while not finished:
            time.sleep(1)
            print("Waiting for players ...")
            readable, _, errored = select.select(self.connections + [self.server],
                                                 self.connections,
                                                 self.connections, 1)
            for read in readable:
                if read == self.server:
                    conn, addr = self.accept_connection(False)
                    print(f"New connection to {conn}, {addr}")
                    self.logger.debug("New connection",
                                      extra={"session_uuid": self.session_uuid})
                else:
                    msg = self.recieve(read)
                    if msg[0] == "handshake":
                        if msg[1][0] == "player":
                            if len(players) == s_inputs["player_num"]:
                                finished = True
                                spectators.append(read)
                                self.logger.info("Added player as spectator",
                                                  extra={"session_uuid": self.session_uuid,
                                                         "client_uuid": msg[1][2]})
                                conn_uuid[read] = msg[1][2]
                            else:
                                players[read] = msg[1][1]
                                self.logger.info("Added player",
                                                  extra={"session_uuid": self.session_uuid,
                                                         "client_uuid": msg[1][2]})
                                conn_uuid[read] = msg[1][2]
                        else:
                            self.logger.info("Added spectator",
                                              extra={"session_uuid": self.session_uuid,
                                                     "client_uuid": msg[1][2]})
                            spectators.append(read)
                            conn_uuid[read] = msg[1][2]
                    elif msg[0] == "ByeBye":
                        print(f"Closed connection to {read}")
                        self.logger.debug("Closed connection",
                                          extra={"session_uuid": self.session_uuid,
                                                 "client_uuid": conn_uuid.pop(read)})
                        if players.pop(read, None) is None:
                            spectators.remove(read)
                        self.close_connection(read)
                    else:
                        self.logger.warning("Handshake, Unkown message",
                                            extra={"session_uuid": self.session_uuid,
                                                   "client_uuid": conn_uuid[read],
                                                   "recieved": msg})


            for error in errored:
                self.logger.error("Connection failed!",
                                  extra={"session_uuid": self.session_uuid,
                                         "client_uuid": conn_uuid.pop(error)})
                if players.pop(error, None) is None:
                    spectators.remove(error)
                self.close_connection(error)

            if len(players) >= s_inputs["player_num"]:
                self.logger.debug("All players joined",
                                  extra={"session_uuid": self.session_uuid})
                finished = True

        # randomize player order
        player_dict = {}
        nicknames_dict = {}

        for num in range(s_inputs["player_num"]):
            conn, nickname = random.choice([*players.items()])
            player_dict[conn] = num
            nicknames_dict[num] = nickname
            players.pop(conn)

        handshake_dict = {}
        handshake_dict["nicknames"] = nicknames_dict
        handshake_dict["player_num"] = s_inputs["player_num"]
        handshake_dict["width"] = s_inputs["width"]
        handshake_dict["height"] = s_inputs["height"]
        handshake_dict["session_uuid"] = self.session_uuid
        for conn, num in player_dict.items():
            self.send(conn, ("handshake", handshake_dict))
            self.send(conn, ("your number", num))
            self.logger.debug("Send handshake and number",
                              extra={"session_uuid": self.session_uuid,
                                     "client_uuid": conn_uuid[conn],
                                     "number": num})

        for spectator in spectators:
            self.send(spectator, ("handshake", handshake_dict))
            self.send(spectator, ("spectator", None))
            self.logger.debug("Send handshake and spectator",
                              extra={"session_uuid": self.session_uuid,
                                     "client_uuid": conn_uuid[conn]})
        return nicknames_dict, player_dict, handshake_dict, conn_uuid
