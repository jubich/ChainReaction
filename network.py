#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# sending and recieving client and server


import sys
import time
import socket
import pickle
import select
import random

HEADERSIZE = 20


class Network_c:
    def __init__(self, ip, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.addr = (self.ip, self.port)

    def connect(self):
        try:
            self.client.connect(self.addr)
            print("connected")
            return True
        except Exception as e:
            print("connection failed:", e.args)
            return False

    def send(self, data):
        print("sending", data)
        msg = pickle.dumps(data)
        msg = bytes(f"{len(msg):<{HEADERSIZE}}", "utf-8") + msg
        self.client.sendall(msg)

    def recieve(self):
        msg = self.client.recv(HEADERSIZE).decode("utf-8")
        if msg != "":
            msg_len = int(msg)
            recv = pickle.loads(self.client.recv(msg_len))
            print("recieved", recv)
            return recv
        return (None, None)

    def close(self):
        self.client.close()
        print("Connection closed!")

    def setblocking(self, flag):
        self.client.setblocking(flag)

    def handshake(self, nickname, player=True):
        tries = 0
        if player:
            self.send(("handshake", ("player", nickname)))
        else:
            self.send(("handshake", ("spectator", None)))
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
                    print(f"Unkown message: {msg}")
            if errored:
                print("Connection failed!")
                self.close()
                time.sleep(2)
                sys.exit()
        print("Handshake took to long!")
        print("Handshake stopped!")
        self.send(("ByeBye", None))
        self.close()
        time.sleep(2)
        sys.exit()


class Network_s:
    def __init__(self, ip, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.addr = (self.ip, self.port)
        self.connections = []

    def bind_address(self, listen):
        try:
            self.server.bind(self.addr)
            self.server.listen(listen)
            return True
        except Exception as e:
            print("Failed binding", e.args)
            return False

    def accept_connection(self, blocking_flag):
        connection, addr = self.server.accept()
        connection.setblocking(blocking_flag)
        self.connections.append(connection)
        return connection, addr

    def send(self, connection, data):
        print("sending", data)
        msg = pickle.dumps(data)
        msg = bytes(f"{len(msg):<{HEADERSIZE}}", "utf-8") + msg
        connection.sendall(msg)

    def recieve(self, connection):
        msg = connection.recv(HEADERSIZE).decode("utf-8")
        if msg != "":
            msg_len = int(msg)
            recv = pickle.loads(connection.recv(msg_len))
            print("recieved", recv)
            return recv
        return (None, None)

    def close_connection(self, connection):
        self.connections.remove(connection)
        connection.close()
        print(f"Closed connection to {connection}!")

    def setblocking(self, flag):
        self.server.setblocking(flag)

    def handshake(self, s_inputs):
        finished = False
        players = {}
        spectators = []
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
                else:
                    msg = self.recieve(read)
                    if msg[0] == "handshake":
                        if msg[1][0] == "player":
                            if len(players) == s_inputs["player_num"]:
                                finished = True
                                spectators.append(read)
                            else:
                                players[read] = msg[1][1]
                        else:
                            spectators.append(read)
                    elif msg[0] == "ByeBye":
                        if players.pop(read, None) is None:
                            spectators.remove(read)
                        self.close_connection(read)
                    else:
                        print(f"Unkown message: {msg}")

            for error in errored:
                print(f"Error with {error}!")
                self.close_connection(error)

            if len(players) >= s_inputs["player_num"]:
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
        for conn, num in player_dict.items():
            self.send(conn, ("handshake", handshake_dict))
            self.send(conn, ("your number", num))

        for spectator in spectators:
            self.send(spectator, ("viewer", None))

        return nicknames_dict, player_dict, spectators, handshake_dict
