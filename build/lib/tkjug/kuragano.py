import tkinter as tk
import tkinter.ttk as ttk


class Kuragano(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.master.geometry('+100+100')
        frame = ttk.Frame(self, style='c.TFrame')
        frame.pack(expand=True, fill=tk.BOTH)

        frame1 = ttk.Frame(frame, style='c.TFrame')
        frame1.pack(expand=True, fill=tk.BOTH, padx=16, pady=16)
        ttk.Label(frame1, text='black', style='c.TLabel').pack()
