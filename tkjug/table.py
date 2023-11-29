from datetime import datetime, timedelta
import holidays
import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk
from tkjug.useredis import kamisato_data, kuragano_data

# spam
sug, im, my, go = kamisato_data()

colors = {
    # dark matplot
    'bluegreen': '#8dd3c7',
    'lemon': '#feffb3',
    'lilac': '#bfbbd9',
    'salmon': '#fa8174',
    'aero': '#81b1d2',
    'orange': '#fdb462',
    'junebud': '#b3de69',
    'violet': '#bc82bd',
    'mint': '#ccebc4',
    'yellow': '#ffed6f'
}

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


def daily_table(df: pd.DataFrame, label='i_'):

    # units = df['no'].unique().size
    df_ = df.drop(columns=['no']).set_index(['date'])
    sample = df_.resample('D').agg(['count', 'sum', 'mean'])

    m_out = sample['out']['mean']
    m_games = sample['games']['mean']
    out = sample['out']['sum']
    saf = sample['saf']['sum']
    bal = out - saf
    rate = saf / out
    rb = sample['games']['sum'] / sample['rb']['sum']

    m_out.name = label + 'out'
    m_games.name = label + 'games'
    bal.name = label + 'bal'
    rate.name = label + 'rate'
    rb.name = label + 'rb'
    s = [m_out, m_games, bal, rate, rb]

    return pd.concat(s, axis=1)


class Table(tk.Frame):
    def __init__(self, df, dt, master=None):
        super().__init__(master)
        self.pack()
        self.df = df
        self.dt = dt

        self.frame = ttk.Frame(self.master, style='c.TFrame')
        self.frame.pack()

        self.buttons()

        self.init_tree()

        # self.tree()

    def buttons(self):
        button = ttk.Button(self.frame, text='prev', command=self.prev())
        button.pack()

    def init_tree(self):
        dt_s = datetime.strftime(self.dt, '%Y-%m')
        df_ = self.df.loc[dt_s]
        df = df_.reset_index()

        height = 31
        self.tree = ttk.Treeview(self.frame, height=height)
        self.tree['column'] = list(range(len(df.columns)))
        self.tree['show'] = 'headings'
        
        for i, name in enumerate(df.columns):
            self.tree.heading(i, text=name)
            anchor = tk.E if i else tk.W
            width = 82 if i else 128
            self.tree.column(i, width=width, anchor=anchor)

        self.tree_ids = []
        for i in range(height):
            values = ['' for _ in range(len(df.columns))]
            item = self.tree.insert("", "end", values=values)
            self.tree_ids.append((i+1, item))

        print(self.tree_ids)

        self.tree.pack()

    def tree(self):
        frame = ttk.Frame(self.frame, style='c.TFrame')
        frame.pack(expand=True, fill=tk.BOTH, padx=16, pady=16)
        label = ttk.Label(frame, text='Table', style='c.TLabel', font=('Arial', 16))
        label.pack(anchor=tk.W, pady=8)

        dt_s = datetime.strftime(self.dt, '%Y-%m')
        df_ = self.df.loc[dt_s]
        df = df_.reset_index()
        tree = ttk.Treeview(frame, height=len(df))
        tree["column"] = list(range(len(df.columns)))
        tree["show"] = "headings"

        tree.tag_configure('break-even', foreground=colors['salmon'])
        tree.tag_configure('im-break-even', foreground=colors['orange'])
        tree.tag_configure('my-break-even', foreground=colors['violet'])

        cols = []
        for i, col in enumerate(df.columns):
            if not i:
                width = 128
            else:
                width = 82
            cols.append((col, width))

        for i, (name, width) in enumerate(cols):
            tree.heading(i, text=name)
            anchor = tk.E if i > 0 else tk.W
            tree.column(i, width=width, anchor=anchor)

        d = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat',6: 'sun'}
        for i in df.index:
            cols = [df[col][i] for col in df.columns]
            dt = cols[0]
            wd = 'Hol' if dt in holidays.JP() else d[dt.weekday()]
            dt_s = datetime.strftime(dt, '%y-%m-%d') + ' ' + wd
            _values = [round(val, 3) if j in (3, 8) else round(val, 1) for j, val in enumerate(cols[1:])]
            imRate, myRate = _values[3], _values[8]
            values = [dt_s] + _values
            if imRate >= 1.0 and myRate >= 1.0:
                tree.insert("", "end", values=values, tags=('break-even'))
            elif imRate >= 1.0:
                tree.insert("", "end", values=values, tags=('im-break-even'))
            elif myRate >= 1.0:
                tree.insert("", "end", values=values, tags=('my-break-even'))
            else:
                tree.insert("", "end", values=values)

        tree.pack(anchor=tk.W)

    def prev(self):
        def func():
            print('ham eggs')
        return func

if __name__ == '__main__':
    from tkjug.tkapp import Theme
    root = tk.Tk()
    _ = Theme(root)
    args = kuragano_data()
    imdf = daily_table(args[1], label='i_')
    mydf = daily_table(args[2], label='m_')
    df = pd.concat([imdf, mydf], axis=1)
    dt = datetime(2023, 10, 1)
    app = Table(df, dt, master=root)
    app.mainloop()
