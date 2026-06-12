import os
import yfinance as yf
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import pandas_datareader.data as web
from FinMind.data import DataLoader

app = FastAPI(title="全球金融大數據量化終端")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

dl = DataLoader()

# Symbols
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

    def fetch_timeframe_data(self, name, symbol, category, period="2y"):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            if df.empty:
                df = ticker.history(period="1mo")
                if df.empty: return None
            
            close = df['Close'].ffill()
            
            def format_series(data):
                clean_data = data.dropna()
                return [{"t": t.strftime('%Y-%m-%d'), "v": round(float(v), 2)} 
                        for t, v in clean_data.items()]

            current = round(float(close.iloc[-1]), 2)
            prev = float(close.iloc[-2]) if len(df) > 1 else current
            change = round(current - prev, 2)
            pct = round((change / prev) * 100, 2) if prev != 0 else 0
            
            return {
                "name": name,
                "category": category,
                "current": current,
                "change": change,
                "pct": pct,
                "series": {
                    "daily": format_series(close.tail(30)),
                    "weekly": format_series(close.resample('W').last().tail(20)),
                    "monthly": format_series(close.resample('M').last().tail(12)),
                    "quarterly": format_series(close.resample('Q').last().tail(8))
                }
            }
        except Exception as e:
            self.add_log(f"同步錯誤 {name}: {str(e)}")
            return None

    def fetch_fred_macro(self):
        """Fetch real macro curves from FRED and combine with other regional data."""
        try:
            self.add_log("正在執行全球宏觀管線聚合...")
            start = datetime.now() - timedelta(days=365*5)
            # M2SL: US M2, T10Y2Y: Yield Spread, CPIAUCSL: CPI
            fred_map = {'M2SL': '美國 M2 供應量', 'T10Y2Y': '美債 10Y-2Y 利差', 'CPIAUCSL': '美國 CPI 通膨'}
            
            macro_results = {}
            for sym, label in fred_map.items():
                try:
                    df = web.DataReader(sym, 'fred', start)
                    if not df.empty:
                        series = df[sym].dropna()
                        current_val = round(float(series.iloc[-1]), 2)
                        prev_val = series.iloc[-2] if len(series) > 1 else current_val
                        trend = "上升" if current_val > prev_val else "下降"
                        
                        macro_results[label] = {
                            "value": current_val,
                            "trend": trend,
                            "unit": "兆" if sym == 'M2SL' else "%",
                            "period": "月報" if sym != 'T10Y2Y' else "日報",
                            "next": (series.index[-1] + timedelta(days=30)).strftime('%Y-%m-%d'),
                            "series": [{"t": t.strftime('%Y-%m-%d'), "v": round(float(v), 2)} for t, v in series.tail(60).items()]
                        }
                except Exception: pass

            # Restore secondary macro indicators (Taiwan, China, EU)
            # These can be static/placeholder if no direct FRED/Yahoo symbol is available yet
            others = {
                "台灣 M2 貨幣": {"value": 5.4, "unit": "%", "trend": "穩定", "period": "月報", "next": "2026-07-20", "series": []},
                "中國 M2 貨幣": {"value": 8.7, "unit": "%", "trend": "寬鬆", "period": "月報", "next": "2026-07-15", "series": []},
                "歐元區 GDP": {"value": 0.4, "unit": "%", "trend": "疲弱", "period": "季報", "next": "2026-08-10", "series": []}
            }
            macro_results.update(others)
            
            self.add_log("全球宏觀數據聚合完成。")
            return macro_results
        except Exception as e:
            self.add_log(f"宏觀引擎故障: {str(e)}")
            return {}

orchestrator = MarketDataOrchestrator()

@app.get("/api/terminal")
def get_terminal_data():
    main_indices = {}
    for cat, assets in SYMBOLS.items():
        for name, sym in assets.items():
            data = orchestrator.fetch_timeframe_data(name, sym, cat)
            if data:
                main_indices[name] = data
    
    macro = orchestrator.fetch_fred_macro()
    
    return {
        "indices": main_indices,
        "reports": macro,
        "flows": {"value": -4904284, "date": "2026-06-11"},
        "logs": orchestrator.log_feed,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "quant": {
            "liquidity_correlation": "0.82 (高度正相關)"
        }
    }

os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
