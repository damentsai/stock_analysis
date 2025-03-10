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
start = '2024-01-01'
n = 9  # 定義KDJ RSI windows大小


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

USA = True
target_stock = '^GSPC'  # 股票代碼
df = yf.download((TWorTWO(target_stock) if not USA else target_stock), start=start, interval='1d')
filename = f'./data/{target_stock}.csv'
df.to_csv(filename)
df = pd.read_csv(filename)
df['OBV'] = 0

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


# 第一步：計算RSV
df['period high'] = df['High'].rolling(window=n).max()  # 日線，raw
df['period low'] = df['Low'].rolling(window=n).min()  # 日線，raw
df['RSI'] = (df['Close'] - df['period low']) / (df['period high'] - df['period low'])
df['K'] = None
df.iloc[0:n, df.columns.get_loc('K')] = 0.5
df.iloc[0:n, df.columns.get_loc('RSI')] = 0.5
for i in range(1, len(df)):
    df.iloc[i, df.columns.get_loc('K')] = 1/3 * df.iloc[i, df.columns.get_loc('RSI')] + 2/3 * df.iloc[
        i-1, df.columns.get_loc('K')]
df['D'] = None
df.iloc[0:n, df.columns.get_loc('D')] = 0.5
for i in range(1, len(df)):
    df.iloc[i, df.columns.get_loc('D')] = 1 / 3 * df.iloc[i, df.columns.get_loc('K')] + 2 / 3 * df.iloc[
        i - 1, df.columns.get_loc('D')]
df['J'] = 3 * df['K'] - 2 * df['D']

df['26ema'] = EMA(df['Close'], days=26, pre_mode='nan')
df['12ema'] = EMA(df['Close'], days=12, pre_mode='nan')
df['diff'] = df['12ema'] - df['26ema']
df['dea'] = EMA(df['diff'], days=9, pre_mode='avg')
df['MACD'] = df['diff'] - df['dea']
df['diff(%)'] = df['diff'] / df['26ema']
df['MACD(%)'] = df['MACD'] / df['dea']

# ATR 作為單獨指標，與均線分別表示市場的波動幅度
# 當天最高最低差、今天最高與昨日收盤差、今天最低宇昨天收盤差 三者最大值
df['ATR'] = None  # average true range
df.at[0, 'ATR'] = 0
for i in range(1, len(df)):
    df.iloc[i, df.columns.get_loc('ATR')] = max(
        abs(df['Close'][i] - df['Open'][i]),
        abs(df['High'][i] - df['Close'][i-1]),
        abs(df['Low'][i] - df['Close'][i-1]),
    )
df['ATR 14ema'] = EMA(df['ATR'], days=14, pre_mode='nan')

# +DM and -DM，Directional Movement 向上(向下)動向，必大於零
# 衡量漲勢和跌勢的同時間的力量
df['mDM'] = None  # -DM
df['pDM'] = None  # +DM
df.at[0, 'mDM'] = 0
df.at[0, 'pDM'] = 0
for i in range(1, len(df)):
    df.iloc[i, df.columns.get_loc('pDM')] = max(
        df['High'][i] - df['High'][i-1],
        0
    )
    df.iloc[i, df.columns.get_loc('mDM')] = max(
        df['Low'][i-1] - df['Low'][i],
        0
    )

df['mDM 14ema'] = EMA(df['mDM'], days=14, pre_mode='avg')
df['pDM 14ema'] = EMA(df['pDM'], days=14, pre_mode='avg')

# the positive/negative indicator，上升下降動向指數
df['pDI'] = df['pDM 14ema'] / (df['ATR 14ema']+1e-10) * 100
df['mDI'] = df['mDM 14ema'] / (df['ATR 14ema']+1e-10) * 100

# Directional movement index
df['DX'] = abs(pd.to_numeric((df['pDI'] - df['mDI']) / (df['pDI'] + df['mDI']+1e-10) * 100))
df['ADX'] = EMA(df['DX'], days=14, pre_mode='avg')

