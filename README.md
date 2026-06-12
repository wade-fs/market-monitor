# Macro Intelligence Platform v4.0 (全球總體經濟情報平台)

![Version](https://img.shields.io/badge/version-4.0-blue.svg)
![Architecture](https://img.shields.io/badge/architecture-Macro%20First-success.svg)
![Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20Redis%20%7C%20ECharts-purple.svg)

Macro Intelligence Platform 是一個高度整合的總體經濟監控系統，設計理念深受 Bloomberg Terminal 與 Trading Economics 啟發。
在 v4.0 的重大重構中，我們全面轉向 **「總經優先 (Macro First)」** 的架構，為專業投資人與分析師提供即時的全球經濟脈動、流動性熱力圖以及跨市場的風險評估。

---

## 🌟 核心功能 (Core Features)

1. **全球總經概觀 (Global Overview)**
   * **全球風險評分 (Global Risk Score)**：動態計算全球主要資產的上漲比例，以儀表板 (Gauge) 呈現當前市場風險偏好。
   * **資金流動性熱力圖 (Liquidity Heatmap)**：一目了然地監控美國、台灣、日本、新加坡等國的 M1/M2 貨幣供給擴張或收縮狀態。
   * **通膨壓力熱力圖 (Inflation Heatmap)**：視覺化呈現各國 CPI、Core CPI 的趨勢變化，提早預判央行貨幣政策走向。

2. **國家經濟儀表板 (Country Dashboards)**
   * 提供 **美國 (US)、台灣 (TW)、日本 (JP)、新加坡 (SG)** 的專屬 360 度總經矩陣。
   * 指標涵蓋 8 大維度：經濟成長 (Growth)、通膨物價 (Inflation)、資金流動性 (Liquidity)、利率水準 (Rates)、勞動力市場 (Labor)、國際貿易 (Trade)、匯率走勢 (FX)、資產市場 (Asset Market)。
   * 所有數據配備 **Sparkline 趨勢迷你圖**，並自動標示百分比變動與多空顏色。

3. **高可用性數據引擎 (High-Availability Data Engine)**
   * 整合 `yfinance`、`pandas_datareader` (FRED) 與 `FinMind`。
   * 具備 **「智慧型備援機制 (Proxy Fallback)」**：當 FRED API 阻擋或無回應時，系統會自動利用各國大盤指數（如 TAIEX）作為流動性代理，透過演算法生成合理的趨勢基準，確保 UI 永不留白。
   * 內建 **開機自動預熱 (Pre-warming)**，啟動瞬間即在背景同步全球數十項總經數據。

4. **高效能微服務架構**
   * 引入 **Redis** 進行 12-24 小時的持久化快取，大幅減少對第三方 API 的請求次數。
   * 使用 **Nginx** 作為 API Gateway 與靜態資源伺服器，達成前後端完全分離。

---

## 🏗️ 系統架構 (Architecture)

```text
market-monitor/
├── backend/                  # FastAPI 核心服務
│   ├── config.py             # 環境變數與 Redis 設定
│   ├── models.py             # 統一資料結構 (Indicator, SeriesPoint)
│   ├── services/             # 業務邏輯層 (macro, risk, heatmap, cache)
│   └── data_sources/         # 爬蟲與 API 封裝 (FRED, FinMind, Yahoo Finance)
├── frontend/                 # Nginx 託管之前端應用
│   ├── index.html            # 終端機 UI 進入點
│   ├── css/                  # 樣式表 (Tailwind + Custom)
│   └── js/                   # 邏輯與 ECharts 渲染器
├── nginx/                    # 反向代理設定
└── docker-compose.yml        # 容器編排
```

---

## 🛠️ 技術棧 (Tech Stack)

* **Backend**: Python 3.11, FastAPI, Uvicorn, Pandas, yfinance, pandas-datareader
* **Frontend**: HTML5, Tailwind CSS, ECharts (資料視覺化), Lucide (圖標)
* **Infrastructure**: Docker, Docker Compose, Redis 7 (AOF Persistence), Nginx

---

## 🚀 快速部署 (Quick Start)

### 系統需求
* Docker
* Docker Compose

### 啟動步驟

1. **複製專案**
   ```bash
   git clone <your_repository_url>
   cd market-monitor
   ```

2. **(選擇性) 設定環境變數**
   * 系統預設具備無 Key 的代理備援機制。若要獲取最精準的 FRED 官方數據，可在 `docker-compose.yml` 內的 `backend` 區塊加入環境變數：
     ```yaml
     environment:
       - FRED_API_KEY=your_fred_api_key
       - FINMIND_TOKEN=your_finmind_token
     ```

3. **啟動服務**
   ```bash
   docker compose up --build -d
   ```
   * *初次啟動時，後端將在背景執行約 10-30 秒的全球數據預熱。*

4. **開啟平台**
   * 打開瀏覽器，前往：[http://localhost:16888](http://localhost:16888)

---

## 🛑 故障排除 (Troubleshooting)

* **數據全部顯示為 Proxy 走勢**：請確認伺服器對外網路連線正常，或者嘗試申請並填寫 `FRED_API_KEY` 以獲取真實的美國以外總經數據。
* **無法連線至網頁 (502 Bad Gateway)**：後端 FastAPI 可能還在啟動或背景預熱中，請等待 10 秒後重新整理。
* **清除緩存**：若欲強制更新所有總經數據，請執行：
  ```bash
  docker compose down
  docker volume rm market-monitor_redis_data
  docker compose up -d
  ```

---

## 📝 Roadmap (未來展望)

- [x] **Phase 1**: V4 Dashboard 重構，導入 Nginx + Redis 架構。
- [x] **Phase 2**: ECharts 視覺化，實作 Liquidity & Inflation Heatmap。
- [x] **Phase 3**: 智慧型代理數據備援 (Proxy Fallback) 與中文化 UI。
- [ ] **Phase 4**: 實作 Alert Engine (預警系統) 與投資組合疊加比對功能。
- [ ] **Phase 5**: 導入 Recession Model (衰退模型) 與 Nowcasting (即時預測)。
