import yfinance as yf
import pandas_datareader.data as web
from datetime import datetime, timedelta

def fetch_yfinance_series(symbol, period="2y", is_vix=False):
    try:
        df = yf.Ticker(symbol).history(period=period)
        if df.empty: return []
        df.index = df.index.tz_localize(None).normalize()
        res = df['Close'].resample('ME').last() if not is_vix else df['Close']
        return [{"date": t.strftime('%Y-%m-%d'), "value": round(float(v), 2)} for t, v in res.tail(24).items()]
    except: return []

def fetch_fred_series(symbol, years=3):
    try:
        start = datetime.now() - timedelta(days=365*years)
        df = web.DataReader(symbol, 'fred', start)
        if df.empty: return []
        series_raw = df.iloc[:, 0].dropna()
        return [{"date": t.strftime('%Y-%m-%d'), "value": round(float(v), 2)} for t, v in series_raw.tail(24).items()]
    except: return []
