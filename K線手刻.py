import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 准备示例数据
data = {
    'Date': ['2024-02-01', '2024-02-02', '2024-02-03', '2024-02-04', '2024-02-05'],
    'Open': [182.91, 188.52, 188.80, 198.53, 193.67],
    'High': [184.00, 190.00, 189.00, 199.00, 194.00],
    'Low': [182.00, 187.00, 187.00, 197.00, 192.00],
    'Close': [183.50, 189.00, 188.80, 198.00, 193.00],
}
df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'])

# 设置绘图参数
fig, ax = plt.subplots()

# K 线图绘制
for i in range(len(df)):
    # 判断涨跌
    if df['Close'][i] >= df['Open'][i]:  # 收盘价高于开盘价（上涨）
        color = 'red'
        lower = df['Open'][i]
        height = df['Close'][i] - df['Open'][i]
    else:  # 收盘价低于开盘价（下跌）
        color = 'green'
        lower = df['Close'][i]
        height = df['Open'][i] - df['Close'][i]

    # 将日期转换为数字
    date_num = mdates.date2num(df['Date'][i])
    print(date_num)
    # 绘制蜡烛
    ax.add_patch(plt.Rectangle((date_num - 0.2, lower), width=0.4, height=height, color=color))

    # 绘制上影线
    ax.plot([date_num, date_num], [df['Low'][i], df['High'][i]], color=color)

# 设置日期格式
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mdates.DayLocator())
plt.xticks(rotation=45)

# 添加标题和标签
plt.title('Candlestick Chart')
plt.xlabel('Date')
plt.ylabel('Price')

plt.show()

# 輸入個股的所有資訊，以dataframe形式
def CandlePlot(df):
    df['Date'] = pd.to_datetime(df['Date'])

    # 设置绘图参数
    fig, ax = plt.subplots()

    # K 线图绘制
    for i in range(len(df)):
        # 判断涨跌
        if df['Close'][i] >= df['Open'][i]:  # 收盘价高于开盘价（上涨）
            color = 'red'
            lower = df['Open'][i]
            height = df['Close'][i] - df['Open'][i]
        else:  # 收盘价低于开盘价（下跌）
            color = 'green'
            lower = df['Close'][i]
            height = df['Open'][i] - df['Close'][i]

        # 将日期转换为数字
        date_num = mdates.date2num(df['Date'][i])

        # 绘制蜡烛
        ax.add_patch(plt.Rectangle((date_num - 0.2, lower), width=0.4, height=height, color=color))

        # 绘制上影线
        ax.plot([date_num, date_num], [df['Low'][i], df['High'][i]], color=color)

    # 设置日期格式
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    plt.xticks(rotation=45)

    # 添加标题和标签
    plt.title('Candlestick Chart')
    plt.xlabel('Date')
    plt.ylabel('Price')

CandlePlot(df)
plt.show()
