import tkinter as tk
from tkjug.kamisato import Kamisato
from tkjug.useredis import kamisato_data
import pandas as pd
import pytest


class TestHall:

    @pytest.fixture
    def init_app(self):
        root = tk.Tk()
        sug, im, my, go = kamisato_data()
        self.app = Kamisato(sug, im, my, go, master=root)
        yield self.app
        self.app.quit()
        self.app.destroy()

    def test_(self, init_app):
        assert self.app.h2 == ('Arial', 24)
        assert isinstance(self.app.im_df, pd.DataFrame)


    
