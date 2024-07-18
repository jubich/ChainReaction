#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import socket

import tkinter as tk
import numpy as np
import matplotlib
import matplotlib.ticker as ticker
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


matplotlib.use('Agg')



class client_gui():
    def __init__(self, nickname=None, ip=None, port=None, be_player=True):
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

    def _close_window(self):
        self._window.destroy()
        sys.exit()

    def _continue(self):
        self._nickname = self._nickname_box.get()[:15]
        self._ip = self._ip_box.get()
        socket.inet_pton(socket.AF_INET, self._ip)  # tests for valid ip4
        self._port = int(self._port_box.get())
        self._window.destroy()

    def get_inputs(self, client_uuid):
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

    def _set_spectator(self):
        self.be_player = not self.be_player

    @staticmethod
    def write_entry_txt(entry, txt):
        entry.delete(0, tk.END)
        entry.insert(0, txt)


class client_gui_restart():
    def __init__(self, nickname, be_player, player_colors, player_num,
                 nicknames, finish_message):
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

    def _close_window(self):
        self._window.destroy()
        sys.exit()

    def _continue(self):
        self._nickname = self._nickname_box.get()[:15]
        self._window.destroy()

    def get_inputs(self, c_inputs, client_uuid):
        if len(self._nickname.strip()) == 0:
            c_inputs["nickname"] = client_uuid[:15]
        else:
            self._nickname.encode("utf-8", "strict")  # tests for valid uft-8 name
            c_inputs["nickname"] = self._nickname
        c_inputs["be_player"] = self.be_player
        return c_inputs

    def _set_spectator(self):
        self.be_player = not self.be_player

    def make_plots(self, fig, time_line, player_colors, player_num, nicknames):
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

        major_tick, minor_tick = self.get_spacing(round_num)
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
    def write_entry_txt(entry, txt):
        entry.delete(0, tk.END)
        entry.insert(0, txt)

    @staticmethod
    def get_spacing(time_line_len):
        if not (time_line_len % 50 == 0):
            time_line_len += 50 - (time_line_len % 50)
        major_tick = int(time_line_len / 10)
        minor_tick = int(major_tick / 5)
        return major_tick, minor_tick


class client_quit_gui():
    def __init__(self):

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
