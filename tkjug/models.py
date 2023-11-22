import numpy as np


def imjug() -> np.ndarray:
    big = 273.1, 269.7, 269.7, 259.0, 259.0, 255.0
    reg = 439.8, 399.6, 331.0, 315.1, 255.0, 255.0 
    grape = 6.02, 6.02, 6.02, 6.02, 6.02, 5.78 
    cherry =  (32.28,) * 6 
    bell =  (1092.27,) * 6
    clown = (1092.27,) * 6
    replay = (7.298,) * 6
    return np.array([big, reg, grape, cherry, bell, clown, replay])

def myjug() -> np.ndarray:
    big = 273.1, 270.8, 266.4, 254.0, 240.1, 229.1
    reg = 409.6, 385.5, 336.1, 290.0, 268.6, 229.1
    grape = 5.90, 5.85, 5.80, 5.78, 5.76, 5.66
    cherry = 38.1, 38.1, 36.82, 35.62, 35.62, 35.62
    bell =  (1024.0,) * 6
    clown = (1024.0,) * 6
    replay =   (7.298,) * 6
    return np.array([big, reg, grape, cherry, bell, clown, replay])

def hall_rate(model: str) -> np.ndarray:
    if model == 'imjug':
        a = imjug()
    elif model == 'myjug':
        a = myjug()
    else:
        return
    cherry = a[3] * 2
    bell = a[4] * 3
    clown = a[5] * 3
    return np.concatenate([a[:3], [cherry, bell, clown], a[6:]])

def get_pk(setting: int, jug: np.ndarray) -> np.ndarray:
    p = 1/jug
    q = 1 - np.sum(p, axis=0)
    ak = np.concatenate([p, [q]]).T
    return ak[setting - 1]

def get_out_and_saf(bb: int, rb: int, games: int, model='imjug'):
    setting = 2
    a = hall_rate(model=model)
    pk = get_pk(setting, a)
    payouts = np.array([-1., -1., 8., 2., 14., 10., 3., 0.])
    bbpay = 252
    if model == 'myjug':
        bbpay = 240
    rbpay = 96
    base = pk * payouts * games
    saf = base.sum() + (bb * bbpay) + (rb * rbpay)
    out = games * 3.0
    return out, saf

def is_setting(jug: np.ndarray, rb: int, games: int) -> int:
    pass
    # reg = jug[1]
    # t = games / rb if rb else 500.0
    # values = list(map(lambda x: abs(t-x), reg))
    # min_value = min(values)
    # return values.index(min_value) + 1

# def get_balance(bb: int, rb: int, games: int, model='im'):
#     setting = 3
#     a = hall_rate(model=model)
#     pk = get_pk(setting, a)
#     payouts = np.array([-1., -1., 8., 2., 14., 10., 3., 0.])
#     big_pay = 252
#     if model == 'my':
#         big_pay = 240
#     reg_pay = 96
#     base = pk * payouts * games
#     pay = base.sum() + (bb * big_pay) + (rb * reg_pay)
#     out = games * 3.0
#     return pay, out, pay - out