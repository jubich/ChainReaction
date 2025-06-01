#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Contains all none pygame gui's for the client process."""


from __future__ import annotations
from typing import Optional, Dict, Tuple, List
import sys
import socket

import tkinter as tk
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.ticker as ticker
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class client_gui():
    """Main client gui used for initial session start."""
    def __init__(self, nickname: Optional[str, None]=None, ip: Optional[str, None]=None,
                 port: Optional[int, None]=None, be_player: Optional[bool]=True) -> None:
        """Initializes the instance.

        Args:
            nickname: Nickname of the client. Defaults to None.
            ip: Ip of the server to connect. Defaults to None.
            port: Port of the server to connect. Defaults to None.
            be_player: Whether the client is "player" or "spectator". Defaults to True.
        """
        self._nickname = nickname
        self._ip = ip
        self._port = port

        self._window = tk.Tk()
        self._window.title('Client GUI')
        self._window.protocol("WM_DELETE_WINDOW", self._close_window)

        self.be_player = be_player

        row = 0
        tk.Label(self._window, text="Nickname:").grid(row=row, column=0)
        self._nickname_box = tk.Entry(self._window, width=35)
        self._nickname_box.grid(row=row, column=1)
        if self._nickname is not None:
            self.write_entry_txt(self._nickname_box, self._nickname)

        row += 1
        tk.Label(self._window, text="IP:").grid(row=row, column=0)
        self._ip_box = tk.Entry(self._window, width=35)
        self._ip_box.grid(row=row, column=1)
        if self._ip is not None:
            self.write_entry_txt(self._ip_box, self._ip)

        row += 1
        tk.Label(self._window, text="Port:").grid(row=row, column=0)
        self._port_box = tk.Entry(self._window, width=35)
        self._port_box.grid(row=row, column=1)
        if self._port is not None:
            self.write_entry_txt(self._port_box, self._port)

        row += 1
        self.spectator_cbutton = tk.Checkbutton(self._window, text='Spectator', command=self._set_spectator)
        self.spectator_cbutton.grid(row=row, column=1)
        if not self.be_player:
            self.spectator_cbutton.select()

        row += 1
        tk.Button(self._window, text='Continue', command=self._continue).grid(row=row, column=1)

        screen_w = self._window.winfo_screenwidth()
        screen_h = self._window.winfo_screenheight()
        width = 370
        height = 125
        self._window.geometry(f"{width}x{height}+{int(screen_w/2-width/2)}+{int(screen_h/2-height/2)}")

        self._window.mainloop()

    def _close_window(self) -> None:
        """Closes the window and terminates client process with "sys.exit()"."""
        self._window.destroy()
        sys.exit()

    def _continue(self) -> None:
        """If button is pressed, saves inputs in their corresponding class variables and closes window."""
        self._nickname = self._nickname_box.get()[:15]
        self._ip = self._ip_box.get()
        socket.inet_pton(socket.AF_INET, self._ip)  # tests for valid ip4
        self._port = int(self._port_box.get())
        self._window.destroy()

    def get_inputs(self, client_uuid: str) -> Dict[str, str|int|bool]:
        """Collects variables containing the inputs and combines them in a dictionary.

        Args:
            client_uuid: Used as a nickname if none is given.

        Returns:
            inputs: Dictionary containing collected inputs.
        """
        inputs = {}
        if len(self._nickname.strip()) == 0:
            inputs["nickname"] = client_uuid[:15]
        else:
            self._nickname.encode("utf-8", "strict")  # tests for valid uft-8 name
            inputs["nickname"] = self._nickname
        inputs["ip"] = self._ip
        inputs["port"] = self._port
        inputs["be_player"] = self.be_player
        return inputs

    def _set_spectator(self) -> None:
        """Toggles "be_player" between "player" and "spectator" depending on checkbox."""
        self.be_player = not self.be_player

    @staticmethod
    def write_entry_txt(entry: tk.Entry, txt: str|int) -> None:
        """Replaces text in "entry" with "txt".

        Args:
            entry: Entrybox whose text will be replaced.
            txt: Text to be placed in "entry".
        """
        entry.delete(0, tk.END)
        entry.insert(0, txt)


