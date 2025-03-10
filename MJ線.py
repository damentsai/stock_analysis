import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import yfinance as yf

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

# MACD 柱狀體 + J 線
# 當 J 線穿過 MACD 的零線時，且向上穿過與多方強度柱體重疊，向下穿過與空方柱體重疊時，分別可以做為做多或做空的依據，
# 否則是J線穿過零線是無效的訊號，且當MACD柱體太小代表震盪或系統重整，不建議操作
def EMA(data, days, pre_mode):
    data_ema = []
    if (pre_mode=='nan'):
        for i in range(days):
            data_ema.append(data[days])
            print(data_ema[i])
    elif (pre_mode=='avg'):
        for i in range(days):
            data_ema.append(sum(data[:days])/days)
    alpha = 2 / (days + 1)
    for i in range(days, len(data)):
        data_ema.append(alpha * data[i] + (1 - alpha) * data_ema[i-1])

    return data_ema

target_stock = '2330'  # 股票代碼
df = yf.download(TWorTWO(target_stock), start=start, interval='1d')
filename = f'./data/{target_stock}.csv'
df.to_csv(filename)
df = pd.read_csv(filename)

n = 14  # 定義windows大小
# 第一步：計算RSV
df['period high'] = df['High'].rolling(window=n).max()  # 日線，raw
df['period low'] = df['Low'].rolling(window=n).min()  # 日線，raw
df['RSV'] = (df['Close'] - df['period low']) / (df['period high'] - df['period low'])
df['K'] = None
df.at[0:n, 'K'] = 0.5
df.at[0:n, 'RSV'] = 0.5
for i in range(1, len(df)):
    df.iloc[i, df.columns.get_loc('K')] = 1/3 * df.iloc[i, df.columns.get_loc('RSV')] + 2/3 * df.iloc[
        i-1, df.columns.get_loc('K')]
df['D'] = None
df.at[0:n, 'D'] = 0.5
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



fig, ax1 = plt.subplots()
colors = ['red' if val >= 0 else 'green' for val in df['MACD']]
print(colors)
plt.bar(df['Date'], df['MACD'], label='MACD', color=colors)

ax2 = ax1.twinx()
ax2.plot(df['Date'], df['J']-0.5, label='J', color='k')
ax1.axhline(0, color='gray', linestyle='--', linewidth=0.8)
ax2.axhline(0, color='gray', linestyle='--', linewidth=0.8)

# 自動調整 y 軸範圍
ax1.set_ylim(auto=True)  # 讓左側 y 軸自動縮放
ax2.set_ylim(auto=True)  # 讓右側 y 軸自動縮放

# 確保 y=0 在中間
# 先獲取目前的 y 軸範圍
y1_min, y1_max = ax1.get_ylim()
y2_min, y2_max = ax2.get_ylim()
# 設定左側和右側 y 軸的範圍，確保 y=0 在中間
ax1.set_ylim(-max(abs(np.array([y1_min, y1_max]))), max(abs(np.array([y1_min, y1_max]))))
ax2.set_ylim(-max(abs(np.array([y2_min, y2_max]))), max(abs(np.array([y2_min, y2_max]))))
plt.title('MJ index')
plt.xticks([])
plt.legend()
plt.show()
