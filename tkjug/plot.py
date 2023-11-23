from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk
from tkjug.tkapp import Superhero
from tkjug.useredis import kuragano_data


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
    days_in_target_month = pd.date_range(start=datetime(year=2023, month=month, day=1), periods=31, freq='D')
    # 特定の月のデータがない日付を抽出
    missing_dates = [date for date in days_in_target_month if date not in df.index]
    return missing_dates

def weekend_marker(ax, x):
    start, end = min(x), max(x)
    num = (end - start).days + 1
    for day in (start + timedelta(x) for x in range(num)):
        if day.weekday() == 5:
            ax.axvline(x=day, linewidth=1, color=light)
        elif day.weekday() == 6:
            ax.axvline(x=day, linewidth=1, color=fg)


class Plot(tk.Frame):
    def __init__(self, df, month, master=None):
        super().__init__(master)
        self.pack()
        self.df = df
        self.month = month
        self.master.protocol('WM_DELETE_WINDOW', self._destroyWindow)
        self.frame = ttk.Frame(self, style='c.TFrame')
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.buttons()

        self.fig, self.ax = plt.subplots(1, 1, figsize=(9, 6))
        self.plot(self.month)
        self.canvas_draw()

    def _destroyWindow(self):
        self.master.quit()
        self.master.destroy()

    def buttons(self):
        frame = ttk.Frame(self.frame, style='c.TFrame')
        frame.pack()
        button = ttk.Button(frame, text='prev', style='c.TButton', command=self.callback())
        button.pack()

    def callback(self):
        def func():
            self.ax.cla()
            self.ax2.cla()
            self.ax3.cla()
            self.replot(10)
            self.canvas.draw()
        return func

    def replot(self, month):
        df = self.df.copy()
        df_ = df[df['date'].dt.month == month]

        df_ = df_.drop(columns=['no']).set_index(['date'])
        sample = df_.resample('D').agg(['sum'])

        missing_dates = get_missing_dates(df_)
        for dt in missing_dates:
            sample.loc[dt] = pd.Series()

        self.ax.set_title('Re: Kuragano Imjuggler', color=fg)
        self.ax.set_xlabel('Date', color=fg)

        x = sample.index
        y = sample['out']['sum'] - sample['saf']['sum']

        labels = [datetime.strftime(dt, '%y-%m-%d') for dt in x]
        self.ax.set_xticks(x, labels, rotation=90)
        self.ax.plot(x, y, label='balance', color=orange)
        self.ax.hlines([0], x.min(), x.max(), color=orange, linestyle='--')

        y_2 = sample['games']['sum'] / sample['rb']['sum']
        self.ax2.plot(x, y_2, label=f'reg', linestyle='--', color=yellow)

        y_3 = sample['out']['sum']
        self.ax3.plot(x, y_3, label='out', color=blue)

        weekend_marker(self.ax, x)

        self.ax.legend(loc=2, facecolor=secondary)
        self.ax2.legend(loc=1, facecolor=secondary)
        self.ax3.legend(loc=3, facecolor=secondary)

    def plot(self, month):
        df = self.df.copy()
        df_ = df[df['date'].dt.month == month]

        df_ = df_.drop(columns=['no']).set_index(['date'])
        sample = df_.resample('D').agg(['sum'])

        missing_dates = get_missing_dates(df_)
        for dt in missing_dates:
            sample.loc[dt] = pd.Series()

        self.fig.set_facecolor(dark)
        self.ax.set_facecolor(secondary)
        self.ax.set_title(f'Kuragano Imjuggler {month}', color=fg)
        self.ax.set_xlabel('Date', color=fg)
        # balance
        x = sample.index
        y = sample['out']['sum'] - sample['saf']['sum']

        plt.gca().tick_params(axis='x', colors=fg)
        plt.gca().tick_params(axis='y', colors=fg)
        # plt.xticks(x, rotation=90)
        labels = [datetime.strftime(dt, '%y-%m-%d') for dt in x]
        self.ax.set_xticks(x, labels, rotation=90)

        self.fig.subplots_adjust(bottom=0.2)
        self.ax.plot(x, y, label='balance', color=orange)
        self.ax.hlines([0], x.min(), x.max(), color=orange, linestyle='--')
        # reg
        self.ax2 = self.ax.twinx()
        y_2 = sample['games']['sum'] / sample['rb']['sum']
        self.ax2.plot(x, y_2, label=f'reg', linestyle='--', color=yellow)
        plt.gca().tick_params(axis='y', colors=fg)
        # out
        self.ax3 = self.ax.twinx()
        y_3 = sample['out']['sum']
        self.ax3.plot(x, y_3, label='out', color=blue)
        self.ax3.tick_params(labelright=False, labelleft=False)
        self.ax3.tick_params(right=False, left=False)

        weekend_marker(self.ax, x)

        self.ax.legend(loc=2, facecolor=secondary)
        self.ax2.legend(loc=1, facecolor=secondary)
        self.ax3.legend(loc=3, facecolor=secondary)
        # plt.show()

    def canvas_draw(self):
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)


if __name__ == '__main__':
    _, im_df, my_df = kuragano_data()
    root = tk.Tk()
    _ = Superhero(root)
    app = Plot(im_df, 11, master=root)
    app.mainloop()