class client_gui_restart():
    """Client gui used for restarting a game."""
    def __init__(self, nickname: str, be_player: bool,
                 player_colors: List[Tuple[int, int, int]], player_num: int,
                 nicknames: Dict[int, str], finish_message: Tuple[int, Dict[int, List[List[int]]]]|None) -> None:
        """Initializes the instance.

        Args:
            nickname: Nickname of the client.
            be_player: Whether the client is "player" or "spectator".
            player_colors: Colors for the players.
            player_num: Number of players.
            nicknames: Connects "player_number" to the respective player nicknames.
            finish_message: Contains the "player_number" of the winner and a dictionary
              with the information about the game evolution ("time line").
              Is None if not recieved.
        """
        self._nickname = nickname

        self._window = tk.Tk()
        self._window.title('Client GUI')
        self._window.protocol("WM_DELETE_WINDOW", self._close_window)

        self.be_player = be_player

        row = 0
        tk.Label(self._window, text="Nickname:").grid(row=row, column=0)
        self._nickname_box = tk.Entry(self._window, width=35)
        self._nickname_box.grid(row=row, column=1)
        self.write_entry_txt(self._nickname_box, self._nickname)

        row += 1
        self.spectator_cbutton = tk.Checkbutton(self._window, text='Spectator', command=self._set_spectator)
        self.spectator_cbutton.grid(row=row, column=1)
        if not self.be_player:
            self.spectator_cbutton.select()

        row += 1
        tk.Button(self._window, text='Continue', command=self._continue).grid(row=row, column=1)

        if finish_message is not None:
            row += 1
            tk.Label(self._window, text=75*"=").grid(row=row, column=0, columnspan=2)

            time_line = finish_message[1]
            winner = finish_message[0]
            row += 1
            tk.Label(self._window, text="Winner:").grid(row=row, column=0)
            tk.Label(self._window, text=f"{nicknames[winner]}").grid(row=row, column=1)

            row += 1
            frame = tk.Frame(self._window)
            frame.grid(row=row, column=0, columnspan=2)
            fig = Figure(figsize=(8,5), constrained_layout=True)
            self.make_plots(fig, time_line, player_colors, player_num, nicknames)
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
            toolbar = NavigationToolbar2Tk(canvas, frame, pack_toolbar=False)
            toolbar.update()
            toolbar.pack(anchor="w", fill=tk.X)

            screen_w = self._window.winfo_screenwidth()
            screen_h = self._window.winfo_screenheight()
            width = 830
            height = 665
            self._window.geometry(f"{width}x{height}+{int(screen_w/2-width/2)}+{int(screen_h/2-height/2)}")
        else:
            screen_w = self._window.winfo_screenwidth()
            screen_h = self._window.winfo_screenheight()
            width = 370
            height = 78
            self._window.geometry(f"{width}x{height}+{int(screen_w/2-width/2)}+{int(screen_h/2-height/2)}")

        self._window.mainloop()

    def _close_window(self) -> None:
        """Closes the window and terminates client process with "sys.exit()"."""
        self._window.destroy()
        sys.exit()

    def _continue(self) -> None:
        """If button is pressed, saves inputs in their corresponding class variables and closes window."""
        self._nickname = self._nickname_box.get()[:15]
        self._window.destroy()

    def get_inputs(self, c_inputs: Dict[str, str|int|bool],
                   client_uuid: str) -> Dict[str, str|int|bool]:
        """Collects variables containing the inputs and combines them in a dictionary.

        Args:
            c_inputs: Old inputs.
            client_uuid: Used as a nickname if none is given.

        Returns:
            c_inputs: Dictionary containing old inputs updated with newly collected inputs.
        """
        if len(self._nickname.strip()) == 0:
            c_inputs["nickname"] = client_uuid[:15]
        else:
            self._nickname.encode("utf-8", "strict")  # tests for valid uft-8 name
            c_inputs["nickname"] = self._nickname
        c_inputs["be_player"] = self.be_player
        return c_inputs

    def _set_spectator(self) -> None:
        """Toggles "be_player" between "player" and "spectator" depending on checkbox."""
        self.be_player = not self.be_player

    def make_plots(self, fig: Figure, time_line: Dict[int, List[List[int]]],
                   player_colors: List[Tuple[int, int, int]],
                   player_num: int, nicknames: Dict[int, str]) -> None:
        """Creates the plots to show the game evolution ("time line").

        Args:
            fig: Figure to add the plots to.
            time_line: Information about the game evolution ("time line").
            player_colors: Colors for the players.
            player_num: Number of players.
            nicknames: Connects "player_number" to the respective player nicknames.
        """
        x_list = []
        y_lists = {}
        y_lists1 = {}
        for num in range(player_num):
            y_lists[num] = []
            y_lists1[num] = []

        round_num = 0
        for round_num, round_counts in time_line.items():
            step = 1/len(round_counts)
            for step_num, step_counts in enumerate(round_counts):
                x_list.append(round_num + step * step_num)
                y = 0
                for num, player_count in enumerate(step_counts):
                    y_lists[num].append(player_count)
                    y += player_count
                    y_lists1[num].append(y)

        major_tick, minor_tick = self.get_spacing(round_num + 1)
        axs1 = fig.add_subplot(2, 1, 1)
        axs1.xaxis.set_major_locator(ticker.MultipleLocator(major_tick))
        axs1.xaxis.set_minor_locator(ticker.MultipleLocator(minor_tick))
        axs1.set_ylim([0, round_num+2])
        axs1.set_xlim([0, round_num+1])
        axs1.plot([0, round_num+1], [1, round_num+2], color="black", linestyle="--")
        for num in list(range(0, round_num+2, major_tick)):
            axs1.vlines(num, 0, num+1, color="lightgray", linestyle="--")
        for num in range(player_num):
            color = player_colors[num % len(player_colors)]
            axs1.plot(x_list, y_lists[num],
                        color=(color[0]/255, color[1]/255, color[2]/255),
                        label=nicknames[num])
        axs1.legend(loc="upper left")

        axs2 = fig.add_subplot(2, 1, 2)
        axs2.xaxis.set_major_locator(ticker.MultipleLocator(major_tick))
        axs2.xaxis.set_minor_locator(ticker.MultipleLocator(minor_tick))
        axs2.set_ylim([0, round_num+2])
        axs2.set_xlim([0, round_num+1])
        axs2.plot([0, round_num+1], [1, round_num+2], color="black", linestyle="--")
        for num in list(range(0, round_num+2, major_tick)):
            axs2.vlines(num, 0, num+1, color="lightgray", linestyle="--")
        y_lists1[-1] = np.zeros(len(x_list))
        for num in range(player_num):
            color = player_colors[num % len(player_colors)]
            axs2.fill_between(x_list, y_lists1[num-1], y_lists1[num],
                              color=(color[0]/255, color[1]/255, color[2]/255),
                              label=nicknames[num])
        axs2.legend(loc="upper left")

    @staticmethod
    def write_entry_txt(entry: tk.Entry, txt: str|int) -> None:
        """Replaces text in "entry" with "txt".

        Args:
            entry: Entrybox whose text will be replaced.
            txt: Text to be placed in "entry".
        """
        entry.delete(0, tk.END)
        entry.insert(0, txt)

    @staticmethod
    def get_spacing(time_line_len: int) -> Tuple[int, int]:
        """Calculates major and minor tick-spacing for x-axis.

        Args:
            time_line_len: Length of x-axis.

        Returns:
            major_tick: Major tick-spacing for x-axis.
            minor_tick: Minor tick-spacing for x-axis.
        """
        if not (time_line_len % 50 == 0):
            time_line_len += 50 - (time_line_len % 50)
        major_tick = int(time_line_len / 10)
        minor_tick = int(major_tick / 5)
        return major_tick, minor_tick


