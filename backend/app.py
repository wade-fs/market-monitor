import os
import yfinance as yf
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from FinMind.data import DataLoader

app = FastAPI(title="全球金融大數據終端機")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

dl = DataLoader()

# Expanded Global Symbols with Categories
SYMBOLS = {
    "股市": {
        "台股加權": "^TWII",
        "納斯達克": "^IXIC",
        "標普500": "^GSPC",
        "日經225": "^N225",
        "德國DAX": "^GDAXI",
        "印度NIFTY": "^NSEI",
        "澳洲ASX": "^AXJO",
        "新加坡STI": "^STI"
    },
    "期匯": {
        "美元指數": "DX-Y.NYB",
        "美債10Y": "^TNX",
        "台幣匯率": "TWD=X"
    },
    "數字貨幣": {
        "比特幣": "BTC-USD",
        "以太幣": "ETH-USD"
    }
}

class MarketDataOrchestrator:
    def __init__(self):
        self.log_feed = []

    def add_log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_feed.insert(0, f"[{timestamp}] {msg}")
        self.log_feed = self.log_feed[:10]

    def clean_series(self, series):
        """Replace NaN/Inf with None for JSON compliance."""
        return [float(x) if np.isfinite(x) else None for x in series]

    def fetch_timeframe_data(self, name, symbol, category, period="2y"):
        try:
            self.add_log(f"正在同步 {name} ({symbol})...")
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            if df.empty:
                df = ticker.history(period="1mo")
                if df.empty:
                    self.add_log(f"同步失敗: {name} 無數據")
                    return None
            
            close = df['Close'].ffill()
            
            def format_series(data):
                # Returns list of {t: timestamp, v: value}
                return [{"t": t.strftime('%Y-%m-%d'), "v": round(float(v), 2) if np.isfinite(v) else None} 
                        for t, v in data.items()]

            # Timeframe series with dates
            daily = format_series(close.tail(30))
            weekly = format_series(close.resample('W').last().tail(20))
            monthly = format_series(close.resample('ME').last().tail(12))
            quarterly = format_series(close.resample('QE').last().tail(8))
            
            current = round(float(close.iloc[-1]), 2)
            if not np.isfinite(current): current = 0
            
            prev = float(close.iloc[-2]) if len(df) > 1 else current
            if not np.isfinite(prev): prev = current
            
            change = round(current - prev, 2)
            pct = round((change / prev) * 100, 2) if prev != 0 else 0
            
            self.add_log(f"成功更新: {name}")
            return {
                "name": name,
                "category": category,
                "current": current,
                "change": change,
                "pct": pct,
                "series": {
                    "daily": daily,
                    "weekly": weekly,
                    "monthly": monthly,
                    "quarterly": quarterly
                }
            }
        except Exception as e:
            self.add_log(f"同步錯誤 {name}: {str(e)}")
            return None

    def get_finmind_flow(self):
        try:
            start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
            df = dl.taiwan_stock_institutional_investors(stock_id='2330', start_date=start_date)
            if not df.empty:
                foreign = df[df['name'] == 'Foreign_Investor']
                if not foreign.empty:
                    latest = foreign.iloc[-1]
                    return {"value": int(latest['buy'] - latest['sell']), "date": latest['date']}
        except Exception as e:
            self.add_log(f"FinMind 數據源錯誤: {str(e)}")
        return {"value": 0, "date": "--"}

orchestrator = MarketDataOrchestrator()

@app.get("/api/terminal")
def get_terminal_data():
    orchestrator.add_log("啟動全球大數據管線同步...")
    
    main_indices = {}
    for cat, assets in SYMBOLS.items():
        for name, sym in assets.items():
            data = orchestrator.fetch_timeframe_data(name, sym, cat)
            if data:
                main_indices[name] = data
    
    reports = {
        "CPI 通膨": {"value": 3.1, "period": "月報", "trend": "持平", "next": "2026-07-12"},
        "GDP 成長": {"value": 2.1, "period": "季報", "trend": "上升", "next": "2026-08-01"},
        "M2 貨幣": {"value": 5.4, "period": "月報", "trend": "擴張", "next": "2026-07-20"}
    }
    
    flows = orchestrator.get_finmind_flow()
    orchestrator.add_log("數據管線聚合完成。")
    
    return {
        "indices": main_indices,
        "reports": reports,
        "flows": flows,
        "logs": orchestrator.log_feed,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
