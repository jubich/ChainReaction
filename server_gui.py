#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Contains all gui's for the server process."""


from __future__ import annotations
from typing import Optional, Dict
import sys
import socket

import tkinter as tk


class server_gui():
    """Main server gui used for initial session start."""
    def __init__(self, player_num: Optional[int|None]=None,
                 width: Optional[int|None]=None,
                 height: Optional[int|None]=None, ip: Optional[str|None]=None,
                 port: Optional[int|None]=None) -> None:
        """Initializes the instance.

        Args:
            player_num: Number of players. Defaults to None.
            width: Number of boxes in x-direction. Defaults to None.
            height: Number of boxes in y-direction. Defaults to None.
            ip: Ip to bind. Defaults to None.
            port: Port to bind. Defaults to None.
        """
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

        screen_w = self._window.winfo_screenwidth()
        screen_h = self._window.winfo_screenheight()
        width = 300
        height = 146
        self._window.geometry(f"{width}x{height}+{int(screen_w/2-width/2)}+{int(screen_h/2-height/2)}")

        self._window.mainloop()

    def _close_window(self) -> None:
        """Closes the window and terminates server process with "sys.exit()"."""
        self._window.destroy()
        sys.exit()

    def _continue(self) -> None:
        """If button is pressed, saves inputs in their corresponding class variables and closes window."""
        self._player_num = int(self._pl_num_box.get())
        self._width = int(self._width_box.get())
        self._height = int(self._height_box.get())
        self._ip = self._ip_box.get()
        socket.inet_pton(socket.AF_INET, self._ip)  # tests for valid ip4
        self._port = int(self._port_box.get())
        self._window.destroy()

    def get_inputs(self) -> Dict[str, int|str]:
        """Collects variables containing the inputs and combines them in a dictionary.

        Returns:
            inputs: Dictionary containing collected inputs.
        """
        inputs = {}
        inputs["player_num"] = self._player_num
        inputs["width"] = self._width
        inputs["height"] = self._height
        inputs["ip"] = self._ip
        inputs["port"] = self._port
        return inputs

    @staticmethod
    def write_entry_txt(entry: tk.Entry, txt: str|int) -> None:
        """Replaces text in "entry" with "txt".

        Args:
            entry: Entrybox whose text will be replaced.
            txt: Text to be placed in "entry".
        """
        entry.delete(0, tk.END)
        entry.insert(0, txt)


class server_gui_restart():
    """Server gui used for restarting a game."""
    def __init__(self, player_num: Optional[int|None]=None,
                 width: Optional[int|None]=None,
                 height: Optional[int|None]=None) -> None:
        """Initializes the instance.

        Args:
            player_num: Number of players. Defaults to None.
            width: Number of boxes in x-direction. Defaults to None.
            height: Number of boxes in y-direction. Defaults to None.
        """
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

        screen_w = self._window.winfo_screenwidth()
        screen_h = self._window.winfo_screenheight()
        width = 300
        height = 100
        self._window.geometry(f"{width}x{height}+{int(screen_w/2-width/2)}+{int(screen_h/2-height/2)}")

        self._window.mainloop()

    def _close_window(self) -> None:
        """Closes the window and terminates server process with "sys.exit()"."""
        self._window.destroy()
        sys.exit()

    def _continue(self) -> None:
        """If button is pressed, saves inputs in their corresponding class variables and closes window."""
        self._player_num = int(self._pl_num_box.get())
        self._width = int(self._width_box.get())
        self._height = int(self._height_box.get())
        self._window.destroy()

    def get_inputs(self, s_inputs: Dict[str, int|str]) -> Dict[str, int|str]:
        """Collects variables containing the inputs and combines them in a dictionary.

        Args:
            s_inputs: Old inputs.

        Returns:
            s_inputs: Dictionary containing old inputs updated with newly collected inputs.
        """
        s_inputs["player_num"] = self._player_num
        s_inputs["width"] = self._width
        s_inputs["height"] = self._height
        return s_inputs

    @staticmethod
    def write_entry_txt(entry: tk.Entry, txt: str|int) -> None:
        """Replaces text in "entry" with "txt".

        Args:
            entry: Entrybox whose text will be replaced.
            txt: Text to be placed in "entry".
        """
        entry.delete(0, tk.END)
        entry.insert(0, txt)


if __name__ == "__main__":
    pass
    # s_gui = server_gui()
    # s_inputs = s_gui.get_inputs()
    # s_gui_r = server_gui_restart()
    # s_inputs = s_gui_r.get_inputs()
