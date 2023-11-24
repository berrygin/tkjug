from datetime import datetime
import json
import pandas as pd
import redis
from tkjug.models import get_out_and_saf

def get_halldata(hall: str) -> dict:
    if hall not in ['kuragano', 'kamisato']:
        return {}
    rc = redis.Redis(db=0, decode_responses=True)
    target = hall + '*'
    keys = rc.keys(target)
    dic = {}
    for key in sorted(keys):
        s = rc.get(key)
        d = json.loads(s)
        dic |= {key: d}
    return dic

def dic2df(dic: dict, model: str) -> pd.DataFrame:
    if model not in ['imjug', 'myjug', 'gojug']:
        return pd.DataFrame()
    columns = ['date', 'no', 'bb', 'rb', 'games', 'out', 'saf']
    rows = []
    for key in dic.keys():
        d = dic[key]
        date = d['desc']['date']
        dt = datetime.strptime(date, '%Y%m%d')
        model_d = d[model]
        for no, result in model_d.items():
            out, saf = get_out_and_saf(*result, model)
            row = [dt, no, *result, out, saf]
            rows.append(row)
    return pd.DataFrame(rows, columns=columns)

def suggestions(dic: dict) -> dict:
    sug = {}
    for key in dic.keys():
        desc = dic[key]['desc']
        dt = datetime.strptime(desc['date'], '%Y%m%d')
        sug |= {dt: desc['sug']}
    return sug

def kuragano_data():
    dic = get_halldata('kuragano')
    sugd = suggestions(dic)
    imdf = dic2df(dic, 'imjug')
    mydf = dic2df(dic, 'myjug')
    return sugd, imdf, mydf

def kamisato_data():
    dic = get_halldata('kamisato')
    sugd = suggestions(dic)
    imdf = dic2df(dic, 'imjug')
    mydf = dic2df(dic, 'myjug')
    godf = dic2df(dic, 'gojug')
    return sugd, imdf, mydf, godf