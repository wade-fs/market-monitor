# 全球金融大數據量化終端 — 後續分析擴充筆記

> 基於現有系統：FastAPI + yfinance + FRED + FinMind，Docker 部署

---

## 系統現況

| 類別 | 資料來源 | 涵蓋指標 |
|------|----------|----------|
| 股市 | yfinance | 台股、納斯達克、S&P500、日經、DAX 等 8 個指數 |
| 期匯 | yfinance | 美元指數、美債10Y、台幣匯率 |
| 數字貨幣 | yfinance | BTC、ETH |
| 宏觀 | FRED API | M2、CPI、10Y-2Y 利差 |
| 台股籌碼 | FinMind（已初始化，**尚未使用**） | — |

---

## 擴充路線圖

```
目前系統（股市/期匯/加密/宏觀監控）
         │
    ┌────┴────┐
    ▼         ▼
 ① 技術指標   ② 相關性矩陣
    │         │
    ▼         ▼
 ③ 情緒分析   ④ ML 預測模型
    │         │
    ▼         ▼
 ⑤ 籌碼分析   ⑥ 總經事件分析
    └────┬────┘
         ▼
   整合儀表板（多模組 API + Chart.js 擴充）
```

---

## ① 技術指標量化分析 🟦

**優先度：S 級（最建議先做）**

### 說明
`yfinance` 已拉好歷史 OHLCV，只需加 `pandas-ta` 計算層，即可在現有 `/api/terminal` 回傳資料裡附帶技術訊號。Chart.js 支援多軸疊圖，前端改動小但資訊量大增。

### 要做的事
- [ ] 後端加 `pandas-ta` 計算 RSI、MACD、KD、布林通道
- [ ] `/api/terminal` 回傳資料新增 `indicators` 欄位
- [ ] 前端 Chart.js 加第二 Y 軸疊圖顯示 RSI / MACD

### 關鍵指標

| 指標 | 說明 | 用途 |
|------|------|------|
| RSI (14) | 相對強弱指數 | 超買（>70）/ 超賣（<30）訊號 |
| MACD | 均線差值 + 訊號線 | 趨勢轉折、金叉/死叉 |
| 布林通道 | 均線 ± 2σ | 突破或均值回歸 |
| KD (9,3,3) | 隨機指標 | 短線買賣時機 |

### 範例程式（後端）

```python
import pandas_ta as ta

def add_indicators(df: pd.DataFrame) -> dict:
    df['rsi'] = ta.rsi(df['Close'], length=14)
    macd = ta.macd(df['Close'])
    df['macd'] = macd['MACD_12_26_9']
    df['macd_signal'] = macd['MACDs_12_26_9']
    bb = ta.bbands(df['Close'], length=20)
    df['bb_upper'] = bb['BBU_20_2.0']
    df['bb_lower'] = bb['BBL_20_2.0']
    return df
```

---

## ② 跨市場相關性矩陣 🟩

**優先度：S 級**

### 說明
把現有 SYMBOLS 所有標的一起抓成 DataFrame，計算滾動相關係數（rolling correlation），產出熱力圖，直接視覺化現有 README 裡提到的「流動性相關性 0.82」。

### 要做的事
- [ ] 後端新增 `/api/correlation` endpoint
- [ ] 支援可調視窗：30天 / 90天 / 1年
- [ ] 前端用 Chart.js 的矩陣熱力圖顯示

### 重點相關性觀察

| 組合 | 預期相關性 | 意義 |
|------|------------|------|
| 台幣 ↔ 台股加權 | 正相關 | 外資流向指標 |
| 美債10Y ↔ 納斯達克 | 負相關 | 升息壓估值 |
| DXY ↔ 新興市場 | 負相關 | 美元強弱影響資金流 |
| BTC ↔ 納斯達克 | 正相關（近年） | 風險偏好同步 |

### 範例程式（後端）

```python
@app.get("/api/correlation")
def get_correlation(period: str = "90d"):
    symbols = {**SYMBOLS["股市"], **SYMBOLS["期匯"], **SYMBOLS["數字貨幣"]}
    closes = {}
    for name, sym in symbols.items():
        df = yf.Ticker(sym).history(period=period)
        if not df.empty:
            closes[name] = df['Close']
    combined = pd.DataFrame(closes).dropna()
    corr = combined.corr(method='pearson').round(2)
    return corr.to_dict()
```

---

## ③ 新聞 / 社群情緒分析 🟨

**優先度：B 級（需新 API 或爬蟲）**

### 說明
接 `newsapi.org` 或 `GDELT` 免費新聞 API，用 NLP 做中英文情緒分類，產出每日市場情緒分數，作為額外 alpha 因子疊加在走勢圖上。

### 要做的事
- [ ] 串接 NewsAPI（免費版：100 requests/day）
- [ ] 用 `transformers` 或 `snownlp` 做情緒分類
- [ ] 每日計算「看多比例」分數（0~1）
- [ ] 前端新增情緒儀表板（gauge chart）

### 資料來源選擇

