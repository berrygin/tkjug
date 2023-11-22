from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from tkjug.useredis import kuragano_data


def hex2rgb(colorcode: str):
    code = colorcode.lstrip('#')
    return tuple(int(code[i:i+2], 16)/256 for i in range(0, 6, 2))

bg = hex2rgb('#0f2537')
fg = hex2rgb('#ebebeb')
orange = hex2rgb('#df6919')
secondary = hex2rgb('#4e5d6c')
green = hex2rgb('#5cb85c')
blue = hex2rgb('#5bc0de')
yellow = hex2rgb('#ffc107')
red = hex2rgb('#d9534f')
light = hex2rgb('#abb6c2')
dark = hex2rgb('#20374c')


def get_missing_dates(df):
    dt = df.index[0]
    year = dt.year
    month = dt.month
    # 特定の月の日付範囲を生成
    days_in_target_month = pd.date_range(start=datetime(year=2023, month=month, day=1), periods=31, freq='D')
    # 特定の月のデータがない日付を抽出
    missing_dates = [date for date in days_in_target_month if date not in df.index]
    # print(missing_dates)
    return missing_dates

def weekend_marker(plt, start, end):
    num = (end - start).days + 1
    for day in (start + timedelta(x) for x in range(num)):
        if day.weekday() == 5:
            plt.axvline(x=day, linewidth=1, color=blue)
        elif day.weekday() == 6:
            plt.axvline(x=day, linewidth=1, color=orange)

_, im_df, my_df = kuragano_data()

df = im_df[im_df['date'].dt.month == 11]

df_ = df.drop(columns=['no']).set_index(['date'])
# sample = df_.resample('D').agg(['count', 'sum', 'mean'])
sample = df_.resample('D').agg(['sum'])
# print(sample.head(2))
missing_dates = get_missing_dates(df_)
for dt in missing_dates:
    sample.loc[dt] = pd.Series()


fig, ax = plt.subplots(1, 1, figsize=(10, 7))
fig.set_facecolor(dark)
ax.set_facecolor(secondary)
ax.set_title('sample')

ax.set_xlabel('Date')
x = sample.index
y = sample['out']['sum']
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
plt.xticks(x, rotation=90)
fig.subplots_adjust(bottom=0.2)
# out
ax.plot(x, y, label='out', color=green)

# balance
ax2 = ax.twinx()
y_ = sample['out']['sum'] - sample['saf']['sum']
ax2.plot(x, y_, label='balance', color=yellow)
ax2.hlines([0], x.min(), x.max(), color=yellow, linestyle='dashed')
# reg
ax3 = ax.twinx()
y_rb = sample['games']['sum'] / sample['rb']['sum']
m = round(y_rb.mean(), 1)
ax3.plot(x, y_rb, label=f'reg mean={m}', color=light)
ax3.tick_params(labelbottom=False, labelright=False)
ax3.tick_params(bottom=False, right=False)

weekend_marker(plt, x[0], x[-1])

ax.legend(loc=2)
ax2.legend(loc=1)
ax3.legend(loc=4)

plt.show()