plt.figure(num="DX +-DI")
# plt.plot(df['Date'], df['ATR'], label='ATR')
plt.plot(df['Date'], df['pDI'], label='+DI')
plt.plot(df['Date'], df['mDI'], label='-DI')
plt.plot(df['Date'], df['ADX'], label='ADX')
plt.axhline(y=25, color='gray', linestyle='--', linewidth=0.8)
plt.legend()
plt.ylim([0, 100])
plt.xticks([])
plt.title(f'台股代碼{target_stock} 的動向指標')
plt.ylabel('參考相對強度(%)')


fig_num = 5
fig, ax = plt.subplots(fig_num, 1)
plt.suptitle(f'台股代碼{target_stock} 的 OBV & K線 & 成交量 & MJ')
plt.subplot(fig_num, 1, 1)
plt.bar(df['Date'], height=k_height, bottom=k_lower, width=0.8, color=k_color)
plt.bar(df['Date'], height=df['High']-df['Low'], bottom=df['Low'], width=0.15, color=k_color)
plt.xticks([])
plt.title('日K線圖')
plt.ylabel('台幣 (NTD)')

plt.subplot(fig_num, 1, 2)
plt.bar(df['Date'], df['Volume'], label='Volume', color=vol_colors)
plt.xticks([])
plt.ylabel('台幣 (NTD)')
plt.title('成交量、成交金額')
plt.legend()

plt.subplot(fig_num, 1, 3)
plt.plot(df['Date'], df['OBV'], label='OBV')
plt.plot(df['Date'], df['OBV 10ma'], label='OBV 10ma')
plt.plot(df['Date'], df['OBV 20ma'], label='OBV 20ma')
plt.title('OBV')
plt.ylabel('參考相對強度')
plt.xticks([])
plt.legend()

macd_plt = 4
plt.subplot(fig_num, 1, macd_plt)
colors = ['red' if val >= 0 else 'green' for val in df['MACD']]
ax[macd_plt-1].plot(df['Date'], df['diff'], label='DIFF')
ax[macd_plt-1].bar(df['Date'], df['MACD'], label='MACD', color=colors)
ax2 = ax[macd_plt-1].twinx()
ax2.plot(df['Date'], df['J']-0.5, label='J', color='k')
# ax2.plot(df['Date'], df['RSI']-0.5, label='RSI', color='r')
ax[macd_plt-1].axhline(0, color='gray', linestyle='--', linewidth=0.8)
ax2.axhline(0, color='gray', linestyle='--', linewidth=0.8)
ax[macd_plt-1].set_ylim(auto=True)  # 讓左側 y 軸自動縮放
ax2.set_ylim(auto=True)  # 讓右側 y 軸自動縮放
y1_min, y1_max = ax[macd_plt-1].get_ylim()
y2_min, y2_max = ax2.get_ylim()
ax[macd_plt-1].set_ylim(-max(abs(np.array([y1_min, y1_max]))), max(abs(np.array([y1_min, y1_max]))))
ax2.set_ylim(-max(abs(np.array([y2_min, y2_max]))), max(abs(np.array([y2_min, y2_max]))))
plt.title('MJ index')
plt.xticks([])
ax[macd_plt-1].legend()
ax2.legend()

plt.subplot(fig_num, 1, 5)
plt.plot(df['Date'], df['RSI'], label='RSI')
plt.plot(df['Date'], df['K'], label='K')
plt.plot(df['Date'], df['D'], label='D')
plt.plot(df['Date'], df['J'], label='J')
plt.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
plt.axhline(y=0.2, color='gray', linestyle='--', linewidth=0.8)
plt.axhline(y=0.8, color='gray', linestyle='--', linewidth=0.8)
plt.axhline(y=1, color='gray', linestyle='--', linewidth=0.8)
plt.xticks([])
plt.ylabel('ratio')
plt.title('KDJ指標圖')
plt.legend()
plt.show()