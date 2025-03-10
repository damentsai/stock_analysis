import matplotlib.pyplot as plt
import twstock
import mplfinance as mpf
import pandas as pd


target_stock = '2330'  # 股票代碼
stock = twstock.Stock(target_stock)
target_price = stock.fetch_from(2020, 5)
name_attribute = ['Date', 'Capacity', 'Turnover', 'Open', 'High', 'Low', 'Close', 'Change', 'Transcation']
df = pd.DataFrame(columns=name_attribute, data=target_price)
filename = f'./data/{target_stock}.csv'
df.to_csv(filename)
df = pd.read_csv(filename)

df.rename(columns={'Turnover': 'Volume'}, inplace=True)  # mplfinance lib辨認需求(成交量)
df.index = pd.to_datetime(df['Date'])  # 第一欄改成 Date 的格式

# 改成台灣版本的漲跌習慣的顏色, mpf吃Open High, Low, Close, Volume 
mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
s = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)

kwargs = dict(type='candle', mav=(5, 20, 60), volume=True, figratio=(10, 8), figscale=0.75, title=target_stock, style=s)

mpf.plot(df, **kwargs)

#  周均線、月均線、季均線(三月)、半年均線、年均線，會找前面n個做移動平均線
df['1ma'] = df['Close'].rolling(window=1).mean()  # 日線，raw
df['5ma'] = df['Close'].rolling(window=5).mean()  # 周均線
df['20ma'] = df['Close'].rolling(window=20).mean()  # 月均線
df['60ma'] = df['Close'].rolling(window=60).mean()  # 季均線
df['120ma'] = df['Close'].rolling(window=120).mean()  # 半年均線
df['240ma'] = df['Close'].rolling(window=240).mean()  # 年均線

# 要分析的股票是長期的操作，這邊比較希望有超過一年的歷史淨值資料
assert df.shape[0] > 240, "total dates should be larger than 240 for mean average analysis"

plt.subplot(211)
plt.plot(df['Date'], df['1ma'], label='1MA')
plt.plot(df['Date'], df['5ma'], label='5MA')
plt.plot(df['Date'], df['20ma'], label='20MA')
plt.plot(df['Date'], df['60ma'], label='60MA')
plt.plot(df['Date'], df['120ma'], label='120MA')
plt.plot(df['Date'], df['240ma'], label='240MA')
plt.xticks([])
plt.legend()

plt.subplot(212)
plt.bar(df['Date'], df['Volume'], label='Volume')
plt.xticks([])
plt.ylabel('trade money (NTD)')
plt.legend()
plt.show()

# 回傳最近n天內的實際股價淨值最大和最小值 (無所謂益)，也就是截止到最後一天的收盤價格
# 回傳最近一天和過往的比較，當然用時時報價的數值加入作為買賣比較
n = 120  # 最近幾個工作天n當作買入或賣出的考量
latest_price = df['Close'].tail(1).iloc[0]
# latest_price = 手key

last_n_data = df['Close'].tail(n)
last_n_data_min = min(last_n_data)
last_n_data_max = max(last_n_data)
print(last_n_data_min, last_n_data_max)

# 用來判斷明天要不要買進，
# 回傳最近一天和過往日線做的比較
ratio = (latest_price - last_n_data_min) / (last_n_data_max - last_n_data_min)
print(f"對於日線，近{n}天的相對漲幅內處在的比例：{(ratio*100):.2f}%")
if (ratio > 1):
    print(f"歷史最高價，不建議買入，極度適合賣出")
elif (ratio <= 1 and ratio >= 0.9):
    print(f"不建議買入，相當適合賣出")
elif (ratio <= 0.1 and ratio >=0):
    print(f"若對於該股票相當有信心回漲，當適合買入或進場，否則考慮保本才售出")
elif (ratio < 0):
    print(f"若對於該股票相當有信心回漲，極度適合進場或大量買入，否則考慮保本認賠殺出")
else:
    print(f"保持穩健的定期定額買入，任何操作都不推薦，因為要賺的是穩健的錢")


# 當然當前淨值也可以跟月線做比較，但我喜歡跟周線做比較
ma_compare = '5ma'
assert ma_compare in df.columns, "The ma doesn't exist"
last_n_data_ma = df[ma_compare].tail(n)
last_n_data_ma_min = min(last_n_data_ma)
last_n_data_ma_max = max(last_n_data_ma)
print(last_n_data_ma_min, last_n_data_ma_max)
ratio_ma = (latest_price - last_n_data_ma_min) / (last_n_data_ma_max - last_n_data_ma_min)
print(f"對於均線{ma_compare}，近{n}天處在的比例：{(ratio_ma * 100):.2f}%")
if (ratio_ma > 1):
    print(f"歷史最高價，不建議買入，極度適合賣出")
elif (ratio_ma <= 1 and ratio_ma >= 0.9):
    print(f"不建議買入，相當適合賣出")
elif (ratio_ma <= 0.1 and ratio_ma >=0):
    print(f"若對於該股票相當有信心回漲，當適合買入或進場，否則考慮保本才售出")
elif (ratio_ma < 0):
    print(f"若對於該股票相當有信心回漲，極度適合進場或大量買入，否則考慮保本認賠殺出")
else:
    print(f"保持穩健的定期定額買入，任何操作都不推薦，因為要賺的是穩健的錢")

