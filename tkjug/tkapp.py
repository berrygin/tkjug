import os
import redis
import tkinter as tk
import tkinter.ttk as ttk
from tkjug.kuragano import Hall as Kuragano
from tkjug.kamisato import Hall as Kamisato
from tkjug.useredis import kuragano_data, kamisato_data


# def test2():
#     rc = redis.Redis()
#     print(len(rc.keys()))


class Theme(tk.Frame):
    ''' Bootstrap Superhero & clam Theme '''
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        style = ttk.Style()
        style.theme_use('clam')

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
        bg = colors['background']
        fg = colors['foreground']

        h1_font = 'Arial', 32
        h2_font = 'Arial', 24
        h3_font = 'Arial', 16
        body_font = 'Arial', 8
        style.configure('c.TFrame', background=bg)
        style.configure('c.TLabel', background=bg, foreground=fg)
        style.configure('green.TLabel', background=bg, foreground=colors['success'])
        # style.configure('c.TCheckbutton', background=bg, foreground=fg)
        style.configure('c.TButton', borderwidth=0, background=colors['secondary'], foreground=fg)
        style.configure('c.TSeparator', background=bg)
        # tree
        style.configure('Treeview.Heading', background=colors['light'], foreground=fg, font=('Arial', 12))
        fontsize = 11 if os.name == 'nt' else 12
        style.configure('Treeview', background='black', foreground=fg, font=('Courier', fontsize))
        # matplot dark
        style.configure('plot.TFrame', background='black')
        style.configure('plot.TLabel', background='black', foreground='white')
        style.configure('plot.TButton', background=colors['secondary'], foreground='white')  # mint


class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        # self.master.protocol('WM_DELETE_WINDOW', self._destroyWindow)
        self.master.title('ฅ•ω•ฅ GOGO! CHANCE ฅ•ω•ฅ')
        self.master.geometry('+32+32')
        self.master.resizable(width=False, height=False)
        self.master.attributes('-alpha', 0.98)
        self.frame = ttk.Frame(master, width=200, height=200, style='c.TFrame')
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.heading()
        self.buttons()

    def _destroyWindow(self):
        self.master.quit()
        self.master.destroy()

    def heading(self):
        frame1 = ttk.Frame(self.frame, style='c.TFrame')
        frame1.pack(expand=True, fill=tk.X, anchor=tk.N, padx=16, pady=16)
        h3_font = 'Arial', 16
        s = 'The evil clown and the strange hat'
        label = ttk.Label(frame1, text=s, style='c.TLabel', font=h3_font)
        label.pack(anchor=tk.W, padx=16)
        separator = ttk.Separator(frame1, orient='horizontal', style='c.TSeparator')
        separator.pack(fill=tk.BOTH, padx=16)

    def buttons(self):
        frame2 = ttk.Frame(self.frame, style='c.TFrame')
        frame2.pack(expand=True, fill=tk.BOTH, padx=32)
        btn = ttk.Button(frame2, text='Kuragano', style='c.TButton', command=self.kuragano())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)
        btn = ttk.Button(frame2, text='Kamisato', style='c.TButton', command=self.kamisato())
        btn.pack(side=tk.LEFT, anchor=tk.N, padx=4, pady=8)
        ttk.Frame(frame2, style='c.TFrame').pack(pady=32)

    def kuragano(self):
        def func():
            root = tk.Toplevel(self)
            args = kuragano_data()
            app = Kuragano(*args, master=root)
            app.mainloop()
        return func

    def kamisato(self):
        def func():
            root = tk.Toplevel(self)
            args = kamisato_data()
            app = Kamisato(*args, master=root)
            app.mainloop()
        return func

def hex2rgb(colorcode: str):
    hex_ = colorcode.lstrip('#')
    return tuple(int(hex_[i:i+2], 16)/256 for i in range(0, 6, 2))

def main():
    root = tk.Tk()
    _ = Theme(root)
    app = App(master=root)
    app.mainloop()


if __name__ == '__main__':
    main()