| 來源 | 費用 | 語言 | 備註 |
|------|------|------|------|
| [NewsAPI](https://newsapi.org) | 免費 100次/天 | 英文 | 快速串接 |
| [GDELT](https://www.gdeltproject.org) | 免費 | 多語 | 資料量大，需篩選 |
| PTT Stock 版 | 免費（爬蟲） | 中文 | 需遵守爬蟲規範 |
| Google Trends | 免費（`pytrends`） | 全球 | 關鍵字熱度 |

### 情緒分類邏輯

```python
from snownlp import SnowNLP  # 中文情緒

def analyze_sentiment(text: str) -> float:
    """回傳 0(負面) ~ 1(正面)"""
    s = SnowNLP(text)
    return round(s.sentiments, 3)
```

---

## ④ 機器學習預測模型 🟧

**優先度：C 級（長期投資，複雜度高）**

### 說明
LSTM 或 LightGBM，需先完成①②的特徵工程（技術指標 + 宏觀數據合併）。適合前幾個模組穩定後再進行。

### 要做的事
- [ ] 特徵工程：合併技術指標 + 宏觀數據
- [ ] 建立滾動視窗訓練集（walk-forward validation）
- [ ] 模型一：LSTM（時序預測）
- [ ] 模型二：LightGBM（特徵重要性解釋）
- [ ] 前端顯示預測區間（上下界）

### 特徵清單（建議）

```
技術面：RSI, MACD, KD, 布林通道寬度, 成交量變化率
宏觀面：CPI YoY, 美債10Y, 台幣匯率, DXY
情緒面：新聞情緒分數, Google Trends 熱度
籌碼面：外資買賣超, 融資餘額變化
```

### 技術架構

```
特徵工程 (pandas)
    │
    ├── LSTM (tensorflow/keras)  → 價格預測區間
    └── LightGBM                 → 漲跌方向分類 + 特徵重要性
```

---

## ⑤ 三大法人籌碼分析 🟥

**優先度：A 級（FinMind 已初始化，改動最小）**

### 說明
`app.py` 中 `DataLoader` 已初始化但**尚未使用任何 endpoint**。直接加 `TaiwanStockInstitutionalInvestorsBuySell` API 呼叫即可取得三大法人每日買賣超，是台股短線最重要的籌碼指標。

### 要做的事
- [ ] 後端新增 `/api/institutional` endpoint
- [ ] 呼叫 FinMind 三大法人 API（外資/投信/自營）
- [ ] 計算累計買賣超 + N 日動態趨勢
- [ ] 前端加「籌碼流向」堆疊長條圖

### 範例程式（後端）

```python
@app.get("/api/institutional")
def get_institutional(stock_id: str = "2330", days: int = 30):
    end = datetime.now().strftime('%Y-%m-%d')
    start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    df = dl.taiwan_stock_institutional_investors(
        stock_id=stock_id,
        start_date=start,
        end_date=end
    )
    
    result = {}
    for investor_type in ['Foreign_Investor', 'Investment_Trust', 'Dealer']:
        subset = df[df['name'] == investor_type]
        result[investor_type] = [
            {"date": row['date'], "net": row['buy'] - row['sell']}
            for _, row in subset.iterrows()
        ]
    return result
```

### 觀察指標

| 指標 | 訊號 | 意義 |
|------|------|------|
| 外資連買 N 日 | 偏多 | 國際資金流入 |
| 投信連買 + 外資同買 | 強烈偏多 | 主力共同佈局 |
| 融資大增 + 外資賣超 | 警訊 | 散戶追高，法人出貨 |

---

## ⑥ 總經事件影響分析 🟩

**優先度：A 級**

### 說明
建立事件日曆表（Fed 決議日、CPI 公布日、NFP 日），計算每次事件前後 N 個交易日的各指數漲跌幅分佈，做成統計圖。對波段策略很有參考價值。

### 要做的事
- [ ] 建立 `events.json`（歷史事件日曆）
- [ ] 後端新增 `/api/event-impact` endpoint
- [ ] 計算事件前 5 日 / 後 5 日漲跌幅分佈
- [ ] 前端顯示箱型圖（box plot）或長條圖

### 事件日曆資料結構

```json
{
  "events": [
    {
      "date": "2024-07-31",
      "type": "Fed",
      "title": "FOMC 利率決議",
      "decision": "降息 25bps",
      "result": "維持不變"
    },
    {
      "date": "2024-08-13",
      "type": "CPI",
      "title": "美國 CPI 公布",
      "actual": 2.9,
      "forecast": 3.0
    }
  ]
}
```

### 關鍵事件類型

| 事件 | 頻率 | 對台股影響 |
|------|------|------------|
| FOMC 利率決議 | 每 6~8 週 | 極高（改變資金成本） |
| 美國 CPI 公布 | 每月第二週 | 極高（影響降息預期） |
| 非農就業 NFP | 每月第一個週五 | 高 |
| 台積電法說會 | 每季 | 極高（台股指標） |
| 美國 GDP | 每季 | 中高 |

---

## 實作優先順序建議

```
第一階段（1~2 週）
  ├── ① 技術指標  ← 改動最小，效果最明顯
  └── ⑤ 籌碼分析 ← FinMind 已就緒

第二階段（2~4 週）
  ├── ② 相關性矩陣
  └── ⑥ 總經事件分析

第三階段（1~2 個月）
  └── ③ 情緒分析

長期目標
  └── ④ ML 預測模型
```

---

## 相關資源

- [FinMind 文件](https://finmindtrade.com/analysis/#/document/api)
- [FRED API](https://fred.stlouisfed.org/docs/api/fred/)
- [yfinance 文件](https://ranaroussi.github.io/yfinance/)
- [pandas-ta 指標列表](https://github.com/twopirllc/pandas-ta)
- [NewsAPI](https://newsapi.org/docs)
- [GDELT Project](https://www.gdeltproject.org/)
