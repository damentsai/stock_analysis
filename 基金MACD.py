import pandas as pd
import numpy as np
import pickle
import requests
import datetime
import twstock
import matplotlib
import matplotlib.pyplot as plt

def EMA(data, days, pre_mode):
    data_ema = []
    if (pre_mode=='nan'):
        for i in range(days):
            data_ema.append(data[days])
            # print(data_ema[i])
    elif (pre_mode=='avg'):
        for i in range(days):
            data_ema.append(sum(data[:days])/days)
    alpha = 2 / (days + 1)
    for i in range(days, len(data)):
        data_ema.append(alpha * data[i] + (1 - alpha) * data_ema[i-1])

    return data_ema


matplotlib.rc('font', family='Microsoft JhengHei')
today = datetime.datetime.today().strftime('%y%m%d')
ticker = 'aCDD04'  # 安聯
RERUN = False
FUND_KDJ_DICT_NAME = 'funds_MACD.pkl'

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
        for (i, stock) in enumerate(funds_df.iloc[1:, 0]):
            idx = whole_stock.index[whole_stock['名稱▼'] == funds_df.iloc[i + 1, 0]].tolist()[0]
            #print(idx)
            funds_df.loc[i+1, '代號'] = whole_stock.loc[idx, '代號▼']
    except Exception as e:
        print(e)


    # print(funds_df)
    funds_dict = {}
    funds_dict['funds name'] = fund_name
    n = 14  # 定義KDJ使用的 rolling windows 大小
    for i in range(1, len(funds_df)):
        print(funds_df.loc[i, '代號'])
        target_stock = funds_df.loc[i, '代號']
        stock = twstock.Stock(target_stock)
        # print(funds_df.loc[i, '代號'].tolist(0))
        target_price = stock.fetch_from(2023, 9)
        name_attribute = ['Date', 'Capacity', 'Turnover', 'Open', 'High', 'Low', 'Close', 'Change', 'Transcation']
        df = pd.DataFrame(columns=name_attribute, data=target_price)  # 初始化
        filename = f'./data/{target_stock}.csv'
        df.to_csv(filename)
        df = pd.read_csv(filename)
        df.rename(columns={'Turnover': 'Volume'}, inplace=True)  # mplfinance lib辨認需求(成交量)
        df.index = pd.to_datetime(df['Date'])  # 第一欄改成 Date 的格式
        funds_dict['Date'] = df['Date']

        df['26ema'] = EMA(df['Close'], days=26, pre_mode='nan')
        df['12ema'] = EMA(df['Close'], days=12, pre_mode='nan')
        df['diff'] = df['12ema'] - df['26ema']
        # df['dea'] = EMA(df['diff'], days=9, pre_mode='avg')
        # df['MACD'] = df['diff'] - df['dea']
        funds_dict[target_stock] = df
    funds_dict['funds df'] = funds_df
    with open(FUND_KDJ_DICT_NAME, 'wb') as f:
        pickle.dump(funds_dict, f)

else:
    with open(FUND_KDJ_DICT_NAME, 'rb') as f:
        funds_dict = pickle.load(f)

fund_name = funds_dict['funds name']
funds_df = funds_dict['funds df']
funds_dict['weighted diff'] = [0 for _ in range(len(funds_dict['Date']))]
funds_dict['weighted dea'] = [0 for _ in range(len(funds_dict['Date']))]
funds_dict['weighted MACD'] = [0 for _ in range(len(funds_dict['Date']))]
total_weight = sum(funds_df.iloc[1:, 2])
# print(total_weight)
# 按照資金權重去做加總，得到加權的KDJ值
for i in range(1, len(funds_df)):
    target_stock = funds_df.loc[i, '代號']
    weight = funds_df.iloc[i, 2] / total_weight
    print(target_stock, np.array(funds_dict['weighted diff']).shape, np.array(funds_dict[target_stock]['diff']).shape)
    funds_dict['weighted diff'] = (np.array(funds_dict['weighted diff']) + weight * np.array(funds_dict[target_stock]['diff'])).tolist()
funds_dict['weighted dea'] = EMA(funds_dict['weighted diff'], days=9, pre_mode='avg')
funds_dict['weighted MACD'] = (np.array(funds_dict['weighted diff']) - np.array(funds_dict['weighted dea'])).tolist()

plt.plot(funds_dict['Date'], funds_dict['weighted diff'], label='weighted DIFF')
plt.plot(funds_dict['Date'], funds_dict['weighted dea'], label='weighted DEA')
plt.bar(funds_dict['Date'], funds_dict['weighted MACD'], label='weighted MACD')
plt.title(f'{fund_name}基金MACD均線的乖離率與它的指數移動平均')
plt.ylabel('台幣 (NTD)')
plt.xticks([])
plt.legend()

plt.show()




