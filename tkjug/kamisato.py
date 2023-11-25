from datetime import datetime, timedelta
import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk
from tkjug.useredis import kamisato_data
from tkjug.plot import Plot
from tkjug.table import Mtable


colors = {
    # cyborg
    'primary': '#0da3de',
    'secondary': '#5e5e5e',
    'success': '#68be0d',
    'info': '#ad0dd4',
    'warning': '#ff890d',
    'danger': '#df0d0d',
    'foreground': '#ffffff',
    'light': '#2d2d2d',
    'dark': '#b1b3b2',
    'background': '#060606'
}

bg = colors['background']
fg = colors['foreground']


def sequences_of_machine() -> tuple:
    seq1 = ['1001'] + [str(n) for n in reversed(range(787, 796))]  # im
    seq2 = [str(n) for n in reversed(range(758, 776))]  # im
    seq3 = [str(n) for n in range(750, 758)]  # im
    seq4 = [str(n) for n in reversed(range(993, 1001))]  # my
    seq5 = [str(n) for n in range(969, 977)]  # my
    seq6 = [str(n) for n in range(776, 784)]  # go
    return seq1, seq2, seq3, seq4, seq5, seq6

def _func(*args):
    dt, df1, df2, df3 = args
    cc_df = pd.concat([df1, df2, df3], axis=0)
    df = cc_df[cc_df['date'] == dt]
    im_df = df1[df1['date'] == dt]
    my_df = df2[df2['date'] == dt]
    go_df = df3[df3['date'] == dt]

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

    go_games_mean = go_df['games'].mean()
    go_rate = go_df['saf'].sum() / go_df['out'].sum()
    go_reg = go_df['games'].sum() / go_df['rb'].sum()
    go_balance = go_df['saf'].sum() - go_df['out'].sum()

    data = [out, out_mean, games_mean, rate, balance]
    data += [im_games_mean, im_rate, im_reg, im_balance]
    data += [my_games_mean, my_rate, my_reg, my_balance]
    data += [go_games_mean, go_rate, go_reg, go_balance]

    index = ['TotalOut', 'MeanOut', 'Games', 'Rate', 'Balance']
    index += ['iGames', 'iRate', 'iReg', 'iBalance']
    index += ['mGames', 'mRate', 'mReg', 'mBalance']
    index += ['gGames', 'gRate', 'gReg', 'gBalance']
    
    return pd.Series(data, index=index)


