# 開放型經濟體總體經濟監控指標（Macro Dashboard Guide）

適用國家：

- 台灣
- 美國
- 日本
- 新加坡
- 韓國
- 香港
- 歐元區

目的：

- 觀察景氣循環
- 預測股市趨勢
- 監控流動性變化
- 評估通膨壓力
- 判斷央行政策方向
- 建立量化投資因子

---

# 一、經濟成長（Growth）

衡量經濟是否處於擴張或衰退階段。

## 核心指標

| 指標 | 頻率 |
|--------|--------|
| GDP 年增率 | 季 |
| GDP 季增率 | 季 |
| 工業生產指數 | 月 |
| PMI 製造業 | 月 |
| PMI 服務業 | 月 |
| 零售銷售 | 月 |

## 重要程度

⭐⭐⭐⭐⭐

---

# 二、通膨（Inflation）

衡量物價壓力與央行升降息方向。

## 核心指標

| 指標 | 頻率 |
|--------|--------|
| CPI | 月 |
| Core CPI | 月 |
| PPI | 月 |
| Import Price Index | 月 |
| Producer Cost Index | 月 |

## 重要程度

⭐⭐⭐⭐⭐

---

# 三、貨幣供給（Liquidity）

衡量市場流動性。

## 核心指標

| 指標 | 頻率 |
|--------|--------|
| M0 | 月 |
| M1 | 月 |
| M2 | 月 |
| M3（部分國家） | 月 |
| 銀行放款餘額 | 月 |
| 信用餘額 | 月 |

## 最重要觀察

### M2 年增率（M2 YoY）

```text
M2 ↑
→ 市場流動性增加
→ 股市與房市受惠

M2 ↓
→ 流動性收縮
→ 風險資產承壓
```

## 重要程度

⭐⭐⭐⭐⭐

---

# 四、利率（Rates）

決定資金成本與估值水準。

## 美國

- Fed Funds Rate
- SOFR
- 2Y Treasury Yield
- 10Y Treasury Yield
- 30Y Treasury Yield

## 台灣

- 重貼現率
- 公債殖利率

## 日本

- BOJ Policy Rate
- JGB 10Y

## 新加坡

- SORA
- SGS 10Y

## 重要程度

⭐⭐⭐⭐⭐

---

# 五、就業（Labor Market）

反映景氣與消費能力。

## 美國

- Nonfarm Payrolls
- Unemployment Rate
- Initial Jobless Claims
- Average Hourly Earnings

## 台灣

- 失業率
- 經常性薪資

## 日本

- 失業率
- 求人倍率

## 重要程度

⭐⭐⭐⭐

---

# 六、國際貿易（Trade）

開放型經濟體必須重點追蹤。

## 台灣

- 出口總額
- 進口總額
- 貿易順差
- 電子零組件出口

## 日本

- Exports
- Imports
- Trade Balance

## 新加坡

- Non-Oil Domestic Exports
- Total Trade

## 重要程度

⭐⭐⭐⭐⭐

---

# 七、匯率（Foreign Exchange）

反映資金流向與國際競爭力。

## 核心指標

| 國家 | 指標 |
|--------|--------|
| 美國 | DXY |
| 台灣 | USD/TWD |
| 日本 | USD/JPY |
| 新加坡 | USD/SGD |
| 歐元區 | EUR/USD |

## 台灣重點

### USD/TWD

```text
台幣升值
→ 外資流入
→ 股市通常偏強

台幣貶值
→ 外資流出
→ 股市通常偏弱
```

## 重要程度

⭐⭐⭐⭐⭐

---

# 八、資產市場（Asset Market）

市場對未來經濟的預期。

## 股票市場

| 國家 | 指數 |
|--------|--------|
| 美國 | S&P500 |
| 美國 | Nasdaq |
| 台灣 | TAIEX |
| 日本 | Nikkei 225 |
| 新加坡 | STI |

## 債券市場

- 2Y Yield
- 10Y Yield
- Yield Curve

## 波動率

- VIX
- MOVE Index

## 重要程度

⭐⭐⭐⭐⭐

---

# 建議的核心監控指標（Top 20）

## 全球

1. 美國 CPI
2. 美國 Core CPI
3. Fed Funds Rate
4. Fed Balance Sheet
5. 美國 M2
6. DXY
7. VIX
8. 美國 10Y Yield
9. 美國 2Y Yield
10. 美國殖利率曲線（10Y-2Y）

---

## 台灣

11. 台灣 M2
12. 台灣 CPI
13. 台灣出口金額
14. 台灣 PMI
15. 台灣失業率
16. USD/TWD

---

## 日本

17. 日本 CPI
18. BOJ Policy Rate
19. USD/JPY

---

## 新加坡

20. USD/SGD

---

# Dashboard 分類架構

```text
Macro
├── Growth
│   ├── GDP
│   ├── PMI
│   ├── Retail Sales
│   └── Industrial Production
│
├── Inflation
│   ├── CPI
│   ├── Core CPI
│   └── PPI
│
├── Liquidity
│   ├── M1
│   ├── M2
│   ├── Credit
│   └── Bank Loans
│
├── Rates
│   ├── Policy Rate
│   ├── 2Y Yield
│   ├── 10Y Yield
│   └── Yield Curve
│
├── Labor
│   ├── Unemployment
│   ├── Payrolls
│   └── Wage Growth
│
├── Trade
│   ├── Exports
│   ├── Imports
│   └── Trade Balance
│
├── FX
│   ├── DXY
│   ├── USD/TWD
│   ├── USD/JPY
│   └── USD/SGD
│
└── Asset Market
    ├── S&P500
    ├── Nasdaq
    ├── TAIEX
    ├── Nikkei225
    └── VIX
```

---

# 建議統一資料格式

```json
{
  "name": "Taiwan M2",
  "country": "TW",
  "category": "Liquidity",
  "unit": "%",
  "frequency": "monthly",
  "current": 5.81,
  "previous": 5.63,
  "change": 0.18,
  "updated_at": "2026-06-01",
  "series": [
    {
      "date": "2026-05-01",
      "value": 5.81
    }
  ]
}
```

---

# 對股市影響最大的五大因子

依歷史經驗排序：

1. 美國聯準會利率（Fed Rate）
2. 美國 M2
3. 美國 CPI
4. 美國 10Y 公債殖利率
5. 美元指數（DXY）

這五項通常足以解釋全球股市大部分的中長期趨勢變化。
