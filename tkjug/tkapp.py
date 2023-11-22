import redis
import tkinter as tk
import tkinter.ttk as ttk
from tkjug.kuragano import Kuragano


def test2():
    rc = redis.Redis()
    print(len(rc.keys()))


class Superhero(tk.Frame):
    ''' Bootstrap Superhero & clam Theme '''
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        style = ttk.Style()
        style.theme_use('clam')
        bg = '#0f2537'
        fg = '#ebebeb'
        secondary = '#4e5d6c'
        light = '#abb6c2'
        dark = '#20374c'
        orange = '#df6919'
        green = '#5cb85c'
        blue = '#5bc0de'
        yellow = '#ffc107'
        red = '#d9534f'
        h1_font = 'Arial', 32
        h2_font = 'Arial', 24
        h3_font = 'Arial', 16
        body_font = 'Arial', 8
        style.configure('c.TFrame', background=bg)
        style.configure('c.TLabel', background=bg, foreground=fg)
        style.configure('light.TLabel', background=bg, foreground=light)
        style.configure('green.TLabel', background=bg, foreground=green)
        style.configure('c.TCheckbutton', background=bg, foreground=fg)
        style.configure('c.TButton', borderwidth=0, background=secondary, foreground=fg)
        style.configure('c.TSeparator', background=bg)
        style.configure('Treeview.Heading', background=secondary, foreground=fg)
        style.configure('Treeview', background=dark, foreground=fg)

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.master.protocol('WM_DELETE_WINDOW', self._destroyWindow)
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
            app = Kuragano(master=root)
            app.mainloop()
        return func

    def kamisato(self):
        def func():
            print('funk!')
        return func


def hex2rgb(colorcode: str):
    hex_ = colorcode.lstrip('#')
    return tuple(int(hex_[i:i+2], 16)/256 for i in range(0, 6, 2))

def main():
    root = tk.Tk()
    _ = Superhero(root)
    app = App(master=root)
    app.mainloop()


if __name__ == '__main__':
    main()