import pandas as pd
import numpy as np
import requests
import datetime
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rc('font', family='Microsoft JhengHei')


today = datetime.datetime.today().strftime('%y%m%d')
ticker = 'aCDD04'  # 安聯

try:
    url_df = f'https://www.moneydj.com/funddj/yp/yp011000.djhtm?a={ticker}'
    fund_name = pd.read_html(url_df)[3][3][0]

    url = f'https://www.moneydj.com/funddj/yp/yp013000.djhtm?a={ticker}'
    data = pd.read_html(url)
    df = data[8]  # 多嘗試幾個index，pd read_html就可以找到對的表格了
    first_part = df.iloc[:, :4]  # 前兩列
    second_part = df.iloc[1:, 4:]  # 後兩列
    second_part.columns = [0, 1, 2, 3]  # columns 校準
    columns = first_part.columns[:4]  # [投資名稱  投資(千股)    比例      增減]
    df = pd.concat([first_part, second_part], axis=0, ignore_index=True)
    for (i, stock) in enumerate(df.iloc[:, 0].isnull()):
        if df.iloc[:, 0].isnull()[i]:
            df = df.drop([i], axis=0)

    for (i, stock) in enumerate(df.iloc[:, 3].isnull()):
        print(i, stock)
        if i != 0:
            if df.iloc[:, 3].isnull()[i]:
                df.iloc[i, 3] = 0.0
            else:
                df.iloc[i, 3] = df.iloc[i, 3].replace('%', '')

    df.iloc[1:, 2] = pd.to_numeric(df.iloc[1:, 2]) / 100
    df.iloc[1:, 3] = pd.to_numeric(df.iloc[1:, 3]) / 100
    # print(df)

    # 找到基金投資股票的代碼。
    whole_stock_url = "https://histock.tw/stock/rank.aspx?p=all"
    whole_stock = pd.read_html(whole_stock_url)
    whole_stock = whole_stock[0]
    # print(whole_stock.head())
    whole_stock = whole_stock[['代號▼', '名稱▼']]
    df['代號'] = None
    for (i, stock) in enumerate(df.iloc[1:, 0]):
        # print(df.iloc[i+1, 0])
        idx = whole_stock.index[whole_stock['名稱▼'] == df.iloc[i + 1, 0]]
        df['代號'][i + 1] = whole_stock.iloc[idx, 0]
        print(type(whole_stock.iloc[idx, 0]))
        # df.at[i+1, '公司代號'] = whole_stock.iloc[idx, 1]
    print(df)

except Exception as e:
    print(e)




plt.pie(df.iloc[1:, 2],
        radius=1.4,
        labels=df.iloc[1:, 0],
        autopct='%.1f%%')   # %.1f%% 表示顯示小數點一位的浮點數，後方加上百分比符號
plt.title(f'{fund_name}各股資金持有比例 (股價x股數)')
plt.show()

