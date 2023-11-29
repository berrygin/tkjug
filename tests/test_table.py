from tkjug.table import *
from datetime import datetime


def test_next_month():
    dt = datetime(2023, 11, 1)
    next_dt = next_month(dt)
    assert next_dt == datetime(2023, 12, 1)

def test_prev_month():
    dt = datetime(2023, 11, 1)
    prev_dt = prev_month(dt)
    assert prev_dt == datetime(2023, 10, 1)