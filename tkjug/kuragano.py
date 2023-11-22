from datetime import datetime, timedelta
import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk
from tkjug.useredis import kuragano_data


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

        self.suggestion_d, self.im_df, self.my_df = kuragano_data()

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
        self.info()
        self.buttons()
        self.tables()
        self.footer()

        self.set_data(self.date)

    def heading(self):
        frame1 = ttk.Frame(self.frame, style='c.TFrame')
        frame1.pack(expand=True, fill=tk.BOTH, pady=16)
        h3_font = 'Arial', 16
        label = ttk.Label(frame1, text='Hall KURAGANO', style='c.TLabel', font=h3_font)
        label.pack(expand=True, fill=tk.BOTH, padx=16)
        separator = ttk.Separator(frame1, orient='horizontal', style='c.TSeparator')
        separator.pack(expand=True, fill=tk.BOTH, padx=16)

    def info(self):
        frame2 = ttk.Frame(self.frame, style='c.TFrame')
        frame2.pack(expand=True, fill=tk.X, padx=32)
        label = ttk.Label(frame2, textvariable=self.var_dt, style='c.TLabel', anchor=tk.W)
        label.pack(side=tk.LEFT)
        label = ttk.Label(frame2, textvariable=self.var_sug, style='c.TLabel', anchor=tk.W)
        label.pack(side=tk.LEFT)      

    def buttons(self):
        frame3 = ttk.Frame(self.frame, style='c.TFrame')
        frame3.pack(expand=True, fill=tk.BOTH, padx=32)
        btn = ttk.Button(frame3, text='next day', style='c.TButton', command=self.next_())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)
        btn = ttk.Button(frame3, text='prev day', style='c.TButton', command=self.prev_())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)
        btn = ttk.Button(frame3, text='monthly table', style='c.TButton', command=self.prev_())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)
        btn = ttk.Button(frame3, text='monthly plot', style='c.TButton', command=self.prev_())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)
        ttk.Frame(frame3, style='c.TFrame').pack(pady=32)

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
            frm = tk.Frame(frm_sum)
            frm.pack(padx=16)
            lbl = ttk.Label(frm, text=idx, width=8, anchor=tk.W)
            lbl.pack(side=tk.LEFT)
            lbl = ttk.Label(frm, textvariable=var, width=8, anchor=tk.E)
            lbl.pack(side=tk.LEFT)

    def footer(self):
        ttk.Frame(self.frame, style='c.TFrame').pack(pady=16)

    def sub_table(self, frame: ttk.Frame, seq: list, name: str):
        h3_font = 'Arial', 16
        lbl = ttk.Label(frame, text=name, style='c.TLabel', font=h3_font)
        lbl.pack(anchor=tk.W, padx=16, pady=4)
        for s in seq:
            frm = tk.Frame(frame)
            frm.pack(padx=16)
            lbl = ttk.Label(frm, text=s, width=4)
            lbl.pack(side=tk.LEFT)
            t = self.varables_d[s]
            lbl = ttk.Label(frm, textvariable=t[0], width=4, anchor=tk.E)
            lbl.pack(side=tk.LEFT)
            lbl = ttk.Label(frm, textvariable=t[1], width=4, anchor=tk.E)
            lbl.pack(side=tk.LEFT)
            lbl = ttk.Label(frm, textvariable=t[2], width=4, anchor=tk.E)
            lbl.pack(side=tk.LEFT)

    def set_data(self, dt):
        dt_s = datetime.strftime(dt, '%Y/%m/%d')
        self.var_dt.set(dt_s)
        suggestion = self.suggestion_d[dt]
        self.var_sug.set(suggestion)

        df = self.im_df[self.im_df['date'] == dt]
        for _, rows in df.iterrows():
            v_games, v_reg, v_balance = self.varables_d[rows['no']]
            games = rows['games']
            v_games.set(str(games))
            rb = int(games / rows['rb']) if rows['rb'] else games
            v_reg.set(str(rb))
            bln = int(rows['saf'] - rows['out'])
            v_balance.set(str(bln))
        # im = last_day(self.im_df)
        # print(im.head())
        self.next_()

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
    # sugd, imdf, mydf = kuragano_data()
    # print(mydf.head())
    

