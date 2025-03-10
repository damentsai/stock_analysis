import numpy as np
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
# 判斷股票代碼屬於上市還是上櫃
TW_csv = 't187ap03_L.csv'  # 上市股票表
TWO_csv = 't187ap03_O.csv'  # 上櫃股票表
TW = pd.read_csv(TW_csv)
TWO = pd.read_csv(TWO_csv)
target_stock = '3529'
TW = TW[['公司代號', '公司簡稱']]
TWO = TWO[['公司代號', '公司簡稱']]

def TWorTWO(target_stock, TW=TW, TWO=TWO):
    if int(target_stock) in TW['公司代號'].tolist():
        return f'{target_stock}.TW'

    elif int(target_stock) in TWO['公司代號'].tolist():
        return f'{target_stock}.TWO'

    else:
        print("THE TW STOCK DONNOT EXIST")
        return


# 使用 yf 回傳和 twstock 排列一致的 dataframe

tsmc = yf.Ticker('2330.TW')
hist = tsmc.history(period='1mo', interval='1d', start='2024-05-01',
                    )

hist = pd.DataFrame(hist)
mpf.plot(hist, type='candle', style='charles', title='2330', volume=True)
print(hist.columns)

a = yf.download('2330.TW', period='6mo', interval='1d')
a = yf.download('2330.TW', start='2024-06-01', interval='1d')
print(a.index)

start = '2024-06-01'
def ret(target_stock, start=start):
    df = yf.download(TWorTWO(target_stock), start=start, interval='1d')
    return df

print(ret('2330'))