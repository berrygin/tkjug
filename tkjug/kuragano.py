from datetime import datetime, timedelta
import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk
from tkjug.useredis import kuragano_data

bg = '#0f2537'
fg = '#ebebeb'
orange = '#df6919'
green = '#5cb85c'
blue = '#5bc0de'
yellow = '#ffc107'
red = '#d9534f'

def sequences_of_machine() -> tuple:
    seq1 = [str(n) for n in reversed(range(744, 761))]
    seq2 = [str(n) for n in range(721, 738)] + ['700']
    seq3 = [str(n) for n in reversed(range(711, 721))]
    seq4 = [str(n) for n in range(681, 691)]
    return seq1, seq2, seq3, seq4

def _func(*args):
    dt, df1, df2 = args
    cc_df = pd.concat([df1, df2], axis=0)
    df = cc_df[cc_df['date'] == dt]
    im_df = df1[df1['date'] == dt]
    my_df = df2[df2['date'] == dt]

    out = df['out'].sum()
    out_mean = df['out'].mean()
    games_mean = df['games'].mean()
    rate = df['saf'].sum() / df['out'].sum()
    balance = df['saf'].sum() - df['out'].sum()

    im_games_mean = im_df['games'].mean()
    im_rate = im_df['saf'].sum() / im_df['out'].sum()
    im_reg = im_df['games'].sum() / im_df['rb'].sum()
    im_balance = im_df['saf'].sum() - im_df['out'].sum()

    my_games_mean = my_df['games'].mean()
    my_rate = my_df['saf'].sum() / my_df['out'].sum()
    my_reg = my_df['games'].sum() / my_df['rb'].sum()
    my_balance = my_df['saf'].sum() - my_df['out'].sum()

    data = [out, out_mean, games_mean, rate, balance]
    data += [im_games_mean, im_rate, im_reg, im_balance]
    data += [my_games_mean, my_rate, my_reg, my_balance]

    index = ['TotalOut', 'MeanOut', 'Games', 'Rate', 'Balance']
    index += ['iGames', 'iRate', 'iReg', 'iBalance']
    index += ['mGames', 'mRate', 'mReg', 'mBalance']
    
    return pd.Series(data, index=index)


