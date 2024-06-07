#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import tkinter as tk


class server_gui():
    def __init__(self, player_num=None, width=None, height=None, ip=None,
                 port=None):
        self._player_num = player_num
        self._width = width
        self._height = height
        self._ip = ip
        self._port = port

        self._window = tk.Tk()
        self._window.title('Server GUI')
        self._window.protocol("WM_DELETE_WINDOW", self._close_window)

        row = 0
        tk.Label(self._window, text="Number of players:").grid(row=row, column=0)
        self._pl_num_box = tk.Entry(self._window)
        self._pl_num_box.grid(row=row, column=1)
        if self._player_num is not None:
            self.write_entry_txt(self._pl_num_box, self._player_num)

        row += 1
        tk.Label(self._window, text="Board tiles width:").grid(row=row, column=0)
        self._width_box = tk.Entry(self._window)
        self._width_box.grid(row=row, column=1)
        if self._width is not None:
            self.write_entry_txt(self._width_box, self._width)

        row += 1
        tk.Label(self._window, text="Board tiles height:").grid(row=row, column=0)
        self._height_box = tk.Entry(self._window)
        self._height_box.grid(row=row, column=1)
        if self._height is not None:
            self.write_entry_txt(self._height_box, self._height)

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
        self._player_num = int(self._pl_num_box.get())
        self._width = int(self._width_box.get())
        self._height = int(self._height_box.get())
        self._ip = self._ip_box.get()
        self._port = int(self._port_box.get())
        self._window.destroy()

    def get_inputs(self):
        inputs = {}
        inputs["player_num"] = self._player_num
        inputs["width"] = self._width
        inputs["height"] = self._height
        inputs["ip"] = self._ip
        inputs["port"] = self._port
        return inputs

    @staticmethod
    def write_entry_txt(entry, txt):
        entry.delete(0, tk.END)
        entry.insert(0, txt)


class server_gui_restart():
    def __init__(self, player_num=None, width=None, height=None):
        self._player_num = player_num
        self._width = width
        self._height = height

        self._window = tk.Tk()
        self._window.title('Server GUI')
        self._window.protocol("WM_DELETE_WINDOW", self._close_window)

        row = 0
        tk.Label(self._window, text="Number of players:").grid(row=row, column=0)
        self._pl_num_box = tk.Entry(self._window)
        self._pl_num_box.grid(row=row, column=1)
        if self._player_num is not None:
            self.write_entry_txt(self._pl_num_box, self._player_num)

        row += 1
        tk.Label(self._window, text="Board tiles width:").grid(row=row, column=0)
        self._width_box = tk.Entry(self._window)
        self._width_box.grid(row=row, column=1)
        if self._width is not None:
            self.write_entry_txt(self._width_box, self._width)

        row += 1
        tk.Label(self._window, text="Board tiles height:").grid(row=row, column=0)
        self._height_box = tk.Entry(self._window)
        self._height_box.grid(row=row, column=1)
        if self._height is not None:
            self.write_entry_txt(self._height_box, self._height)

        row += 1
        tk.Button(self._window, text='Continue', command=self._continue).grid(row=row, column=1)

        self._window.mainloop()

    def _close_window(self):
        self._window.destroy()
        sys.exit()

    def _continue(self):
        self._player_num = int(self._pl_num_box.get())
        self._width = int(self._width_box.get())
        self._height = int(self._height_box.get())
        self._window.destroy()

    def get_inputs(self):
        inputs = {}
        inputs["player_num"] = self._player_num
        inputs["width"] = self._width
        inputs["height"] = self._height
        return inputs

    @staticmethod
    def write_entry_txt(entry, txt):
        entry.delete(0, tk.END)
        entry.insert(0, txt)


if __name__ == "__main__":
    # s_gui = server_gui()
    # s_inputs = s_gui.get_inputs()
    s_gui_r = server_gui_restart()
    s_inputs = s_gui_r.get_inputs()
