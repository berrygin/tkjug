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

def weekend_marker(plt, start, end):
    num = (end - start).days + 1
    for day in (start + timedelta(x) for x in range(num)):
        if day.weekday() == 5:
            plt.axvline(x=day, linewidth=1, color=light)
        elif day.weekday() == 6:
            plt.axvline(x=day, linewidth=1, color=fg)


class Plot(tk.Frame):
    def __init__(self, df, month, master=None):
        super().__init__(master)
        self.pack()
        self.df = df
        self.month = month
        self.frame = ttk.Frame(self, style='c.TFrame')
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.buttons()
        self.draw(self.month)

    def buttons(self):
        frame = ttk.Frame(self.frame, style='c.TFrame')
        frame.pack()
        button = ttk.Button(frame, text='prev', style='c.TButton', command=self.callback())
        button.pack()

    def callback(self):
        def func():
            self.draw(10)
        return func

    def draw(self, month):
        df = self.df.copy()
        df_ = df[df['date'].dt.month == month]

        df_ = df_.drop(columns=['no']).set_index(['date'])
        sample = df_.resample('D').agg(['sum'])

        missing_dates = get_missing_dates(df_)
        for dt in missing_dates:
            sample.loc[dt] = pd.Series()

        fig, ax = plt.subplots(1, 1, figsize=(9, 6))
        fig.set_facecolor(dark)
        ax.set_facecolor(secondary)
        ax.set_title('Kuragano Imjuggler', color=fg)
        ax.set_xlabel('Date', color=fg)
        # balance
        x = sample.index
        y = sample['out']['sum'] - sample['saf']['sum']
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.gca().tick_params(axis='x', colors=fg)
        plt.gca().tick_params(axis='y', colors=fg)
        plt.xticks(x, rotation=90)
        fig.subplots_adjust(bottom=0.2)
        ax.plot(x, y, label='balance', color=orange)
        ax.hlines([0], x.min(), x.max(), color=orange, linestyle='--')
        # reg
        ax2 = ax.twinx()
        y_2 = sample['games']['sum'] / sample['rb']['sum']
        ax2.plot(x, y_2, label=f'reg', linestyle='--', color=yellow)
        plt.gca().tick_params(axis='y', colors=fg)
        # out
        ax3 = ax.twinx()
        y_3 = sample['out']['sum']
        ax3.plot(x, y_3, label='out', color=blue)
        ax3.tick_params(labelright=False, labelleft=False)
        ax3.tick_params(right=False, left=False)

        weekend_marker(plt, x[0], x[-1])

        ax.legend(loc=2, facecolor=secondary)
        ax2.legend(loc=1, facecolor=secondary)
        ax3.legend(loc=3, facecolor=secondary)
        # plt.show()
        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)


if __name__ == '__main__':
    _, im_df, my_df = kuragano_data()
    root = tk.Tk()
    _ = Superhero(root)
    app = Plot(im_df, 11, master=root)
    app.mainloop()