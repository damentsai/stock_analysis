import pandas as pd
import numpy as np
import pickle
import requests
import datetime
import twstock
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rc('font', family='Microsoft JhengHei')
today = datetime.datetime.today().strftime('%y%m%d')
ticker = 'aCDD04'  # 安聯
RERUN = True
FUND_KDJ_DICT_NAME = 'funds_KDJ.pkl'

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


    print(funds_df)
    funds_dict = {}
    funds_dict['funds name'] = fund_name
    n = 14  # 定義KDJ使用的 rolling windows 大小
    for i in range(1, len(funds_df)):
        print(funds_df.loc[i, '代號'])
        target_stock = funds_df.loc[i, '代號']
        stock = twstock.Stock(target_stock)
        # print(funds_df.loc[i, '代號'].tolist(0))
        target_price = stock.fetch_from(2024, 2)
        name_attribute = ['Date', 'Capacity', 'Turnover', 'Open', 'High', 'Low', 'Close', 'Change', 'Transcation']
        df = pd.DataFrame(columns=name_attribute, data=target_price)  # 初始化
        filename = f'./data/{target_stock}.csv'
        df.to_csv(filename)
        df = pd.read_csv(filename)
        df.rename(columns={'Turnover': 'Volume'}, inplace=True)  # mplfinance lib辨認需求(成交量)
        df.index = pd.to_datetime(df['Date'])  # 第一欄改成 Date 的格式
        funds_dict['Date'] = df['Date']

        # 第一步：計算RSI
        df['period high'] = df['High'].rolling(window=n).max()  # 日線，raw
        df['period low'] = df['Low'].rolling(window=n).min()  # 日線，raw
        df['RSI'] = (df['Close'] - df['period low']) / (df['period high'] - df['period low'])
        # 第二步：計算 K 值
        df['K'] = None
        df.at[0:n, 'K'] = 0.5
        df.at[0:n, 'RSI'] = 0.5
        for i in range(1, len(df)):
            df.iloc[i, df.columns.get_loc('K')] = 1/3 * df.iloc[i, df.columns.get_loc('RSI')] + 2/3 * df.iloc[
                i-1, df.columns.get_loc('K')]

        # 第三步：計算 D 值
        df['D'] = None
        df.at[0:n, 'D'] = 0.5
        for i in range(1, len(df)):
            df.iloc[i, df.columns.get_loc('D')] = 1 / 3 * df.iloc[i, df.columns.get_loc('K')] + 2 / 3 * df.iloc[
                i - 1, df.columns.get_loc('D')]

        # 第四步：計算 J 值
        df['J'] = 3 * df['K'] - 2 * df['D']

        funds_dict[target_stock] = df
    funds_dict['funds df'] = funds_df
    with open(FUND_KDJ_DICT_NAME, 'wb') as f:
        pickle.dump(funds_dict, f)

else:
    with open(FUND_KDJ_DICT_NAME, 'rb') as f:
        funds_dict = pickle.load(f)

fund_name = funds_dict['funds name']
funds_df = funds_dict['funds df']
funds_dict['weighted RSI'] = [0 for _ in range(len(funds_dict['Date']))]
funds_dict['weighted K'] = [0 for _ in range(len(funds_dict['Date']))]
funds_dict['weighted D'] = [0 for _ in range(len(funds_dict['Date']))]
funds_dict['weighted J'] = None
total_weight = sum(funds_df.iloc[1:, 2])
# print(total_weight)
# 按照資金權重去做加總，得到加權的KDJ值
print(len(funds_dict['Date']), np.array(funds_dict['weighted RSI']).shape, funds_dict['2330']['RSI'].shape)

for i in range(1, len(funds_df)):
    target_stock = funds_df.loc[i, '代號']
    weight = funds_df.iloc[i, 2] / total_weight
    print(target_stock, len(funds_dict['Date']), np.array(funds_dict['weighted RSI']).shape, funds_dict['2330']['RSI'].shape)
    funds_dict['weighted RSI'] = (np.array(funds_dict['weighted RSI']) + weight * np.array(funds_dict[target_stock]['RSI'])).tolist()
    funds_dict['weighted K'] = (np.array(funds_dict['weighted K']) + weight * np.array(funds_dict[target_stock]['K'])).tolist()
    funds_dict['weighted D'] = (np.array(funds_dict['weighted D']) + weight * np.array(funds_dict[target_stock]['D'])).tolist()

funds_dict['weighted J'] = (3*np.array(funds_dict['weighted K']) - 2*np.array(funds_dict['weighted D'])).tolist()

plt.plot(funds_dict['Date'], funds_dict['weighted RSI'], label='weighted RSI')
plt.plot(funds_dict['Date'], funds_dict['weighted K'], label='weighted K')
plt.plot(funds_dict['Date'], funds_dict['weighted D'], label='weighted D')
plt.plot(funds_dict['Date'], funds_dict['weighted J'], label='weighted J')
plt.axhline(y=0, color='gray', linestyle='--')
plt.axhline(y=0.2, color='gray', linestyle='--')
plt.axhline(y=0.8, color='gray', linestyle='--')
plt.axhline(y=1, color='gray', linestyle='--')
plt.xticks([])
plt.ylabel('ratio')
plt.title(f'{fund_name}KDJ指標圖')
plt.legend()
plt.show()