class client_quit_gui():
    """Gui for asking if pygame window should really be closed."""
    def __init__(self) -> None:
        """Initializes the instance."""
        self._window = tk.Tk()
        self._window.title('Quit')
        self._window.protocol("WM_DELETE_WINDOW", self._close_window)
        self.quit = False

        row = 0
        tk.Label(self._window, text="Do you really want to quit?").grid(row=row, column=0)

        row += 1
        tk.Button(self._window, text='Yes', command=self._do_quit).grid(row=row, column=0)
        tk.Button(self._window, text='No', command=self._not_quit).grid(row=row, column=1)

        screen_w = self._window.winfo_screenwidth()
        screen_h = self._window.winfo_screenheight()
        width = 244
        height = 54
        self._window.geometry(f"{width}x{height}+{int(screen_w/2-width/2)}+{int(screen_h/2-height/2)}")

        self._window.mainloop()

    def _close_window(self) -> None:
        """Closes the window."""
        self._window.destroy()

    def _not_quit(self) -> None:
        """If the button is pressed then the window is closed and the pygame window will not be closed."""
        self.quit = False
        self._window.destroy()

    def _do_quit(self) -> None:
        """If the button is pressed then the window is closed and the pygame window will also be closed."""
        self.quit = True
        self._window.destroy()

    def get_input(self) -> bool:
        """Returns wether the pygame window should be closed or not."""
        return self.quit


if __name__ == "__main__":
    pass
    # c_gui = client_gui()
    # c_inputs = c_gui.get_inputs()
    # quit_gui = client_quit_gui()
    # print(quit_gui.quit())
