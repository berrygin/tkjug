from datetime import datetime, timedelta
import holidays
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk


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

def get_missing_dates(df):
    dt = df.index[0]
    year = dt.year
    month = dt.month
    # 特定の月の日付範囲を生成
    days_in_target_month = pd.date_range(start=datetime(year=year, month=month, day=1), periods=31, freq='D')
    # 特定の月のデータがない日付を抽出
    missing_dates = [date for date in days_in_target_month if date not in df.index]
    return missing_dates

monthd = { i + 1: m for i, m in enumerate(
    ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
)}


class Plot(tk.Frame):
    def __init__(self, df, month, title, master=None):
        super().__init__(master)
        self.pack()
        self.df = df
        self.month = month
        self.master.protocol('WM_DELETE_WINDOW', self._destroyWindow)
        self.frame = ttk.Frame(self, style='plot.TFrame')
        self.frame.pack(expand=True, fill=tk.BOTH)

        pt = title + ' ' + monthd[month]
        self.plot_title = tk.StringVar(value=pt)

        self.buttons()
        self.init_aixs()
        self.plot(self.month)
        self.canvas_draw()

    def buttons(self):
        frame = ttk.Frame(self.frame, style='plot.TFrame')
        frame.pack(expand=True, fill=tk.X, padx=128, pady=16)
        button = ttk.Button(frame, text='prev', style='plot.TButton', command=self.callback())
        button.pack(side=tk.LEFT, anchor=tk.W)
        h3_font = 'Arial', 16
        label = ttk.Label(frame, textvariable=self.plot_title, style='plot.TLabel', font=h3_font, anchor=tk.CENTER)
        label.pack(expand=True, fill=tk.X, side=tk.LEFT)
        button = ttk.Button(frame, text='next', style='plot.TButton', command=self.callback())
        button.pack(anchor=tk.E)

    def callback(self):
        def func():
            self.ax1.cla()
            self.ax2.cla()
            self.ax3.cla()
            self.plot(10)
            self.canvas.draw()
        return func

    def init_aixs(self):
        self.fig, self.ax1 = plt.subplots(1, 1, figsize=(8, 5))
        self.ax2 = self.ax1.twinx()
        self.ax3 = self.ax1.twinx()
        self.fig.set_facecolor('black')
        self.ax1.set_facecolor('black')
        self.fig.subplots_adjust(top=0.99)
        self.fig.subplots_adjust(bottom=0.2)
        for spine in self.ax3.spines.values():
            spine.set_color('white')

    def plot(self, month):
        df = self.df.copy()
        df_ = df[df['date'].dt.month == month]

        df_ = df_.drop(columns=['no']).set_index(['date'])
        sample = df_.resample('D').agg(['sum'])

        missing_dates = get_missing_dates(df_)
        for dt in missing_dates:
            sample.loc[dt] = pd.Series()

        self.ax1.set_xlabel('Date', color='white')
        self.ax1.tick_params(axis='x', colors='white')

        x = sample.index
        labels = [datetime.strftime(dt, '%y-%m-%d') for dt in x]
        self.ax1.set_xticks(x, labels, rotation=90)
        # balance
        orange = colors['orange']
        y_1 = sample['out']['sum'] - sample['saf']['sum']
        self.ax1.plot(x, y_1, label='balance', color=orange)
        self.ax1.hlines([0], x.min(), x.max(), color=orange, linestyle='--')
        self.ax1.tick_params(axis='y', colors=orange)
        # reg
        yellow = colors['mint']
        y_2 = sample['games']['sum'] / sample['rb']['sum']
        self.ax2.plot(x, y_2, label=f'reg', linestyle='--', color=yellow)
        self.ax2.tick_params(axis='y', colors=yellow)
        # out
        blue = colors['aero']
        y_3 = sample['out']['sum']
        self.ax3.plot(x, y_3, label='out', color=blue)
        self.ax3.tick_params(labelright=False, labelleft=False)
        self.ax3.tick_params(right=False, left=False)

        self.weekend_axvline(x)

        self.ax1.legend(loc=2, labelcolor='white', facecolor='black', edgecolor='black')
        self.ax2.legend(loc=1, labelcolor='white', facecolor='black', edgecolor='black')
        self.ax3.legend(loc=3, labelcolor='white', facecolor='black', edgecolor='black')


    def canvas_draw(self):
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def weekend_axvline(self, x):
        start, end = min(x), max(x)
        num = (end - start).days + 1

        for day in (start + timedelta(x) for x in range(num)):
            if day in holidays.JP():
                self.ax1.axvline(x=day, linewidth=1, color=colors['violet'], linestyle=(0, (1, 10)))
            elif day.weekday() == 5:
                self.ax1.axvline(x=day, linewidth=1, color=colors['lilac'], linestyle=(0, (1, 10)))
            elif day.weekday() == 6:
                self.ax1.axvline(x=day, linewidth=1, color=colors['violet'], linestyle=(0, (1, 10)))

    def _destroyWindow(self):
        self.fig.clf()
        plt.close(self.fig)
        self.master.quit()
        self.master.destroy()

if __name__ == '__main__':
    from tkjug.tkapp import Superhero
    from tkjug.useredis import kuragano_data
    _, im_df, my_df = kuragano_data()
    root = tk.Tk()
    _ = Superhero(root)
    app = Plot(im_df, 11, 'test', master=root)
    app.mainloop()