class Kamisato(tk.Frame):
    def __init__(self, *args, master=None):
        super().__init__(master)
        self.pack()
        # self.master.protocol('WM_DELETE_WINDOW', self._destroyWindow)
        self.sug_d, self.im_df, self.my_df, self.go_df = args

        self.master.geometry('+128+128')
        self.frame = ttk.Frame(self, style='c.TFrame')
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.var_dt = tk.StringVar()
        self.var_sug = tk.StringVar()
        self.summary_vars = [tk.StringVar(value='') for _ in range(17)]

        self.varables_d = {}
        seqs = sequences_of_machine()
        for seq in seqs:
            for s in seq:
                t = tk.StringVar(value=''), tk.StringVar(value=''), tk.StringVar(value='')
                self.varables_d |= {s: t}

        self.lbl_game_d = {}
        self.lbl_reg_d = {}
        self.lbl_bal_d = {}

        self.dates = sorted(set(self.sug_d.keys()))
        self.date = self.dates[-1]

        self.heading()
        self.date_suggestion()
        self.buttons()
        self.tables()
        self.footer()

        self.set_data(self.date)

    def _destroyWindow(self):
        self.master.quit()
        self.master.destroy()

    def heading(self):
        hall = 'Kamisato'
        h2 = 'Arial', 24
        frame1 = ttk.Frame(self.frame, style='c.TFrame')
        frame1.pack(expand=True, fill=tk.BOTH, padx=32, pady=16)
        label = ttk.Label(frame1, text=hall, style='c.TLabel', font=h2)
        label.pack(expand=True, fill=tk.BOTH)
        separator = ttk.Separator(frame1, orient='horizontal', style='c.TSeparator')
        separator.pack(expand=True, fill=tk.BOTH)

    def date_suggestion(self):
        h3 = 'Arial', 16
        frame2 = ttk.Frame(self.frame, style='c.TFrame')
        frame2.pack(expand=True, fill=tk.X, padx=32)
        label = ttk.Label(frame2, textvariable=self.var_dt, style='c.TLabel', font=h3, anchor=tk.W)
        label.pack(side=tk.LEFT)
        label = ttk.Label(frame2, textvariable=self.var_sug, style='c.TLabel', font=h3, anchor=tk.W)
        label.pack(side=tk.LEFT, padx=16)      

    def buttons(self):
        frame3 = ttk.Frame(self.frame, style='c.TFrame')
        frame3.pack(expand=True, fill=tk.BOTH, padx=32, pady=8)
        btn = ttk.Button(frame3, text='next day', style='c.TButton', command=self.next_day())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)
        btn = ttk.Button(frame3, text='prev day', style='c.TButton', command=self.prev_day())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)
        btn = ttk.Button(frame3, text='Im plot', style='c.TButton', command=self.implot())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)
        btn = ttk.Button(frame3, text='My plot', style='c.TButton', command=self.myplot())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)
        btn = ttk.Button(frame3, text='montly table', style='c.TButton', command=self.mtable())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)

    def tables(self):
        frame = ttk.Frame(self.frame, style='c.TFrame')
        frame.pack(expand=True, fill=tk.BOTH, padx=16)

        self.set_summary_vars(self.date)
        self.summary(frame)

        seqs = sequences_of_machine()

        frm1 = ttk.Frame(frame, style='c.TFrame')
        frm1.pack(side=tk.LEFT, anchor=tk.NW)
        self.sub_table(frm1, seqs[0], 'Imjuggler')
        self.sub_table(frm1, seqs[5], 'goJuggler')

        frm2 = ttk.Frame(frame, style='c.TFrame')
        frm2.pack(side=tk.LEFT, anchor=tk.NW)
        self.sub_table(frm2, seqs[1], 'ImJuggler')

        frm3 = ttk.Frame(frame, style='c.TFrame')
        frm3.pack(side=tk.LEFT, anchor=tk.NW)
        self.sub_table(frm3, seqs[2], 'ImJuggler')

        frm4 = ttk.Frame(frame, style='c.TFrame')
        frm4.pack(side=tk.LEFT, anchor=tk.N)
        self.sub_table(frm4, seqs[3], 'myJuggler')

        frm5 = ttk.Frame(frame, style='c.TFrame')
        frm5.pack(anchor=tk.NW)
        self.sub_table(frm5, seqs[4], 'myJuggler')

    def set_summary_vars(self, dt):
        sr = _func(dt, self.im_df, self.my_df, self.go_df)
        for var, (key, item) in zip(self.summary_vars, sr.items()):
            if key in ['Rate', 'iRate', 'mRate', 'gRate']:
                value = round(item, 3)
            else:
                value = round(item, 1)
            var.set(str(value))

    def summary(self, frame: ttk.Frame):
        h3 = 'Arial', 16
        index = ['TotalOut', 'MeanOut', 'Games', 'Rate', 'Balance']
        index += ['iGames', 'iRate', 'iReg', 'iBalance']
        index += ['mGames', 'mRate', 'mReg', 'mBalance']
        index += ['gGames', 'gRate', 'gReg', 'gBalance']
        frm_sum = ttk.Frame(frame, style='c.TFrame')
        frm_sum.pack(side=tk.LEFT, anchor=tk.NW)
        lbl = ttk.Label(frm_sum, text='Summary', style='c.TLabel', font=h3)
        lbl.pack(anchor=tk.W, padx=16, pady=4)
        for idx, var in zip(index, self.summary_vars):
            frm = ttk.Frame(frm_sum, style='c.TFrame')
            frm.pack(padx=16)
            lbl1 = ttk.Label(frm, text=idx, width=10, style='c.TLabel', anchor=tk.W)
            lbl1.pack(side=tk.LEFT)
            lbl2 = ttk.Label(frm, textvariable=var, width=12, style='c.TLabel', anchor=tk.E)
            lbl2.pack(side=tk.LEFT)
            if idx == 'Games':
                lbl2.configure(foreground=colors['primary'])
            if idx in ['Rate', 'iRate', 'mRate']:
                lbl2.configure(foreground=colors['danger'])
            if idx in ['iReg', 'mReg']:
                lbl2.configure(foreground=colors['warning'])

    def sub_table(self, frame: ttk.Frame, seq: list, name: str):
        h3 = 'Arial', 16
        lbl = ttk.Label(frame, text=name, style='c.TLabel', font=h3)
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
        suggestion = self.sug_d[dt]
        self.var_sug.set(suggestion)
        imdf = self.im_df[self.im_df['date'] == dt]
        mydf = self.my_df[self.my_df['date'] == dt]
        godf = self.go_df[self.go_df['date'] == dt]
        df = pd.concat([imdf, mydf, godf], axis=0)
        self.zodai()
        for _, rows in df.iterrows():
            seq = rows['no']
            var_game, var_reg, var_bal = self.varables_d[seq]
            games = rows['games']
            var_game.set(str(games))
            rb = int(games / rows['rb']) if rows['rb'] else games
            var_reg.set(str(rb))
            bal = int(rows['saf'] - rows['out'])
            var_bal.set(str(bal))

            color = colors['primary'] if games >= 5000 else fg
            self.lbl_game_d[seq].configure(foreground=color)
            color = colors['warning'] if games >= 2500 and rb < 300 else fg
            self.lbl_reg_d[seq].configure(foreground=color)
            color = colors['danger'] if bal >= 2000 else fg
            self.lbl_bal_d[seq].configure(foreground=color)

    def zodai(self):
        for seq in ['787', '788']:
            var_game, var_reg, var_bal = self.varables_d[seq]
            var_game.set('')
            var_reg.set('')
            var_bal.set('')

    def prev_day(self):
        def func():
            i = self.dates.index(self.date)
            if i == 0:
                print('No!')
            else:
                self.date = self.dates[i - 1]
                self.set_summary_vars(self.date)
                self.set_data(self.date)
        return func

    def next_day(self):
        def func():
            i = self.dates.index(self.date)
            if i == len(self.dates) - 1:
                print('No!')
            else:
                self.date = self.dates[i + 1]
                self.set_summary_vars(self.date)
                self.set_data(self.date)
        return func

    def implot(self):
        def func():
            df = self.im_df.copy()

            root = tk.Toplevel(self)
            app = Plot(df, 11, 'Kamisato ImJuggler', master=root)
            app.mainloop()
        return func

    def myplot(self):
        def func():
            df = self.my_df.copy()
            root = tk.Toplevel(self)
            app = Plot(df, 11, 'Kamisato MyJuggler', master=root)
            app.mainloop()
        return func

    def mtable(self):
        def func():
            df = self.my_df.copy()
            root = tk.Toplevel(self)
            app = Mtable(df, master=root)
            app.mainloop()
        return func


if __name__ == '__main__':
    from tkjug.tkapp import Theme
    sug, im, my, go = kamisato_data()
    root = tk.Tk()
    _ = Theme(root)
    app = Kamisato(sug, im, my, go, master=root)
    app.mainloop()