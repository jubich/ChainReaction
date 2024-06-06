#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import tkinter as tk
import numpy as np

class client_gui():
    def __init__(self, nickname=None, ip=None, port=None):
        self._nickname = nickname
        self._ip = ip
        self._port = port

        self._window = tk.Tk()
        self._window.title('Client GUI')
        self._window.protocol("WM_DELETE_WINDOW", self._close_window)

        row = 0
        tk.Label(self._window, text="Nickname:").grid(row=row, column=0)
        self._nickname_box = tk.Entry(self._window)
        self._nickname_box.grid(row=row, column=1)
        if self._nickname is not None:
            self.write_entry_txt(self._nickname_box, self._nickname)

        row += 1
        tk.Label(self._window, text="IP:").grid(row=row, column=0)
        self._ip_box = tk.Entry(self._window)
        self._ip_box.grid(row=row, column=1)
        if self._ip is not None:
            self.write_entry_txt(self._ip_box, self._ip)

        row += 1
        tk.Label(self._window, text="Port:").grid(row=row, column=0)
        self._port_box = tk.Entry(self._window)
        self._port_box.grid(row=row, column=1)
        if self._port is not None:
            self.write_entry_txt(self._port_box, self._port)

        row += 1
        tk.Button(self._window, text='Continue', command=self._continue).grid(row=row, column=1)

        self._window.mainloop()

    def _close_window(self):
        self._window.destroy()
        sys.exit()

    def _continue(self):
        self._nickname = self._nickname_box.get()
        self._ip = self._ip_box.get()
        self._port = int(self._port_box.get())
        self._window.destroy()

    def get_inputs(self):
        inputs = {}
        inputs["nickname"] = self._nickname
        inputs["ip"] = self._ip
        inputs["port"] = self._port
        return inputs

    @staticmethod
    def write_entry_txt(entry, txt):
        entry.delete(0, tk.END)
        entry.insert(0, txt)


class client_quit_gui():
    def __init__(self):

        self._window = tk.Tk()
        self._window.title('Quit')
        self._window.protocol("WM_DELETE_WINDOW", self._close_window)

        row = 0
        tk.Label(self._window, text="Do you really want to quit?").grid(row=row, column=0)

        row += 1
        tk.Button(self._window, text='Yes', command=self._do_quit).grid(row=row, column=0)
        tk.Button(self._window, text='No', command=self._not_quit).grid(row=row, column=1)

        self._window.mainloop()

    def _close_window(self):
        self._window.destroy()

    def _not_quit(self):
        self.quit = False
        self._window.destroy()

    def _do_quit(self):
        self.quit = True
        self._window.destroy()

    def get_input(self):
        return self.quit

if __name__ == "__main__":
    pass
    # c_gui = client_gui()
    # c_inputs = c_gui.get_inputs()
    # quit_gui = client_quit_gui()
    # print(quit_gui.quit())
