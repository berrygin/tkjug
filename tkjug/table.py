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

monthd = { i + 1: m for i, m in enumerate(
    ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
)}

def next_month(dt):
    year = dt.year + (dt.month // 12)
    month = dt.month % 12 + 1
    next_month = datetime(year, month, 1)
    return next_month

def prev_month(dt):
    first_dt = datetime(dt.year, dt.month, 1)
    dt_ = first_dt + timedelta(days=-1)
    prev_month = datetime(dt_.year, dt_.month, 1)
    return prev_month

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


def concat_df(*args):
    imdf = daily_table(args[1], label='i_')
    mydf = daily_table(args[2], label='m_')
    return pd.concat([imdf, mydf], axis=1)


class Table(tk.Frame):
    def __init__(self, df, dt, hall, master=None):
        super().__init__(master)
        self.pack()
        self.df = df
        self.dt = dt
        self.hall = hall
        
        value = hall + ' ' + monthd[dt.month]
        self.title = tk.StringVar(value=value)

        frame = ttk.Frame(self.master, style='c.TFrame')
        frame.pack(expand=True, fill=tk.BOTH)
        self.upper_frame = ttk.Frame(frame, style='c.TFrame')
        self.upper_frame.pack(expand=True, fill=tk.X, padx=8, pady=16)
        self.lower_frame = ttk.Frame(frame, style='c.TFrame')
        self.lower_frame.pack(expand=True, fill=tk.X, padx=8)

        self.heading()
        self.init_tree()
        self.set_tree(dt)

    def heading(self):
        h2 = 'Arial', 24
        label = ttk.Label(self.upper_frame, textvariable=self.title, style='c.TLabel', font=h2)
        label.pack(side=tk.LEFT, padx=16, anchor=tk.NW)
        self.init_summary(self.upper_frame)
        button = ttk.Button(self.upper_frame, text='prev', command=self.prev())
        button.pack(side=tk.LEFT, padx=8, anchor=tk.NW)
        button = ttk.Button(self.upper_frame, text='next', command=self.next())
        button.pack(anchor=tk.NW, padx=8)

    def init_summary(self, frame):
        self.tree_s = ttk.Treeview(frame, height=1, show='headings')
        columns = 'i_out', 'i_rate', 'i_reg', 'm_out', 'm_rate', 'm_reg'
        self.tree_s['column'] = columns
        for name in columns:
            self.tree_s.heading(name, text=name, anchor=tk.CENTER)
            self.tree_s.column(name, width=82, anchor=tk.E)
        self.item_s = self.tree_s.insert('', 'end', values=('',))
        self.tree_s.pack(side=tk.LEFT, padx=8)

    def set_summary(self, df):
        means = df[['i_out', 'i_rate', 'i_rb', 'm_out', 'm_rate', 'm_rb']].mean()
        values = [round(val, 3) if idx.endswith('rate') else round(val, 1) for idx, val in means.items()]
        self.tree_s.item(self.item_s, values=values)

    def init_tree(self):
        dt_s = datetime.strftime(self.dt, '%Y-%m')
        df_ = self.df.loc[dt_s]
        df = df_.reset_index()

        days = 31
        self.tree = ttk.Treeview(self.lower_frame, height=days, show='headings')
        self.tree['column'] = df.columns.to_list()  # listにしないと一つ余計なフィールドがでる
        for name in df.columns:
            width = 128 if name == 'date' else 82
            anchor = tk.CENTER if name == 'date' else tk.E
            self.tree.heading(name, text=name)
            self.tree.column(name, width=width, anchor=anchor)

        # 空のtreeviewを作成
        self.items = []
        for i in range(days):
            item = self.tree.insert('', 'end', values=('',))
            self.items.append((i+1, item))

        self.tree.pack()

    def reset_tree(self):
        for _, item in self.items:
            self.tree.item(item, values=('',))

    def set_tree(self, dt):

        dt_s = datetime.strftime(dt, '%Y-%m')
        df_ = self.df.loc[dt_s]
        df = df_.reset_index()

        self.set_summary(df)

        self.tree.tag_configure('lose', foreground='white')
        self.tree.tag_configure('break-even', foreground=colors['salmon'])
        self.tree.tag_configure('im-break-even', foreground=colors['orange'])
        self.tree.tag_configure('my-break-even', foreground=colors['violet'])

        d = {}
        for _, row in df.iterrows():
            d |= {row['date'].day: row}

        year, month = dt.year, dt.month
        for i, item in self.items:
            im_rate, my_rate = 0, 0
            if i in d.keys():
                row = d[i]
                im_rate = row['i_rate']
                my_rate = row['m_rate']
                values = self.get_values(row)
            else:
                try:
                    dt = datetime(year, month, i)
                    dt_s = self.get_dt_s(dt)
                    values = (dt_s,)
                except ValueError:
                    values = ('',)

            if im_rate >= 1.0 and my_rate >= 1.0:
                self.tree.item(item, values=values, tags=['break-even'])
            elif im_rate >= 1.0:
                self.tree.item(item, values=values, tags=['im-break-even'])
            elif my_rate >= 1.0:
                self.tree.item(item, values=values, tags=['my-break-even'])
            else:
                self.tree.item(item, values=values, tags=['lose'])

    def get_dt_s(self, dt):
        dic = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat',6: 'sun'}
        weekday = 'hol' if dt in holidays.JP() else dic[dt.weekday()]
        return datetime.strftime(dt, '%y-%m-%d') + ' ' + weekday

    def get_values(self, row):
        values = []
        for idx, item in row.items():
            if idx == 'date':
                value = self.get_dt_s(item)
            elif idx.endswith('rate'):
                value = round(item, 3)
            else:
                value = round(item, 1)
            values.append(value)
        return values

    def the_month_exist(self, dt):
        dt_s = datetime.strftime(dt, '%Y-%m')
        try:
            self.df.loc[dt_s]
        except KeyError:
            return False
        else:
            return True

    def prev(self):
        def func():
            prev_dt = prev_month(self.dt)
            if self.the_month_exist(prev_dt):
                value = self.hall + ' ' + monthd[prev_dt.month]
                self.title.set(value)
                self.reset_tree()
                self.set_tree(prev_dt)
                self.dt = prev_dt
        return func

    def next(self):
        def func():
            next_dt = next_month(self.dt)
            if self.the_month_exist(next_dt):
                value = self.hall + ' ' + monthd[next_dt.month]
                self.title.set(value)
                self.reset_tree()
                self.set_tree(next_dt)
                self.dt = next_dt
        return func

if __name__ == '__main__':
    from tkjug.tkapp import Theme
    root = tk.Tk()
    _ = Theme(root)
    args = kuragano_data()
    df = concat_df(*args)
    dt = datetime(2023, 11, 1)
    hall = 'Kuragano'
    app = Table(df, dt, hall, master=root)
    app.mainloop()
