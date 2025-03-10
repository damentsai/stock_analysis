import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import twstock
import matplotlib
import yfinance as yf
matplotlib.rcParams['font.family'] = ['Microsoft JhengHei', 'Calibri']  # 设置字体家族
plt.rcParams['axes.unicode_minus'] = False

# MACD 聽說是指標之王，想說這裡也順便實作了解，後續聽說還有 MACD + KD = MJ 指標，蠻酷的
# MACD (mean average convergence/divergence)，描述兩均線的聚散關係
# MACD 顯示多方或空方的強度變化，無法用來未來股價趨勢，因為幾乎是延遲消息
# MACD 需要和其他指標做配合，同樣不能直接使用動作
# 有人說 MACD 是比較適用短線交易的指標(?
# 首先要先計算 指數移動平均EMA，EMA有別於一般均線，過去的幾天的影響權重會隨指數遞減，至於遞減的速度和取前幾項(trim, truncate)都可自定義
# EMA 較 MA 能反映股價波動的敏感特徵
# 今天EMA數值 = 今天股價 * alpha + 昨天EMA數值 * (1-alpha)
# 其中昨天EMA數值就是代表歷史對今天的影響，是從歷史慢慢迭代計算出來的
# 對於最一般的MACD計算：
# 首先計算26天和12天的EMA線，兩線相減得到的線稱為diff，又稱為乖離率
# 接著，計算diff的九日EMA
# 最後diff與九日EMA相減，獲得柱狀圖，稱為MACD，說明當前空方或多方力量的強弱
# 柱狀圖與diff背離之時，就是做多或做空的可能選項

# 以下演算法分三步驟計算：
# 第一步：初始值填滿，前幾天的EMA以平均值代表取代NAN
# 第二步：迭代計算第 天數+1 之後所有的 EMA
# 第三步：兩欄相減得diff
# 第四步：計算九天的diff EMA
# 第五步：迭代計算第 天數+1 之後的 EMA
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

def VolColor(df):
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
    return vol_colors

# 判斷股票代碼屬於上市還是上櫃

target_stock = '2330'
TW = TW[['公司代號', '公司簡稱']]
TWO = TWO[['公司代號', '公司簡稱']]
df = yf.download(TWorTWO(target_stock), start=start, interval='1d')
filename = f'./data/{target_stock}.csv'
df.to_csv(filename)
df = pd.read_csv(filename)
df['Date'] = df.index

df['26ema'] = EMA(df['Close'], days=26, pre_mode='nan')
df['12ema'] = EMA(df['Close'], days=12, pre_mode='nan')
df['diff'] = df['12ema'] - df['26ema']
df['dea'] = EMA(df['diff'], days=9, pre_mode='avg')
df['MACD'] = df['diff'] - df['dea']

plt.suptitle(f'stock {TWorTWO(target_stock)}')
plt.subplot(311)
plt.title('MACD長週期與短週期股價的指數移動平均線')
plt.plot(df['Date'], df['26ema'], label='26EMA')
plt.plot(df['Date'], df['12ema'], label='12EMA')
plt.ylabel('台幣 (NTD)')
plt.xticks([])
plt.legend()
plt.subplot(312)
plt.plot(df['Date'], df['diff'], label='DIFF')
plt.plot(df['Date'], df['dea'], label='DEA')
plt.bar(df['Date'], df['MACD'], label='MACD')
plt.title('MACD均線的乖離率與它的指數移動平均')
plt.ylabel('台幣 (NTD)')
plt.xticks([])
plt.legend()

plt.subplot(313)
vol_colors = VolColor(df)
plt.bar(df['Date'], df['Volume'], label='Volume', color=vol_colors)
plt.xticks([])
plt.ylabel('台幣 (NTD)')
plt.title('成交量、成交金額')
plt.legend()
plt.show()

# for i in range(1, len(df)):
#     df.iloc[i, df.columns.get_loc('D')] = 1 / 3 * df.iloc[i, df.columns.get_loc('K')] + 2 / 3 * df.iloc[
#         i - 1, df.columns.get_loc('D')]
