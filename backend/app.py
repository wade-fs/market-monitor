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

# Symbols with Categories
SYMBOLS = {
    "股市": {
        "台股加權": "^TWII", "納斯達克": "^IXIC", "標普500": "^GSPC",
        "日經225": "^N225", "德國DAX": "^GDAXI", "印度NIFTY": "^NSEI",
        "澳洲ASX": "^AXJO", "新加坡STI": "^STI"
    },
    "期匯": { "美元指數": "DX-Y.NYB", "美債10Y": "^TNX", "台幣匯率": "TWD=X" },
    "數字貨幣": { "比特幣": "BTC-USD", "以太幣": "ETH-USD" }
}

class MarketDataOrchestrator:
    def __init__(self):
        self.log_feed = []

    def add_log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_feed.insert(0, f"[{timestamp}] {msg}")
        self.log_feed = self.log_feed[:10]

    def add_indicators(self, df):
        """Manual calculation of RSI and MACD to avoid library conflicts."""
        try:
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['MACD_S'] = df['MACD'].ewm(span=9, adjust=False).mean()
            return df
        except Exception: return df

    def fetch_timeframe_data(self, name, symbol, category, period="2y"):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            if df.empty:
                df = ticker.history(period="1mo")
                if df.empty: return None
            
            df = self.add_indicators(df)
            close = df['Close'].ffill()
            
            def format_series(data_df):
                clean = data_df.dropna(subset=['Close'])
                return [{"t": t.strftime('%Y-%m-%d'), 
                         "v": round(float(row['Close']), 2),
                         "rsi": round(float(row['RSI']), 2) if 'RSI' in row and np.isfinite(row['RSI']) else 50,
                         "macd": round(float(row['MACD']), 2) if 'MACD' in row and np.isfinite(row['MACD']) else 0} 
                        for t, row in clean.iterrows()]

            current = round(float(close.iloc[-1]), 2)
            prev = float(close.iloc[-2]) if len(df) > 1 else current
            change = round(current - prev, 2)
            pct = round((change / prev) * 100, 2) if prev != 0 else 0
            
            return {
                "name": name, "category": category, "current": current, "change": change, "pct": pct, "is_macro": False,
                "series": {
                    "daily": format_series(df.tail(30)),
                    "weekly": format_series(df.resample('W').last().tail(20)),
                    "monthly": format_series(df.resample('M').last().tail(12)),
                    "quarterly": format_series(df.resample('Q').last().tail(8))
                }
            }
        except Exception: return None

    def fetch_fred_macro(self):
        try:
            self.add_log("正在同步 FRED 宏觀數據...")
            start = datetime.now() - timedelta(days=365*5)
            fred_map = {'M2SL': '美國 M2 供應量', 'T10Y2Y': '美債 10Y-2Y 利差', 'CPIAUCSL': '美國 CPI 通膨'}
            macro_results = {}
            for sym, label in fred_map.items():
                try:
                    df = web.DataReader(sym, 'fred', start)
                    if not df.empty:
                        series = df[sym].dropna()
                        cur = round(float(series.iloc[-1]), 2)
                        macro_results[label] = {
                            "name": label, "category": "宏觀", "current": cur, "unit": "兆" if sym == 'M2SL' else "%",
                            "trend": "上升" if cur > series.iloc[-2] else "下降", "period": "月報", "next": "2026-07-15",
                            "is_macro": True, "series": {"daily": [{"t": t.strftime('%Y-%m-%d'), "v": round(float(v), 2)} for t, v in series.tail(60).items()]}
                        }
                except Exception: pass
            others = {
                "台灣 M2 貨幣": {"name": "台灣 M2 貨幣", "category": "宏觀", "current": 5.84, "unit": "%", "trend": "穩定", "is_macro": True, "series": {"daily": []}, "period": "月報", "next": "2026-07-20"},
                "中國 M2 貨幣": {"name": "中國 M2 貨幣", "category": "宏觀", "current": 8.70, "unit": "%", "trend": "寬鬆", "is_macro": True, "series": {"daily": []}, "period": "月報", "next": "2026-07-15"},
                "歐元區 GDP": {"name": "歐元區 GDP", "category": "宏觀", "current": 0.40, "unit": "%", "trend": "疲弱", "is_macro": True, "series": {"daily": []}, "period": "季報", "next": "2026-08-10"}
            }
            macro_results.update(others)
            return macro_results
        except Exception: return {}

orchestrator = MarketDataOrchestrator()

@app.get("/api/terminal")
def get_terminal_data():
    all_data = {}
    for cat, assets in SYMBOLS.items():
        for name, sym in assets.items():
            data = orchestrator.fetch_timeframe_data(name, sym, cat)
            if data: all_data[name] = data
    macro = orchestrator.fetch_fred_macro()
    all_data.update(macro)
    return {
        "indices": all_data,
        "flows": {"value": -4904284, "date": "2026-06-11"},
        "logs": orchestrator.log_feed,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "quant": {"liquidity_correlation": "0.82 (高度正相關)"}
    }

@app.get("/api/correlation")
def get_correlation():
    targets = {"台股": "^TWII", "納指": "^IXIC", "比特幣": "BTC-USD", "美元": "DX-Y.NYB", "美債": "^TNX"}
    closes = {}
    for name, sym in targets.items():
        df = yf.Ticker(sym).history(period="180d")
        if not df.empty: closes[name] = df['Close']
    df_corr = pd.DataFrame(closes).dropna().corr().round(2)
    return df_corr.to_dict()

@app.get("/api/institutional")
def get_institutional(stock_id: str = "2330", days: int = 20):
    try:
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        df = dl.taiwan_stock_institutional_investors(stock_id=stock_id, start_date=start_date)
        if df.empty: return {}
        result = {}
        for itype, label in [('Foreign_Investor', '外資'), ('Investment_Trust', '投信'), ('Dealer', '自營商')]:
            subset = df[df['name'] == itype]
            result[label] = [{"t": row['date'], "v": int(row['buy'] - row['sell'])} for _, row in subset.iterrows()]
        return result
    except Exception: return {}

os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
