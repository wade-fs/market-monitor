建議的最終專案結構
market-monitor-v4/
│
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── config.py
│   │
│   ├── services/
│   │   ├── macro_service.py
│   │   ├── heatmap_service.py
│   │   ├── risk_service.py
│   │   └── market_service.py
│   │
│   ├── data_sources/
│   │   ├── fred.py
│   │   ├── finmind.py
│   │   ├── tw_macro.py
│   │   ├── us_macro.py
│   │   ├── jp_macro.py
│   │   └── sg_macro.py
│   │
│   └── cache/
│
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── dashboard.css
│   │
│   ├── js/
│   │   ├── dashboard.js
│   │   ├── api.js
│   │   ├── charts.js
│   │   └── heatmap.js
│   │
│   └── assets/
│
├── docs/
│   └── MACRO_PLATFORM_V4.md
│
└── docker-compose.yml
1. app.py v4 API

核心 API：

GET /api/global
GET /api/macro/TW
GET /api/macro/US
GET /api/macro/JP
GET /api/macro/SG
GET /api/heatmap
GET /api/risk
GET /api/markets
2. 全新 Dashboard UI

頁面分五區：

┌─────────────────────────────────────┐
│ Global Macro Monitor                │
├─────────────────────────────────────┤
│ Global Risk Score                   │
├─────────────────────────────────────┤
│ Liquidity Heatmap                   │
├─────────────────────────────────────┤
│ Country Dashboard                   │
├─────────────────────────────────────┤
│ Trend Charts                        │
└─────────────────────────────────────┘
3. dashboard.js

主要職責：

loadGlobalData()
loadCountryData(country)
renderKPIs()
renderHeatmap()
renderChart()
renderRiskGauge()
4. macro_service.py

統一資料來源：

def get_country_dashboard(country):
    return {
        "growth": [],
        "inflation": [],
        "liquidity": [],
        "rates": [],
        "trade": [],
        "fx": [],
        "markets": []
    }
5. data_sources
TW
get_tw_m2()
get_tw_cpi()
get_tw_exports()
get_tw_pmi()
US
get_us_m2()
get_us_cpi()
get_us_core_cpi()
get_fed_rate()
JP
get_jp_m2()
get_jp_cpi()
get_boj_rate()
SG
get_sg_cpi()
get_sgd_fx()
6. Docker Compose

加入：

services:

  backend:
    build: ./backend

  redis:
    image: redis:7

  nginx:
    image: nginx:alpine

用途：

Redis
↓
Macro Cache

Nginx
↓
API Gateway

避免每次打 API 都重新抓 FRED / FinMind。

7. Chart.js → ECharts

原因：

Heatmap

Chart.js：

很難做

ECharts：

series: [{
    type: 'heatmap'
}]

直接支援。

Gauge
series: [{
    type: 'gauge'
}]

直接做 Risk Score。

Treemap
series: [{
    type: 'treemap'
}]

直接做市場權重圖。

8. Global Overview Wireframe
┌───────────────────────────────────────────────┐
│ Global Macro Monitor                          │
├───────────────────────────────────────────────┤
│ Risk Score 72 / 100                           │
├───────────────────────────────────────────────┤
│                                               │
│ Liquidity Heatmap                             │
│                                               │
├───────────────────────────────────────────────┤
│ Inflation Heatmap                             │
├───────────────────────────────────────────────┤
│                                               │
│ Taiwan | US | Japan | Singapore               │
│                                               │
│ KPI Cards                                     │
│                                               │
├───────────────────────────────────────────────┤
│ Main Chart                                    │
│                                               │
└───────────────────────────────────────────────┘
