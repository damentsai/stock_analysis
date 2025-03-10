import matplotlib.pyplot as plt
import twstock
import yfinance as yf
import mplfinance as mpf
import pandas as pd
import numpy as np
import matplotlib


matplotlib.rcParams['font.family'] = ['Microsoft JhengHei', 'Calibri']  # 设置字体家族
plt.rcParams['axes.unicode_minus'] = False

# 先補充KD線知識
# 知識來源：https://www.thinkmarkets.com/tw/trading-academy/tech-indicators/stochastic-oscillator/
# K線(快線)和D線(慢線)可以作為買賣的依據，希望藉由參考基金各股來參考並決定投資策略
# KD用於判斷當前價格與一段時間內價格波動範圍的動量，從而判斷未來市場趨勢，提供超買或超賣的訊號
# 當價格上漲到一定程度，會出現超買現象，市場可能會出現回調或下跌
# 當價格下跌到一定程度，會出現超賣現象，市場可能會出現反彈或上漲
# K線：快速平均值，衡量當日的收盤價相對於過去幾天內的最高與最低間所處在的位置
# D線：慢速平均值，K線的平均值
# 三步驟：
# 第一步：計算 RSV (Raw Stochastic Value)，(當天收盤價 - 期間最低價)/(期間最高價 - 期間最低價)*100%
# 第二步：計算 K 值，當天 K = 1/3 * 當天 RSV + 2/3 * 前一天 K，若沒有前一天 K 值，就假設為50%
# 第三步：計算 D 值，當天 D = 1/3 * 當天 K + 2/3 * 前一天 D，若沒有前一天 D 值，就假設為50%
# 第四步(optional)：KDJ指標，計算 J 值，J = 3K - 2D
# 交易週期會影響平滑度K值的，常見的有6天、9天(十天後的K價格影響力 < 1%)、14天，週期愈長線會越平穩，較能反映長期趨勢、長期投資、趨勢波動較平緩的股票
# K 就像是目前這個價格是不是這段期間內最便宜的
# D 就像這多天買的價格的平均線
# J 衡量K值與D值的背離程度
# D線低於30%，代表超賣訊號
# D線高於70%，代表超買訊號
# 黃金交叉or低位金叉是指K、J線上突D線，有機會買入入場
# 死亡交叉or高位死差是指K、J線下突D線，有機會賣出做空清倉
# 頂部背離：當股價走勢一峰比一峰高時，KDJ值卻在高位上一峰比一峰低往下走，價格位置與指標位置出現明顯反差，通常是股價反轉的信號，表示市場上漲行情
#         即將結束，出現下跌行情，是賣出信號，投資者應該賣出股票。
# 底部背離：當股價走勢一峰比一峰低時，KDJ值卻在低位上一峰比一峰高往上走，價格位置與指標位置出現明顯反差，一般是股價反轉的信號，表示市場下跌行情
#         即將結束，股價迎來觸底反彈，是買入信號，投資者應該建倉。

# KD指標的問題
# 指標鈍化：KDJ指標對市場趨勢的運行非常靈敏，經常過早的發出買入或賣出信號，在極強或者極弱的市場行情下會出現指標鈍化現象，過早的買入賣出使投資者
#         往往造成不必要的失誤，頻繁的買賣也增加了投資者的風險。
# 信號滯後：KDJ指標是基於過去一段時間的價格變動計算得出的，它的信號有一定的滯後性。當市場出現快速變化時，KDJ指標可能無法及時反映最新市場情況。
# 缺乏獨立性：KDJ指標缺乏獨立性，不能作為投資決策唯一參考指標，它通常需要與其他技術指標或圖表結合使用才可靠。
# 容易產生假信號：由於市場的波動性和噪音，KDJ指標容易產生假信號，會給出錯誤的買入或賣出信號。尤其是在市場橫盤或震蕩時，KDJ指標的表現比較不穩定
#              ，會對交易者造成誤導。

# 總體而言，雖然KDJ指標在技術分析中有其用途，但投資者應該意識到它的局限性並結合其他工具和分析方法來進行全面的市場分析和交易決策。
# KDJ指標是市場走勢分析中的重要技術指標。它是一個趨勢跟踪指標。在查看 KDJ 形成的價格模式時，重要的是要知道可能會產生錯誤信號。
# 因此建議是將其與另一個指標結合使用。

# 交叉時 KD其中一個趨勢向上，另一個趨勢向下，代表即將迎來的變化大，我認為進場或做空動作的支持力，但也不保證不會指標鈍化
# 我覺得參考可以用10或14天的計算結果，因為可以反應較為準確且少雜訊的趨勢

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

df.rename(columns={'Turnover': 'Volume'}, inplace=True)  # mplfinance lib辨認需求(成交量)
df.index = pd.to_datetime(df['Date'])  # 第一欄改成 Date 的格式

n = 9  # 定義windows大小
# 第一步：計算RSV
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

plt.plot(df['Date'], df['RSI'], label='RSI')
plt.plot(df['Date'], df['K'], label='K')
plt.plot(df['Date'], df['D'], label='D')
plt.plot(df['Date'], df['J'], label='J')
plt.axhline(y=0, color='gray', linestyle='--')
plt.axhline(y=0.2, color='gray', linestyle='--')
plt.axhline(y=0.8, color='gray', linestyle='--')
plt.axhline(y=1, color='gray', linestyle='--')
plt.xticks([])
plt.ylabel('ratio')
plt.title('KDJ指標圖')
plt.legend()
plt.show()

