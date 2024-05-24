#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# sending and recieving client and server


import socket
import pickle

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
        msg = pickle.dumps(data)
        msg = bytes(f"{len(msg):<{HEADERSIZE}}", "utf-8") + msg
        self.client.sendall(msg)

    def recieve(self):
        msg = self.client.recv(HEADERSIZE).decode("utf-8")
        if msg != "":
            msg_len = int(msg)
            return pickle.loads(self.client.recv(msg_len))
        return (None, None)

    def close(self):
        self.client.close()

    def setblocking(self, flag):
        self.client.setblocking(flag)


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
        msg = pickle.dumps(data)
        msg = bytes(f"{len(msg):<{HEADERSIZE}}", "utf-8") + msg
        connection.sendall(msg)

    def recieve(self, connection):
        msg = connection.recv(HEADERSIZE).decode("utf-8")
        if msg != "":
            msg_len = int(msg)
            return pickle.loads(connection.recv(msg_len))
        return (None, None)

    def close_connection(self, connection):
        self.connections.remove(connection)
        connection.close()

    def setblocking(self, flag):
        self.server.setblocking(flag)
