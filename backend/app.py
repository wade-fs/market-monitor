import os
import yfinance as yf
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from FinMind.data import DataLoader

app = FastAPI(title="Market Monitor MVP")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

dl = DataLoader()

# Symbols for Yahoo Finance
SYMBOLS = {
    "US10Y": "^TNX",
    "DXY": "DX-Y.NYB",
    "TWII": "^TWII",
    "TWD": "TWD=X"
}

def get_yfinance_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="5d")
        if not data.empty:
            history = [round(v, 2) for v in data['Close'].tolist()]
            current = history[-1]
            prev = history[-2] if len(history) > 1 else current
            change = round(current - prev, 2)
            pct_change = round((change / prev) * 100, 2) if prev != 0 else 0
            return {"value": current, "history": history, "change": change, "pct": pct_change}
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
    return {"value": 0, "history": [0,0,0,0,0], "change": 0, "pct": 0}

def get_finmind_taiwan_indicators():
    try:
        start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
        df_inv = dl.taiwan_stock_institutional_investors(stock_id='2330', start_date=start_date)
        if not df_inv.empty:
            foreign_data = df_inv[df_inv['name'] == 'Foreign_Investor']
            if not foreign_data.empty:
                latest = foreign_data.iloc[-1]
                net_buy = int(latest['buy'] - latest['sell'])
                return {"value": net_buy, "date": latest['date'], "source": "FinMind"}
    except Exception as e:
        print(f"FinMind error: {e}")
    return {"value": 0, "error": "Failed to fetch"}

@app.get("/api/dashboard")
def get_dashboard_data():
    macro = {
        "US10Y": get_yfinance_data(SYMBOLS["US10Y"]),
        "DXY": get_yfinance_data(SYMBOLS["DXY"]),
        "CPI": {"value": 3.1, "change": 0.1, "note": "Target: 2.0%"},
    }
    taiwan = {
        "TWII": get_yfinance_data(SYMBOLS["TWII"]),
        "TWD": get_yfinance_data(SYMBOLS["TWD"]),
        "ForeignFlow": get_finmind_taiwan_indicators()
    }
    
    # Alert Logic based on README
    alerts = []
    if macro["US10Y"]["value"] > 4.5:
        alerts.append({"level": "warning", "msg": "高殖利率警訊：美債 10Y 突破 4.5%，科技股壓力增大。"})
    if macro["DXY"]["value"] > 105:
        alerts.append({"level": "warning", "msg": "強勢美元警訊：資金可能回流美國，新興市場承壓。"})
    if taiwan["ForeignFlow"]["value"] < -10000000:
        alerts.append({"level": "danger", "msg": "外資大幅提款：外資單日大幅賣超，注意回檔風險。"})
    if macro["CPI"]["value"] > 3.0:
        alerts.append({"level": "info", "msg": "通膨維持高位：CPI 仍高於 3%，降息預期可能延後。"})

    return {
        "macro": macro,
        "taiwan": taiwan,
        "alerts": alerts,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# Serve static files
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