class Kuragano(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.master.geometry('+128+128')
        self.frame = ttk.Frame(self, style='c.TFrame')
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.h2 = 'Arial', 24
        self.h3 = 'Arial', 16

        self.suggestion_d, self.im_df, self.my_df = kuragano_data()

        self.lbl_game_d = {}
        self.lbl_reg_d = {}
        self.lbl_bal_d = {}

        self.varables_d = {}
        seqs = sequences_of_machine()
        for seq in seqs:
            for s in seq:
                t = tk.StringVar(value=''), tk.StringVar(value=''), tk.StringVar(value='')
                self.varables_d |= {s: t}

        self.dates = sorted(set(self.suggestion_d.keys()))
        self.date = self.dates[-1]

        self.var_dt = tk.StringVar()
        self.var_sug = tk.StringVar()
        self.summary_vars = [tk.StringVar(value='') for _ in range(13)]

        self.heading()
        self.date_suggestion()
        self.buttons()
        self.tables()
        self.footer()

        self.set_data(self.date)

    def heading(self):
        frame1 = ttk.Frame(self.frame, style='c.TFrame')
        frame1.pack(expand=True, fill=tk.BOTH, padx=32, pady=16)
        label = ttk.Label(frame1, text='Kuragano', style='c.TLabel', font=self.h2)
        label.pack(expand=True, fill=tk.BOTH)
        separator = ttk.Separator(frame1, orient='horizontal', style='c.TSeparator')
        separator.pack(expand=True, fill=tk.BOTH)

    def date_suggestion(self):
        frame2 = ttk.Frame(self.frame, style='c.TFrame')
        frame2.pack(expand=True, fill=tk.X, padx=32)
        label = ttk.Label(frame2, textvariable=self.var_dt, style='c.TLabel', font=self.h3, anchor=tk.W)
        label.pack(side=tk.LEFT)
        label = ttk.Label(frame2, textvariable=self.var_sug, style='light.TLabel', font=self.h3, anchor=tk.W)
        label.pack(side=tk.LEFT, padx=16)      

    def buttons(self):
        frame3 = ttk.Frame(self.frame, style='c.TFrame')
        frame3.pack(expand=True, fill=tk.BOTH, padx=32, pady=8)
        btn = ttk.Button(frame3, text='next day', style='c.TButton', command=self.next_())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)
        btn = ttk.Button(frame3, text='prev day', style='c.TButton', command=self.prev_())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)
        btn = ttk.Button(frame3, text='monthly table', style='c.TButton', command=self.prev_())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)
        btn = ttk.Button(frame3, text='monthly plot', style='c.TButton', command=self.prev_())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)

    def tables(self):
        frame = ttk.Frame(self.frame, style='c.TFrame')
        frame.pack(expand=True, fill=tk.BOTH, padx=16)

        self.set_summary_vars(self.date)
        self.summary(frame)

        seqences = sequences_of_machine()

        frm1 = ttk.Frame(frame, style='c.TFrame')
        frm1.pack(side=tk.LEFT, anchor=tk.NW)
        self.sub_table(frm1, seqences[0], 'Imjuggler')

        frm2 = ttk.Frame(frame, style='c.TFrame')
        frm2.pack(side=tk.LEFT, anchor=tk.NW)
        self.sub_table(frm2, seqences[1], 'ImJuggler')

        frm3 = ttk.Frame(frame, style='c.TFrame')
        frm3.pack(side=tk.LEFT, anchor=tk.NW)
        self.sub_table(frm3, seqences[2], 'myJuggler')

        frm4 = ttk.Frame(frame, style='c.TFrame')
        frm4.pack(side=tk.LEFT, anchor=tk.NW)
        self.sub_table(frm4, seqences[3], 'myJuggler')

    def set_summary_vars(self, dt):
        sr = _func(dt, self.im_df, self.my_df)
        for var, (key, item) in zip(self.summary_vars, sr.items()):
            if key in ['Rate', 'iRate', 'mRate']:
                value = round(item, 3)
            else:
                value = round(item, 1)
            var.set(str(value))

    def summary(self, frame: ttk.Frame):
        index = ['TotalOut', 'MeanOut', 'Games', 'Rate', 'Balance']
        index += ['iGames', 'iRate', 'iReg', 'iBalance']
        index += ['mGames', 'mRate', 'mReg', 'mBalance']
        frm_sum = ttk.Frame(frame, style='c.TFrame')
        frm_sum.pack(side=tk.LEFT, anchor=tk.NW)
        h3_font = 'Arial', 16
        lbl = ttk.Label(frm_sum, text='Summary', style='c.TLabel', font=h3_font)
        lbl.pack(anchor=tk.W, padx=16, pady=4)
        for idx, var in zip(index, self.summary_vars):
            frm = ttk.Frame(frm_sum, style='c.TFrame')
            frm.pack(padx=16)
            lbl1 = ttk.Label(frm, text=idx, width=10, style='c.TLabel', anchor=tk.W)
            lbl1.pack(side=tk.LEFT)
            lbl2 = ttk.Label(frm, textvariable=var, width=12, style='c.TLabel', anchor=tk.E)
            lbl2.pack(side=tk.LEFT)
            if idx in ['Rate', 'iRate', 'mRate']:
                lbl2.configure(foreground=yellow)
            if idx in ['iReg', 'mReg']:
                lbl2.configure(foreground=blue)

    def sub_table(self, frame: ttk.Frame, seq: list, name: str):
        h3_font = 'Arial', 16
        lbl = ttk.Label(frame, text=name, style='light.TLabel', font=h3_font)
        lbl.pack(anchor=tk.W, padx=16, pady=4)
        for s in seq:
            frm = ttk.Frame(frame, style='c.TFrame')
            frm.pack(padx=16)
            lbl = ttk.Label(frm, text=s, style='green.TLabel', width=4)
            lbl.pack(side=tk.LEFT)
            games, reg, balance = self.varables_d[s]
            lbl1 = ttk.Label(frm, textvariable=games, style='c.TLabel', width=4, anchor=tk.E)
            lbl1.pack(side=tk.LEFT)
            lbl2 = ttk.Label(frm, textvariable=reg, style='c.TLabel', width=4, anchor=tk.E)
            lbl2.pack(side=tk.LEFT)
            lbl3 = ttk.Label(frm, textvariable=balance, style='c.TLabel', width=4, anchor=tk.E)
            lbl3.pack(side=tk.LEFT)
            self.lbl_game_d[s] = lbl1
            self.lbl_reg_d[s] = lbl2
            self.lbl_bal_d[s] = lbl3

    def footer(self):
        # spacing only
        ttk.Frame(self.frame, style='c.TFrame').pack(pady=16)

    def set_data(self, dt):

        dt_s = datetime.strftime(dt, '%Y/%m/%d')
        self.var_dt.set(dt_s)
        suggestion = self.suggestion_d[dt]
        self.var_sug.set(suggestion)

        idf = self.im_df[self.im_df['date'] == dt]
        mdf = self.my_df[self.my_df['date'] == dt]
        df = pd.concat([idf, mdf], axis=0)
        for _, rows in df.iterrows():
            seq = rows['no']
            var_games, var_reg, var_balance = self.varables_d[seq]
            games = rows['games']
            var_games.set(str(games))
            rb = int(games / rows['rb']) if rows['rb'] else games
            var_reg.set(str(rb))
            bal = int(rows['saf'] - rows['out'])
            var_balance.set(str(bal))

            color = red if games >= 5000 else fg
            self.lbl_game_d[seq].configure(foreground=color)
            color = orange if games >= 2500 and rb < 300 else fg
            self.lbl_reg_d[seq].configure(foreground=color)
            color = yellow if bal >= 2000 else fg
            self.lbl_bal_d[seq].configure(foreground=color)

    def prev_(self):
        def func():
            i = self.dates.index(self.date)
            if i == 0:
                print('No!')
            else:
                self.date = self.dates[i - 1]
                self.set_summary_vars(self.date)
                self.set_data(self.date)
        return func

    def next_(self):
        def func():
            i = self.dates.index(self.date)
            if i == len(self.dates) - 1:
                print('No!')
            else:
                self.date = self.dates[i + 1]
                self.set_summary_vars(self.date)
                self.set_data(self.date)
        return func

if __name__ == '__main__':
    from tkjug.tkapp import Superhero
    root = tk.Tk()
    _ = Superhero(root)
    app = Kuragano(root)
    app.mainloop()

    

