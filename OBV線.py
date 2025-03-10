import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib
import matplotlib.dates as mdates
from datetime import date

matplotlib.rcParams['font.family'] = ['Microsoft JhengHei', 'Calibri']  # 设置字体家族
plt.rcParams['axes.unicode_minus'] = False
# OBV線 (On Balance Volume) 是少數使用"成交量"作為量化對象的指標，反映了K線價格變化冰山一角下的形貌，也代表該股票的交易熱度
# OBV可以看好大趨勢，是之後將有大漲或大跌的依據
# 新手看價，老手看量就是這個道理，但價格漲跌
# 價格漲跌可以和成交量無關，但是成交量可以預測未來更久的趨勢，也就是目前的上漲或下跌是不是背後有力量在主導
# OBV和K線其實漲跌很高度相關，當股票一直跌，但OBV沒有什麼變化，代表沒有成交量，也不適合做空，反之亦然
# 穩定的漲勢包含價高量增和價低量縮，也就是漲得多跌得少，反之穩定的跌勢就是價高量縮，價低量增
# OBV是前一日的OBV加上今天的(+-)成交量，今天的收盤大於昨天收盤則正，若今天的收盤小於昨天收盤則負，若相等則不增不減
# 對OBV做個均線10MA, 20MA之類的，兩者並列可以得到黃金交叉和死亡交叉
# 這個些OBV產生交叉youtube有人說比KD產生的更早到來，也就是有更早的行情較低的延遲，MACD的交叉也就是零線所發生的位置，描述的是操作的強度變化
# 趨勢描述 | 頂頂高、頂頂低、底底高、底底低: 下一個X比前一個X還要來的O
# 若 OBV 和 K線 趨勢背離，代表未來很可能即將有大趨勢的變化，接下來 OBV 發生交叉可以考慮做空或做多
# OBV 會和移動平均線MA做比較 (為何不用EMA呢??不曉得)


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

target_stock = '2330'  # 股票代碼
df = yf.download(TWorTWO(target_stock), start=start, interval='1d')
filename = f'./data/{target_stock}.csv'
df.to_csv(filename)
df = pd.read_csv(filename)
df['OBV'] = 0
# print(df.loc[df['Date'][1], 'OBV'])
# print(df.iloc[0, df.columns.get_loc('OBV')] +\
#                                              df.iloc[1, df.columns.get_loc('Volume')] * df.iloc[1, df.columns.get_loc('K State')])
vol_colors = ["#EDB120"]
for i in range(1, len(df)):
    if df.iloc[i, df.columns.get_loc('Close')] - df.iloc[i-1, df.columns.get_loc('Close')] > 0:
        sign = 1
        vol_colors.append("red")
    elif df.iloc[i, df.columns.get_loc('Close')] - df.iloc[i-1, df.columns.get_loc('Close')] < 0:
        sign = -1
        vol_colors.append("green")
    else:
        sign = 0
        vol_colors.append("#EDB120")
    df.iloc[i,  df.columns.get_loc('OBV')] = df.iloc[i-1, df.columns.get_loc('OBV')] +\
                                             df.iloc[i, df.columns.get_loc('Volume')] * sign


df['OBV 10ma'] = df['OBV'].rolling(window=10).mean()  # 周均線
df['OBV 20ma'] = df['OBV'].rolling(window=20).mean()  # 周均線

# df['OBV'] = pd.to_numeric(df['OBV'])
print(df['OBV'])

# K 线图绘制
k_color = []
k_lower = []
k_height = []
for i in range(len(df)):
    # 判断涨跌
    if df['Close'][i] > df['Open'][i]:  # 收盘价高于开盘价（上涨）
        k_color.append('red')
        k_lower.append(df['Open'][i])
        k_height.append(df['Close'][i] - df['Open'][i])
    elif df['Close'][i] == df['Open'][i]:
        k_color.append("#EDB120")
        k_lower.append(df['Open'][i])
        k_height.append(df['Close'][i] - df['Open'][i])
    else:  # 收盘价低于开盘价（下跌）
        k_color.append('green')
        k_lower.append(df['Close'][i])
        k_height.append(df['Open'][i] - df['Close'][i])


fig, ax = plt.subplots(3, 1)
plt.suptitle(f'台股代碼{target_stock} 的 OBV & K線 & 成交量')
plt.subplot(311)
plt.bar(df['Date'], height=k_height, bottom=k_lower, width=0.8, color=k_color)
plt.bar(df['Date'], height=df['High']-df['Low'], bottom=df['Low'], width=0.15, color=k_color)
plt.xticks([])
plt.title('日K線圖')
plt.ylabel('台幣 (NTD)')

plt.subplot(312)
plt.bar(df['Date'], df['Volume'], label='Volume', color=vol_colors)
plt.xticks([])
plt.ylabel('台幣 (NTD)')
plt.title('成交量、成交金額')
plt.legend()

plt.subplot(313)
plt.plot(df['Date'], df['OBV'], label='OBV')
plt.plot(df['Date'], df['OBV 10ma'], label='OBV 10ma')
plt.plot(df['Date'], df['OBV 20ma'], label='OBV 20ma')
plt.title('OBV')
plt.ylabel('參考相對強度')
plt.xticks([])
plt.legend()


plt.show()