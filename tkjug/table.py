from datetime import datetime, timedelta
import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk
from tkjug.useredis import kamisato_data

# spam
sug, im, my, go = kamisato_data()

def monthly_table_table(df: pd.DataFrame):

    units = df['no'].unique().size
    df_ = df.drop(columns=['no']).set_index(['date'])
    sample = df_.resample('M').agg(['count', 'sum', 'mean'])
    print(sample.index)

    dates = sample['bb']['count'] / units
    # print(dates)
    out = sample['out']['sum']
    saf = sample['saf']['sum']
    balance = out - saf
    rate = saf / out
    mean_out = sample['out']['mean']
    mean_games = sample['games']['mean']
    rb_p = sample['games']['sum'] / sample['rb']['sum']

    s = [dates, out, balance, rate, mean_out, mean_games, rb_p]
    c = 'dates', 'out', 'balance', 'rate', 'mean_out', 'mean_games', 'rb'
    _df = pd.concat(s, axis=1)
    _df.columns = c
    return _df


def daily_table(df: pd.DataFrame):

    units = df['no'].unique().size
    df_ = df.drop(columns=['no']).set_index(['date'])
    sample = df_.resample('D').agg(['count', 'sum', 'mean'])

    dates = sample['bb']['count'] / units
    # print(dates)
    out = sample['out']['sum']
    saf = sample['saf']['sum']
    balance = out - saf
    rate = saf / out
    mean_out = sample['out']['mean']
    mean_games = sample['games']['mean']
    rb_p = sample['games']['sum'] / sample['rb']['sum']

    s = [dates, out, balance, rate, mean_out, mean_games, rb_p]
    c = 'dates', 'out', 'balance', 'rate', 'mean_out', 'mean_games', 'rb'
    _df = pd.concat(s, axis=1)
    _df.columns = c
    print(_df.head(3))


class Table(tk.Frame):
    def __init__(self, df, master=None):
        super().__init__(master)
        self.pack()

        self.frame = ttk.Frame(self.master, style='c.TFrame')
        self.frame.pack()

        self.tree()

    def tree(self):
        frame3 = ttk.Frame(self.frame, style='c.TFrame')
        frame3.pack(expand=True, fill=tk.BOTH, padx=16, pady=16)
        label = ttk.Label(frame3, text='Table', style='c.TLabel', font=('Arial', 16))
        label.pack(anchor=tk.W, pady=8)

        df_ = monthly_table(my)
        # df = df_.drop(columns=['class']).iloc[:3, :]
        df = df_.iloc[:3, :]
        tree = ttk.Treeview(frame3, height=len(df))
        tree["column"] = list(range(len(df.columns)))
        tree["show"] = "headings"
        cols = []
        for col in df.columns:
            cols.append((col, 98))

        for i, (name, width) in enumerate(cols):
            tree.heading(i, text=name)
            # anchor = tk.E if i < 4 else tk.CENTER
            anchor = tk.E
            tree.column(i, width=width, anchor=anchor)

        for i in df.index:
            values = [df[col][i] for col in df.columns]
            values = [round(value, 1) for value in values]
            tree.insert("", "end", values=values)

        tree.pack(anchor=tk.W)


if __name__ == '__main__':
    # from tkjug.tkapp import Theme
    # root = tk.Tk()
    # _ = Theme(root)
    # app = Mtable(root)
    # app.mainloop()
    args = kamisato_data()
    df = args[1]  # im
    daily_table(df)
