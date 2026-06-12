# Macro Intelligence Platform v4.0

## 專案目標

建立一個類似 Bloomberg Terminal、Trading Economics 與 FRED Dashboard 的總體經濟監控平台。

支援：

- 台灣
- 美國
- 日本
- 新加坡

未來可擴充：

- 中國
- 韓國
- 歐元區
- 英國
- 加拿大
- 澳洲

---

# 核心設計理念

目前系統以市場商品為中心：

```text
股票
外匯
加密貨幣
總經
```

改為：

```text
Macro First
Market Second
```

以總體經濟分析流程作為主架構。

---

# 系統架構

```text
Global Macro Monitor
│
├── Global Overview
├── Country Dashboard
│   ├── Taiwan
│   ├── United States
│   ├── Japan
│   └── Singapore
├── Liquidity Monitor
├── Inflation Monitor
├── Rates Monitor
├── FX Monitor
└── Market Terminal
```

---

# 首頁（Global Overview）

- Global Risk Score
- Liquidity Heatmap
- Inflation Heatmap
- Major Markets

---

# 指標分類

## Growth
- GDP
- Industrial Production
- PMI
- Retail Sales

## Inflation
- CPI
- Core CPI
- PPI

## Liquidity
- M1
- M2
- Credit
- Loans

## Rates
- Policy Rate
- 2Y Yield
- 10Y Yield
- Yield Curve

## Labor
- Unemployment
- Payrolls
- Wages

## Trade
- Exports
- Imports
- Trade Balance

## FX
- DXY
- USD/TWD
- USD/JPY
- USD/SGD

## Asset Market
- S&P500
- Nasdaq
- TAIEX
- TOPIX
- STI

---

# 國家 Dashboard

## Taiwan
- GDP
- PMI
- Exports
- M2
- CPI
- Unemployment
- USD/TWD
- TAIEX

## United States
- GDP
- PMI
- M2
- CPI
- Core CPI
- Fed Rate
- US10Y
- DXY
- S&P500

## Japan
- GDP
- PMI
- M2
- CPI
- BOJ Rate
- USD/JPY
- TOPIX
- Nikkei225

## Singapore
- GDP
- PMI
- CPI
- USD/SGD
- STI

---

# Heatmap

## Liquidity

```text
           US TW JP SG
M2         🟢 🟢 🟡 🟢
Credit     🟢 🟢 🟢 🟢
Loans      🟢 🟡 🟢 🟢
```

## Inflation

```text
           US TW JP SG
CPI        🔴 🟢 🟡 🟢
Core CPI   🔴 🟢 🟡 🟢
PPI        🟡 🟢 🟢 🟢
```

---

# API 設計

## GET /api/macro/countries

```json
["TW","US","JP","SG"]
```

## GET /api/macro/{country}

```json
{
  "country":"TW",
  "indicators":[]
}
```

## GET /api/macro/global

首頁 KPI 與風險指標。

## GET /api/macro/heatmap

```json
{
  "TW": {
    "M2": 1,
    "CPI": -1
  }
}
```

---

# 統一資料格式

```json
{
  "id":"tw_m2",
  "country":"TW",
  "category":"Liquidity",
  "name":"M2",
  "unit":"%",
  "frequency":"monthly",
  "current":5.81,
  "previous":5.63,
  "change":0.18,
  "trend":"up",
  "updated_at":"2026-06-01",
  "series":[]
}
```

---

# 前端結構

```text
frontend/
├── pages/
│   ├── overview.js
│   ├── country.js
│   ├── liquidity.js
│   └── inflation.js
├── components/
│   ├── KPICard.js
│   ├── Heatmap.js
│   ├── TrendChart.js
│   └── RiskGauge.js
└── services/
    └── api.js
```

---

# Roadmap

## Phase 1
- Dashboard 重構
- KPI Card
- 國家頁面
- 統一 API

## Phase 2
- Heatmap
- Correlation Matrix
- Risk Score

## Phase 3
- Alert Engine
- AI Summary
- Backtesting

## Phase 4
- Portfolio Overlay
- Economic Calendar
- Recession Model
- Nowcasting
