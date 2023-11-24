import matplotlib.pyplot as plt
import random

def hex2rgb(code: str):
    return tuple(int(code.strip('#')[i:i+2], 16)/256 for i in range(0, 6, 2))
# matplot dark theme
black = (0., 0., 0.)
white = (1., 1., 1.)
bluegreen = hex2rgb('#8dd3c7')
lemon = hex2rgb('#feffb3')
lilac = hex2rgb('#bfbbd9')
salmon = hex2rgb('#fa8174')
aero = hex2rgb('#81b1d2')
orange = hex2rgb('#fdb462')
junebud = hex2rgb('#b3de69')
violet = hex2rgb('#bc82bd')
mint = hex2rgb('#ccebc4')
yellow = hex2rgb('#ffed6f')

plt.style.use('dark_background')

fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.2)

# fig.set_facecolor(black)
# ax.set_facecolor(black)
# ax.spines['top'].set_color(white)
# ax.spines['bottom'].set_color(white)
# ax.spines['left'].set_color(white)
# ax.spines['right'].set_color(white)

ax.set_title('Matplotlib Dark Theme') # , color=white)
# ax.tick_params(axis='x', colors=white)
# ax.tick_params(axis='y', colors=white)

colors = [bluegreen, lemon, lilac, salmon, aero, orange, junebud, violet, mint, yellow]
labels = ['bluegreen', 'lemon', 'lilac', 'salmon', 'aero', 'orange', 'junebud', 'violet', 'mint', 'yellow']
x = range(len(colors))
y = [random.randrange(5, 10) for _ in x]

ax.set_xticks(x, labels, rotation=90)
ax.bar(x, y, color=colors)
plt.show()