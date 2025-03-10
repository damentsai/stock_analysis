import pandas as pd
import numpy as np
import pickle
import requests
import datetime
import twstock
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
from datetime import date
import time

TW_csv = 't187ap03_L.csv'  # 上市股票表
TWO_csv = 't187ap03_O.csv'  # 上櫃股票表
TW = pd.read_csv(TW_csv)
TWO = pd.read_csv(TWO_csv)
start = '2024-01-01'

def TWorTWO(target_stock, TW=TW, TWO=TWO):
    if int(target_stock) in TW['公司代號'].tolist():
        return f'{target_stock}.TW'

    elif int(target_stock) in TWO['公司代號'].tolist():
        return f'{target_stock}.TWO'

    else:
        print("THE TW STOCK DONNOT EXIST")
        return

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


matplotlib.rcParams['font.family'] = ['Microsoft JhengHei', 'Calibri']  # 设置字体家族
plt.rcParams['axes.unicode_minus'] = False
today = date.today()
ticker = 'aCDD04'  # 安聯
n = 9  # 定義KDJ使用的 rolling windows 大小
RERUN = True
FUND_KDJ_DICT_NAME = f'funds_{ticker}_{today}_MJ.pkl'

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

    for i in range(1, len(funds_df)):
        print(funds_df.iloc[i, funds_df.columns.get_loc('代號')])
        target_stock = funds_df.iloc[i, funds_df.columns.get_loc('代號')]

        # df = yf.download(TWorTWO(target_stock), start=start, interval='1d')

        while(1):
            try:
                df = yf.download(TWorTWO(target_stock), start=start, interval="1d")
                if not df.empty:
                    print("下載成功！")
                    break  # 成功後跳出迴圈
            except Exception as e:
                print(f"下載失敗: {e}，正在重試...")
                time.sleep(1)

        filename = f'./data/{target_stock}.csv'
        df.to_csv(filename)
        df = pd.read_csv(filename)

        df.rename(columns={'Price': 'Date'}, inplace=True)  # mplfinance lib辨認需求(成交量)
        df = df.drop([0, 1], axis=0)
        df.reset_index(drop=True, inplace=True)
        print(df.head())
        columns_to_convert = ['Close', 'High', 'Low', 'Open', 'Volume']
        df['Close'] = pd.to_numeric(df['Close'])
        df['Open'] = pd.to_numeric(df['Open'])
        df['High'] = pd.to_numeric(df['High'])
        df['Low'] = pd.to_numeric(df['Low'])
        df['Volume'] = pd.to_numeric(df['Volume'])

        df.rename(columns={'Turnover': 'Volume'}, inplace=True)  # mplfinance lib辨認需求(成交量)
        df.index = pd.to_datetime(df['Date'])  # 第一欄改成 Date 的格式
        funds_dict['Date'] = df['Date']

        # 第一步：計算RSI
        df['period high'] = df['High'].rolling(window=n).max()  # 日線，raw
        df['period low'] = df['Low'].rolling(window=n).min()  # 日線，raw
        df['RSI'] = (df['Close'] - df['period low']) / (df['period high'] - df['period low'])
        # 第二步：計算 K 值
        df['K'] = None
        df.iloc[0:n, df.columns.get_loc('K')] = 0.5
        df.iloc[0:n, df.columns.get_loc('RSI')] = 0.5
        for i in range(1, len(df)):
            df.iloc[i, df.columns.get_loc('K')] = 1/3 * df.iloc[i, df.columns.get_loc('RSI')] + 2/3 * df.iloc[
                i-1, df.columns.get_loc('K')]

        # 第三步：計算 D 值
        df['D'] = None
        df.iloc[0:n, df.columns.get_loc('D')] = 0.5
        for i in range(1, len(df)):
            df.iloc[i, df.columns.get_loc('D')] = 1 / 3 * df.iloc[i, df.columns.get_loc('K')] + 2 / 3 * df.iloc[
                i - 1, df.columns.get_loc('D')]

        # 第四步：計算 J 值
        df['J'] = 3 * df['K'] - 2 * df['D']

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
funds_dict['weighted RSI'] = [0 for _ in range(len(funds_dict['Date']))]
funds_dict['weighted K'] = [0 for _ in range(len(funds_dict['Date']))]
funds_dict['weighted D'] = [0 for _ in range(len(funds_dict['Date']))]
funds_dict['weighted J'] = None
funds_dict['weighted diff'] = [0 for _ in range(len(funds_dict['Date']))]
funds_dict['weighted dea'] = [0 for _ in range(len(funds_dict['Date']))]
funds_dict['weighted MACD'] = [0 for _ in range(len(funds_dict['Date']))]
total_weight = sum(funds_df.iloc[1:, 2])
# print(total_weight)
# 按照資金權重去做加總，得到加權的KDJ值
# print(len(funds_dict['Date']), np.array(funds_dict['weighted RSI']).shape, funds_dict['2330']['RSI'].shape)

