import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import requests

# 安聯台灣科技基金淨值網址為範例
url = 'https://prd-ap-fund-sc.allianzgi.com/api/fund/exportnetworthdetails/?SalesChannel=tw_endclients&ShareClassId=&SeoName=allianz-global-investors-taiwan-technology-fund&Language=zh-TW&IsuserLoggedIn=False&IsLocalLanguage=False&DatasourceId={379E1EBD-AB87-4C7A-87AD-30A119A3C3B6}'
save_path = 'data/funds_history.xlsx'
response = requests.get(url)

with open(save_path, 'wb') as f:
    f.write(response.content)
print('net worth excel data download and saved')
# 經過觀察，表格紀錄的時間需反轉，且與個股的天數一致，所以只要指定天數，計算個股觀察所需的天數然後在表格裡做擷取翻轉就好。


df = pd.read_excel(save_path)
print(df.head(30))
days = 172
print(df.iloc[8:8+days, :])
nw = df.iloc[8:8+days, :].iloc[::-1].reset_index(drop=True)
nw.columns = ['Date', 'Fund Net Value']
# print(df.columns)
# print(nw)
nw['Date'] = pd.to_datetime(nw['Date'], format='%Y/%m/%d')
nw.index = pd.to_datetime(nw['Date'])
nw['Fund Net Value'] = pd.to_numeric(nw['Fund Net Value'], errors='coerce')
print(nw['Date'])
print(nw['Fund Net Value'])
plt.plot(nw['Date'], nw['Fund Net Value'])
# plt.xticks(rotation=45)  # 旋转 x 轴刻度
plt.title('History of Net Values of the Fund')
plt.xlabel('Date')  # 添加 x 轴标签
plt.ylabel('Fund Net Value')  # 添加 y 轴标签
# 设置日期格式
ax = plt.gca()  # 获取当前轴
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # 设置主刻度格式
# 设置日期间隔
ax.xaxis.set_major_locator(mdates.DayLocator(interval=30))  # 每天一个刻度
ax.yaxis.set_major_locator(mdates.DayLocator(interval=5))  # 每天一个刻度
ax.xaxis.set_major_locator(mdates.AutoDateLocator())  # 視窗自由拖動
plt.show()