from datetime import datetime, timedelta
import holidays
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk


def hex2rgb(colorcode: str):
    code = colorcode.lstrip('#')
    return tuple(int(code[i:i+2], 16)/256 for i in range(0, 6, 2))
# SuperHero
orange = hex2rgb('#df6919')
green = hex2rgb('#5cb85c')
blue = hex2rgb('#5bc0de')
yellow = hex2rgb('#ffc107')
red = hex2rgb('#d9534f')
light = hex2rgb('#abb6c2')
secondary = hex2rgb('#4e5d6c')
dark = hex2rgb('#20374c')
fg = hex2rgb('#ebebeb')
bg = hex2rgb('#0f2537')

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
        self.frame = ttk.Frame(self, style='dark.TFrame')
        self.frame.pack(expand=True, fill=tk.BOTH)

        pt = title + ' ' + monthd[month]
        self.plot_title = tk.StringVar(value=pt)

        self.buttons()
        self.init_aixs()
        self.plot(self.month)
        self.canvas_draw()

    def buttons(self):
        frame = ttk.Frame(self.frame, style='dark.TFrame')
        frame.pack(expand=True, fill=tk.X, padx=128, pady=16)
        button = ttk.Button(frame, text='prev', style='c.TButton', command=self.callback())
        button.pack(side=tk.LEFT, anchor=tk.W)
        h3_font = 'Arial', 16
        label = ttk.Label(frame, textvariable=self.plot_title, style='dark.TLabel', font=h3_font, anchor=tk.CENTER)
        label.pack(expand=True, fill=tk.X, side=tk.LEFT)
        button = ttk.Button(frame, text='next', style='c.TButton', command=self.callback())
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
        self.fig, self.ax1 = plt.subplots(1, 1, figsize=(9, 6))
        self.ax2 = self.ax1.twinx()
        self.ax3 = self.ax1.twinx()
        self.fig.set_facecolor(dark)
        self.ax1.set_facecolor(secondary)
        self.fig.subplots_adjust(top=0.99)
        self.fig.subplots_adjust(bottom=0.2)

    def plot(self, month):
        df = self.df.copy()
        df_ = df[df['date'].dt.month == month]

        df_ = df_.drop(columns=['no']).set_index(['date'])
        sample = df_.resample('D').agg(['sum'])

        missing_dates = get_missing_dates(df_)
        for dt in missing_dates:
            sample.loc[dt] = pd.Series()

        # self.ax1.set_title(f'Kuragano Imjuggler {month}', color=fg)
        self.ax1.set_xlabel('Date', color=fg)
        self.ax1.tick_params(axis='x', colors=fg)

        x = sample.index
        labels = [datetime.strftime(dt, '%y-%m-%d') for dt in x]
        self.ax1.set_xticks(x, labels, rotation=90)
        # balance
        y_1 = sample['out']['sum'] - sample['saf']['sum']
        self.ax1.plot(x, y_1, label='balance', color=orange)
        self.ax1.hlines([0], x.min(), x.max(), color=orange, linestyle='--')
        self.ax1.tick_params(axis='y', colors=orange)
        # reg
        y_2 = sample['games']['sum'] / sample['rb']['sum']
        self.ax2.plot(x, y_2, label=f'reg', linestyle='--', color=yellow)
        self.ax2.tick_params(axis='y', colors=yellow)
        # out
        y_3 = sample['out']['sum']
        self.ax3.plot(x, y_3, label='out', color=blue)
        self.ax3.tick_params(labelright=False, labelleft=False)
        self.ax3.tick_params(right=False, left=False)

        self.weekend_axvline(x)

        self.ax1.legend(loc=2, facecolor=secondary)
        self.ax2.legend(loc=1, facecolor=secondary)
        self.ax3.legend(loc=3, facecolor=secondary)

    def canvas_draw(self):
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def weekend_axvline(self, x):
        start, end = min(x), max(x)
        num = (end - start).days + 1
        for day in (start + timedelta(x) for x in range(num)):
            if day in holidays.JP():
                self.ax1.axvline(x=day, linewidth=1, color=fg, linestyle='--')
            elif day.weekday() == 5:
                self.ax1.axvline(x=day, linewidth=1, color=light)
            elif day.weekday() == 6:
                self.ax1.axvline(x=day, linewidth=1, color=fg)

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