for i in range(1, len(funds_df)):
    target_stock = funds_df.iloc[i, funds_df.columns.get_loc('代號')]
    weight = funds_df.iloc[i, 2] / total_weight

    # 可刪，有些股票沒有更新完全所以不能分析
    if len(funds_dict[target_stock]['RSI']) < len(funds_dict['Date']):
        print(target_stock, 'wrong')
        continue

    print(target_stock, len(funds_dict['Date']), np.array(funds_dict['weighted RSI']).shape,
          funds_dict['2330']['RSI'].shape)
    funds_dict['weighted RSI'] = (np.array(funds_dict['weighted RSI']) + weight * np.array(funds_dict[target_stock]['RSI'])).tolist()
    funds_dict['weighted K'] = (np.array(funds_dict['weighted K']) + weight * np.array(funds_dict[target_stock]['K'])).tolist()
    funds_dict['weighted D'] = (np.array(funds_dict['weighted D']) + weight * np.array(funds_dict[target_stock]['D'])).tolist()
    funds_dict['weighted diff'] = (np.array(funds_dict['weighted diff']) + weight * np.array(funds_dict[target_stock]['diff'])).tolist()
funds_dict['weighted J'] = (3*np.array(funds_dict['weighted K']) - 2*np.array(funds_dict['weighted D'])).tolist()
funds_dict['weighted dea'] = EMA(funds_dict['weighted diff'], days=9, pre_mode='avg')
funds_dict['weighted MACD'] = (np.array(funds_dict['weighted diff']) - np.array(funds_dict['weighted dea'])).tolist()

# 基金淨值查詢，針對安聯官網提供的下載表格，net value (nw)，這個每天都要下載一次
nw_url = 'https://prd-ap-fund-sc.allianzgi.com/api/fund/exportnetworthdetails/?SalesChannel=tw_endclients&ShareClassId=&SeoName=allianz-global-investors-taiwan-technology-fund&Language=zh-TW&IsuserLoggedIn=False&IsLocalLanguage=False&DatasourceId={379E1EBD-AB87-4C7A-87AD-30A119A3C3B6}'
nw_save_path = 'data/funds_history.xlsx'
response = requests.get(nw_url)
with open(nw_save_path, 'wb') as f:
    f.write(response.content)
print('net worth excel data download and saved')
df = pd.read_excel(nw_save_path)
print(df.head(30))
days = len(funds_dict['Date'])
print(df.iloc[8:8+days, :])
nw = df.iloc[8:8+days, :].iloc[::-1].reset_index(drop=True)
nw.columns = ['Date', 'Fund Net Value']
nw['Date'] = pd.to_datetime(nw['Date'], format='%Y/%m/%d')
nw.index = pd.to_datetime(nw['Date'])
nw['Fund Net Value'] = pd.to_numeric(nw['Fund Net Value'], errors='coerce')


fig, ax1 = plt.subplots(4, 1)
colors = ['red' if val >= 0 else 'green' for val in funds_dict['weighted MACD']]
y1 = np.array(funds_dict['weighted MACD'])
y2 = np.array(funds_dict['weighted J'])-0.5
ax1[0].plot(funds_dict['Date'], funds_dict['weighted diff'], label='weighted DIFF')
ax1[0].bar(funds_dict['Date'], y1, label='weighted MACD', color=colors)
# ax2.set_ylim([-2, 2])
ax2 = ax1[0].twinx()
ax2.plot(funds_dict['Date'], y2, label='weighted J', color='k')
plt.title(f'{fund_name}weighted MJ 指標')
ax1[0].set_xticks([])
ax1[0].legend(loc='upper left')
ax2.legend(loc='lower left')
ax1[0].axhline(0, color='gray', linestyle='--', linewidth=0.8)
ax2.axhline(0, color='gray', linestyle='--', linewidth=0.8)

# 自動調整 y 軸範圍
ax1[0].set_ylim(auto=True)  # 讓左側 y 軸自動縮放
ax2.set_ylim(auto=True)  # 讓右側 y 軸自動縮放

# 確保 y=0 在中間
# 先獲取目前的 y 軸範圍
y1_min, y1_max = ax1[0].get_ylim()
y2_min, y2_max = ax2.get_ylim()
# 設定左側和右側 y 軸的範圍，確保 y=0 在中間
ax1[0].set_ylim(-max(abs(np.array([y1_min, y1_max]))), max(abs(np.array([y1_min, y1_max]))))
ax2.set_ylim(-max(abs(np.array([y2_min, y2_max]))), max(abs(np.array([y2_min, y2_max]))))

plt.subplot(412)
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
plt.legend(loc='upper left')

plt.subplot(413)
plt.plot(funds_dict['Date'], funds_dict['weighted diff'], label='weighted DIFF')
plt.plot(funds_dict['Date'], funds_dict['weighted dea'], label='weighted DEA')
plt.bar(funds_dict['Date'], funds_dict['weighted MACD'], label='weighted MACD')
plt.title(f'{fund_name}基金MACD均線的乖離率與它的指數移動平均')
plt.ylabel('台幣 (NTD)')
plt.xticks([])
plt.legend()

# 繪製淨值
plt.subplot(414)
plt.plot(nw['Date'], nw['Fund Net Value'], label='Fund Net Value')
# plt.xticks(rotation=45)  # 旋转 x 轴刻度
plt.title('History of Net Values of the Fund')
plt.legend()
plt.xlabel('Date')  # 添加 x 轴标签
plt.ylabel('Fund Net Value (NTD)')  # 添加 y 轴标签
# 设置日期格式
ax = plt.gca()  # 获取当前轴
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # 设置主刻度格式
ax.xaxis.set_major_locator(mdates.DayLocator(interval=30))  # 每天一个刻度
ax.yaxis.set_major_locator(mdates.DayLocator(interval=10))  # 每天一个刻度
ax.xaxis.set_major_locator(mdates.AutoDateLocator())  # 視窗自由拖動
plt.show()
