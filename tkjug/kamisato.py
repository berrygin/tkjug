from datetime import datetime, timedelta
import holidays
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

summary_keys = ['TotalOut', 'Out', 'Games', 'Rate', 'Balance',
                'imGames', 'imRate', 'imReg', 'imBal',
                'myGames', 'myRate', 'myReg', 'myBal']

def calc(dt, df1, df2):
    # dt, df1, df2 = args
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

    values = [out, out_mean, games_mean, rate, balance,
                im_games_mean, im_rate, im_reg, im_balance,
                my_games_mean, my_rate, my_reg, my_balance]

    return dict(zip(summary_keys, values))


class Hall(tk.Frame):
    def __init__(self, *args, master=None):
        super().__init__(master)
        self.pack()
        # self.master.protocol('WM_DELETE_WINDOW', self._destroyWindow)
        self.hall = 'Kamisato'
        self.args = args  # sug_d, im_df, my_df, (go_df)
        self.sug_d = args[0]

        self.master.geometry('+64+64')
        frame = ttk.Frame(self, style='c.TFrame')
        frame.pack(expand=True, fill=tk.BOTH)
        self.upper_frame = ttk.Frame(frame, style='c.TFrame')
        self.upper_frame.pack(expand=True, fill=tk.BOTH, padx=16)
        self.lower_frame = ttk.Frame(frame, style='c.TFrame')
        self.lower_frame.pack(expand=True, fill=tk.BOTH, padx=16)

        self.dates = sorted(self.sug_d.keys())
        dt = self.dates[-1]
        self.dt = dt
        self.dt_v = tk.StringVar(value='')
        self.weekday_v = tk.StringVar(value='')
        self.sug_v = tk.StringVar(value='')

        variables = [tk.StringVar(value='') for _ in range(len(summary_keys))]
        self.summary_d = dict(zip(summary_keys, variables))

        self.varables_d = {}
        seqs = self.sequences_of_machine()
        for seq in seqs:
            for s in seq:
                t = tk.StringVar(value=''), tk.StringVar(value=''), tk.StringVar(value='')
                self.varables_d |= {s: t}
        self.label_d = {}

        self.heading()
        self.date_sug()
        self.buttons()
        self.summary()
        self.machine_layout()
        self.footer_space()

        self.update_date_sug(dt)
        self.update_summary(dt)
        self.update_island(dt)

    def _destroyWindow(self):
        self.master.quit()
        self.master.destroy()

    def heading(self):
        hall = self.hall
        h2 = 'Arial', 24
        frame1 = ttk.Frame(self.upper_frame, style='c.TFrame')
        frame1.pack(expand=True, fill=tk.BOTH, padx=16, pady=16)
        label = ttk.Label(frame1, text=hall, style='c.TLabel', font=h2)
        label.pack(expand=True, fill=tk.BOTH)
        separator = ttk.Separator(frame1, orient='horizontal', style='c.TSeparator')
        separator.pack(expand=True, fill=tk.BOTH)

    def date_sug(self):
        h3 = 'Arial', 16
        frame = ttk.Frame(self.upper_frame, style='c.TFrame')
        frame.pack(expand=True, fill=tk.X, padx=16)
        label = ttk.Label(frame, textvariable=self.dt_v, style='c.TLabel', font=h3, anchor=tk.W)
        label.pack(side=tk.LEFT)
        self.label_wk = ttk.Label(frame, textvariable=self.weekday_v, style='c.TLabel', width=4, font=h3, anchor=tk.CENTER)
        self.label_wk.pack(side=tk.LEFT)
        label = ttk.Label(frame, textvariable=self.sug_v, style='c.TLabel', font=h3, anchor=tk.W)
        label.pack(side=tk.LEFT)    

    def update_date_sug(self, dt):
        dt_s = datetime.strftime(dt, '%Y/%m/%d')
        self.dt_v.set(dt_s)
        i = dt.weekday()
        d = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat',6: 'sun'}
        self.weekday_v.set(d[i])
        if dt in holidays.JP() or dt.weekday() > 4:
            self.label_wk.configure(foreground=colors['warning'])
        else:
            self.label_wk.configure(foreground=colors['foreground'])
        sug = self.sug_d[dt]
        self.sug_v.set(sug)

    def buttons(self):
        frame3 = ttk.Frame(self.upper_frame, style='c.TFrame')
        frame3.pack(expand=True, fill=tk.BOTH, padx=16, pady=8)
        btn = ttk.Button(frame3, text='next day', style='c.TButton', command=self.next_day())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)
        btn = ttk.Button(frame3, text='prev day', style='c.TButton', command=self.prev_day())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)
        btn = ttk.Button(frame3, text='im plot', style='c.TButton', command=self.implot())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)
        btn = ttk.Button(frame3, text='my plot', style='c.TButton', command=self.myplot())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)
        btn = ttk.Button(frame3, text='montly table', style='c.TButton', command=self.mtable())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)

    def summary(self):
        summary_frame = ttk.Frame(self.lower_frame, style='c.TFrame')
        summary_frame.pack(side=tk.LEFT, anchor=tk.NW)
        h3 = 'Arial', 16
        lbl = ttk.Label(summary_frame, text='Summary', style='c.TLabel', font=h3)
        lbl.pack(anchor=tk.W, padx=16)
        for key, variable in self.summary_d.items():
            frame = ttk.Frame(summary_frame, style='c.TFrame')
            frame.pack(padx=16, pady=1)
            lbl1 = ttk.Label(frame, text=key, width=10, style='c.TLabel', anchor=tk.W)
            lbl1.pack(side=tk.LEFT)
            lbl2 = ttk.Label(frame, textvariable=variable, width=12, style='c.TLabel', anchor=tk.E)
            lbl2.pack(side=tk.LEFT)
            if key == 'Games':
                lbl2.configure(foreground=colors['primary'])
            if key.endswith('Rate'):
                lbl2.configure(foreground=colors['danger'])
            if key.endswith('Reg'):
                lbl2.configure(foreground=colors['warning'])

    def update_summary(self, dt):
        d = calc(dt, *self.args[1:3])
        for key, value in d.items():
            if key.endswith('Rate'):
                s = str(round(value, 3))
            else:
                s = str(round(value, 1))
            self.summary_d[key].set(s)

    def island(self, frame: ttk.Frame, machine_list: list, machine_name: str):
        h3 = 'Arial', 16
        label = ttk.Label(frame, text=machine_name, style='c.TLabel', font=h3)
        label.pack(anchor=tk.W, padx=16, pady=4)

        for machine_no in machine_list:
            frm = ttk.Frame(frame, style='c.TFrame')
            frm.pack(padx=16)
            lbl_no = ttk.Label(frm, text=machine_no, style='green.TLabel', width=4)
            lbl_no.pack(side=tk.LEFT)
            game, reg, balance = self.varables_d[machine_no]
            lbl_game = ttk.Label(frm, textvariable=game, style='c.TLabel', width=4, anchor=tk.E)
            lbl_game.pack(side=tk.LEFT)
            lbl_reg = ttk.Label(frm, textvariable=reg, style='c.TLabel', width=4, anchor=tk.E)
            lbl_reg.pack(side=tk.LEFT)
            lbl_bal = ttk.Label(frm, textvariable=balance, style='c.TLabel', width=5, anchor=tk.E)
            lbl_bal.pack(side=tk.LEFT)
            self.label_d[machine_no] = lbl_game, lbl_reg, lbl_bal

    def update_island(self, dt):
        dfs = [df[df['date']==dt] for df in self.args[1:]]
        df = pd.concat(dfs, axis=0)
        # reset
        for values in self.varables_d.values():
            for var in values:
                var.set('')
        # draw
        for _, rows in df.iterrows():
            machine_no = rows['no']
            games = rows['games']
            game, reg, balance = self.varables_d[machine_no]
            game.set(str(games))
            rb_rate = int(games / rows['rb']) if rows['rb'] else float('NaN')
            reg.set(str(rb_rate))
            bal = int(rows['saf'] - rows['out'])
            balance.set(str(bal))

            color = colors['primary'] if games >= 5000 else colors['foreground']
            self.label_d[machine_no][0].configure(foreground=color)
            color = colors['warning'] if games >= 2500 and rb_rate < 300 else colors['foreground']
            self.label_d[machine_no][1].configure(foreground=color)
            color = colors['dark'] if pd.isna(rb_rate) else colors['foreground']
            self.label_d[machine_no][1].configure(foreground=color)
            color = colors['danger'] if bal >= 2000 else colors['foreground']
            self.label_d[machine_no][2].configure(foreground=color)


    def footer_space(self):
        ttk.Frame(self.lower_frame, style='c.TFrame').pack(pady=16)

    def prev_day(self):
        def func():
            i = self.dates.index(self.dt)
            if i == 0:
                print('No!')
            else:
                dt = self.dates[i - 1]
                self.dt = dt
                self.update_date_sug(dt)
                self.update_summary(dt)
                self.update_island(dt)
        return func

    def next_day(self):
        def func():
            i = self.dates.index(self.dt)
            if i == len(self.dates) - 1:
                print('No!')
            else:
                dt = self.dates[i + 1]
                self.dt = dt
                self.update_summary(dt)
                self.update_date_sug(dt)
                self.update_island(dt)
        return func

    def implot(self):
        def func():
            im_df = self.args[1].copy()
            root = tk.Toplevel(self)
            app = Plot(im_df, 11, 'Kamisato ImJuggler', master=root)
            app.mainloop()
        return func

    def myplot(self):
        def func():
            my_df = self.args[2].copy()
            root = tk.Toplevel(self)
            app = Plot(my_df, 11, 'Kamisato MyJuggler', master=root)
            app.mainloop()
        return func

    def mtable(self):
        def func():
            df = self.args[2].copy()
            root = tk.Toplevel(self)
            app = Mtable(df, master=root)
            app.mainloop()
        return func

    """ Kamisato """
    def sequences_of_machine(self) -> tuple:
        seq1 = ['1001'] + [str(n) for n in reversed(range(787, 796))]  # im
        seq2 = [str(n) for n in reversed(range(758, 776))]  # im
        seq3 = [str(n) for n in range(750, 758)]  # im
        seq4 = [str(n) for n in reversed(range(993, 1001))]  # my
        seq5 = [str(n) for n in range(969, 977)]  # my
        seq6 = [str(n) for n in range(776, 784)]  # go
        return seq1, seq2, seq3, seq4, seq5, seq6

    def machine_layout(self):
        frame = ttk.Frame(self.lower_frame, style='c.TFrame')
        frame.pack(expand=True, fill=tk.BOTH, padx=16)

        seqs = self.sequences_of_machine()

        frm1 = ttk.Frame(frame, style='c.TFrame')
        frm1.pack(side=tk.LEFT, anchor=tk.NW)
        self.island(frm1, seqs[0], 'Imjuggler')
        self.island(frm1, seqs[5], 'goJuggler')

        frm2 = ttk.Frame(frame, style='c.TFrame')
        frm2.pack(side=tk.LEFT, anchor=tk.NW)
        self.island(frm2, seqs[1], 'ImJuggler')

        frm3 = ttk.Frame(frame, style='c.TFrame')
        frm3.pack(side=tk.LEFT, anchor=tk.NW)
        self.island(frm3, seqs[2], 'ImJuggler')

        frm4 = ttk.Frame(frame, style='c.TFrame')
        frm4.pack(side=tk.LEFT, anchor=tk.N)
        self.island(frm4, seqs[3], 'myJuggler')

        frm5 = ttk.Frame(frame, style='c.TFrame')
        frm5.pack(anchor=tk.NW)
        self.island(frm5, seqs[4], 'myJuggler')

if __name__ == '__main__':
    from tkjug.tkapp import Theme
    root = tk.Tk()
    _ = Theme(root)
    args = kamisato_data()
    app = Hall(*args, master=root)
    app.mainloop()