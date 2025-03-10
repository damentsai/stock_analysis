import pandas as pd
import numpy as np
import pickle
import requests
import datetime
import yfinance as yf
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date

TW_csv = 't187ap03_L.csv'  # 上市股票表
TWO_csv = 't187ap03_O.csv'  # 上櫃股票表
TW = pd.read_csv(TW_csv)
TWO = pd.read_csv(TWO_csv)
start = '2024-03-01'

def TWorTWO(target_stock, TW=TW, TWO=TWO):
    if int(target_stock) in TW['公司代號'].tolist():
        return f'{target_stock}.TW'

    elif int(target_stock) in TWO['公司代號'].tolist():
        return f'{target_stock}.TWO'

    else:
        print("THE TW STOCK DONNOT EXIST")
        return

matplotlib.rcParams['font.family'] = ['Microsoft JhengHei', 'Calibri']  # 设置字体家族
plt.rcParams['axes.unicode_minus'] = False
# today = datetime.datetime.today().strftime('%y%m%d')
ticker = 'aCDD04'  # 安聯
RERUN = False
FUND_KDJ_DICT_NAME = 'funds_OBV.pkl'



if (RERUN):
    try:
        url_df = f'https://www.moneydj.com/funddj/yp/yp011000.djhtm?a={ticker}'
        fund_name = pd.read_html(url_df)[3][3][0]
        url = f'https://www.moneydj.com/funddj/yp/yp013000.djhtm?a={ticker}'
        data = pd.read_html(url)
        funds_df = data[8]  # 多嘗試幾個index，pd read_html就可以找到對的表格了
        first_part = funds_df.iloc[:, :4]  # 前兩列
        second_part = funds_df.iloc[1:, 4:]  # 後兩列
        second_part.columns = [0, 1, 2, 3]  # columns 校準
        columns = first_part.columns[:4]  # [投資名稱  投資(千股)    比例      增減]
        funds_df = pd.concat([first_part, second_part], axis=0, ignore_index=True)
        for (i, stock) in enumerate(funds_df.iloc[:, 0].isnull()):
            if funds_df.iloc[:, 0].isnull()[i]:
                funds_df = funds_df.drop([i], axis=0)

        for (i, stock) in enumerate(funds_df.iloc[:, 3].isnull()):
            if i != 0:
                if funds_df.iloc[:, 3].isnull()[i]:
                    funds_df.iloc[i, 3] = 0.0
                else:
                    funds_df.iloc[i, 3] = funds_df.iloc[i, 3].replace('%', '')

        funds_df.iloc[1:, 2] = pd.to_numeric(funds_df.iloc[1:, 2]) / 100
        funds_df.iloc[1:, 3] = pd.to_numeric(funds_df.iloc[1:, 3]) / 100

        # 找到基金投資股票的代碼。
        whole_stock_url = "https://histock.tw/stock/rank.aspx?p=all"
        whole_stock = pd.read_html(whole_stock_url)
        whole_stock = whole_stock[0]

        whole_stock = whole_stock[['代號▼', '名稱▼']]
        funds_df['代號'] = None
        funds_df['名稱'] = None
        for (i, stock) in enumerate(funds_df.iloc[1:, 0]):
            idx = whole_stock.index[whole_stock['名稱▼'] == funds_df.iloc[i + 1, 0]].tolist()[0]
            #print(idx)
            funds_df.loc[i+1, '代號'] = whole_stock.loc[idx, '代號▼']
            funds_df.loc[i + 1, '名稱'] = whole_stock.loc[idx, '名稱▼']
    except Exception as e:
        print(e)


    print(funds_df)
    funds_dict = {}
    funds_dict['funds df'] = funds_df
    total_weight = sum(funds_df.iloc[1:, 2])
    vol_colors = ["#EDB120"]
    target_stock_ = funds_df.loc[1, '代號']
    df_ = yf.download(TWorTWO(target_stock_), start=start, interval='1d')
    # stock = twstock.Stock(target_stock)
    # print(funds_df.loc[i, '代號'].tolist(0))
    funds_dict['Every OBV'] = [''] * (len(funds_df)-1)

    # 下載個股資料
    for i in range(1, len(funds_df)):
        print(funds_df.iloc[i, funds_df.columns.get_loc('代號')])
        target_stock = funds_df.iloc[i, funds_df.columns.get_loc('代號')]
        df = yf.download(TWorTWO(target_stock), start=start, interval='1d')
        filename = f'./data/{target_stock}.csv'
        df.to_csv(filename)
        df = pd.read_csv(filename)
        df['OBV'] = [0] * len(df)
        funds_dict['Date'] = df.index
        for j in range(1, len(df)):
            if df.iloc[j, df.columns.get_loc('Close')] - df.iloc[j - 1, df.columns.get_loc('Close')] > 0:
                sign = 1
            elif df.iloc[j, df.columns.get_loc('Close')] - df.iloc[j - 1, df.columns.get_loc('Close')] < 0:
                sign = -1
            else:
                sign = 0
            df.iloc[j, df.columns.get_loc('OBV')] = df.iloc[j - 1, df.columns.get_loc('OBV')] + \
                                                    df.iloc[j, df.columns.get_loc('Volume')] * sign
        df['10ma OBV'] = df['OBV'].rolling(window=10).mean()
        temp_OBV = df['OBV'] - df['10ma OBV']
        if temp_OBV.tolist()[-1] > 0:
            funds_dict['Every OBV'][i-1] = 'Rise'
        if temp_OBV.tolist()[-1] < 0:
            funds_dict['Every OBV'][i-1] = 'Fall'
        if temp_OBV.tolist()[-1] == 0:
            if temp_OBV.tolist()[-2] > 0:
                funds_dict['Every OBV'][i-1] = 'Dead Cross'
            if temp_OBV.tolist()[-2] < 0:
                funds_dict['Every OBV'][i-1] = 'Gold Cross'

    with open(FUND_KDJ_DICT_NAME, 'wb') as f:
        pickle.dump(funds_dict, f)

else:
    with open(FUND_KDJ_DICT_NAME, 'rb') as f:
        funds_dict = pickle.load(f)
print(funds_dict['funds df']['名稱'])
print(pd.DataFrame(funds_dict['Every OBV']))
print(pd.DataFrame({
    "名稱": funds_dict['funds df']['名稱'].iloc[1:].tolist(),
    "OBV": funds_dict['Every OBV']
    }))
