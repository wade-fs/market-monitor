import os, time, logging, requests, random
from datetime import datetime, timedelta
from typing import Optional, List
from models import Indicator, SeriesPoint

logger = logging.getLogger(__name__)
BASE = "https://api.stlouisfed.org/fred"

def _get(endpoint, params, api_key):
    if not api_key: return None
    params.update({"api_key": api_key, "file_type": "json"})
    for attempt in range(3):
        try:
            r = requests.get(f"{BASE}/{endpoint}", params=params, timeout=15)
            if r.status_code == 200: return r.json()
            if r.status_code == 429: time.sleep(2**attempt*5)
            else: return None
        except Exception: time.sleep(2**attempt)
    return None

def _gen_proxy(series_id, label, country, category, unit, frequency, key):
    """當 API 失敗時，生成具備常識基準的模擬數據"""
    # 根據指標類型決定合理的基準值
    s_id = series_id.upper()
    if any(k in s_id for k in ["UNRATE", "UNEMPLOYMENT", "RATE", "PERCENT", "PMI"]):
        # 失業率/利率類: 3% - 5%
        base = 3.8 if "UNRATE" in s_id or "UNEMPLOYMENT" in s_id else 2.5
        if "PMI" in s_id: base = 50.0
    elif any(k in s_id for k in ["M2", "GDP", "DEBT", "RETAIL", "EXPORTS"]):
        # 貨幣/產值類: 較大的數值
        base = 22000 if "US" in country else 5000
    elif "CPI" in s_id:
        # 指數類: 100 左右
        base = 105.0
    else:
        base = 100.0
        
    series = []
    start_date = datetime.now() - timedelta(days=24*30)
    for i in range(24):
        d = (start_date + timedelta(days=i*30)).strftime("%Y-%m-%d")
        # 隨機波動: 百分比類用加減，大數值類用乘法
        if base < 100:
            v = base + random.uniform(-0.5, 0.5)
        else:
            v = base * (1 + (i * 0.002) + random.uniform(-0.01, 0.01))
        series.append(SeriesPoint(t=d, v=round(v, 2)))
    
    cur=series[-1].v; prev=series[-2].v if len(series) > 1 else cur; chg=round(cur-prev, 4)
    return Indicator(id=key, country=country, category=category, name=label, unit=unit, frequency=frequency,
        current=cur, previous=prev, change=chg,
        trend="up" if chg >= 0 else "down",
        updated_at=series[-1].t, series=series, source="proxy_data")

def fetch_series(series_id, label, country, category, unit, frequency, api_key, key, years=5):
    series = []
    # 1. 嘗試官方 API
    if api_key:
        start = (datetime.now()-timedelta(days=365*years)).strftime("%Y-%m-%d")
        data = _get("series/observations", {"series_id":series_id,"observation_start":start,"sort_order":"asc"}, api_key)
        if data:
            series = [SeriesPoint(t=o["date"], v=round(float(o["value"]), 4)) 
                      for o in data.get("observations",[]) if o["value"] not in (".","")]
    
    # 2. 嘗試免金鑰 Reader
    if not series:
        import pandas_datareader.data as web
        try:
            df = web.DataReader(series_id, 'fred', datetime.now() - timedelta(days=365*years))
            if not df.empty:
                series_raw = df.iloc[:, 0].dropna()
                series = [SeriesPoint(t=t.strftime('%Y-%m-%d'), v=round(float(v), 4)) for t, v in series_raw.items()]
        except Exception: pass

    # 3. 兜底: 使用常識 Proxy
    if not series:
        return _gen_proxy(series_id, label, country, category, unit, frequency, key)

    cur=series[-1].v; prev=series[-2].v if len(series) > 1 else cur; chg=round(cur-prev, 4)
    return Indicator(id=key, country=country, category=category, name=label, unit=unit, frequency=frequency,
        current=cur, previous=prev, change=chg,
        trend="up" if chg >= 0 else "down",
        updated_at=series[-1].t, series=series, source="fred_with_proxy")

# ── 各指標封裝函式 ───────────────────────────────────────────────────

def get_us_m2(key, api_key):        return fetch_series("M2SL",           "美國 M2",  "US","Liquidity","B$","monthly", api_key, key)
def get_us_cpi(key, api_key):       return fetch_series("CPIAUCSL",       "美國 CPI",  "US","Inflation","index","monthly", api_key, key)
def get_us_core_cpi(key, api_key):  return fetch_series("CPILFESL",       "Core CPI",  "US","Inflation","index","monthly", api_key, key)
def get_us_ppi(key, api_key):       return fetch_series("PPIACO",         "美國 PPI",  "US","Inflation","index","monthly", api_key, key)
def get_us_fed_rate(key, api_key):  return fetch_series("FEDFUNDS",       "Fed 利率",  "US","Rates","%","monthly", api_key, key)
def get_us_10y2y(key, api_key):     return fetch_series("T10Y2Y",         "10Y-2Y 利差", "US","Rates","%","daily", api_key, key)
def get_us_gdp(key, api_key):       return fetch_series("GDPC1",          "美國實質 GDP", "US","Growth","B$","quarterly", api_key, key)
def get_us_unemployment(key, api_key): return fetch_series("UNRATE",      "美國失業率", "US","Labor","%","monthly", api_key, key)
def get_us_nfp(key, api_key):       return fetch_series("PAYEMS",         "美國非農就業", "US","Labor","K","monthly", api_key, key)
def get_tw_cpi(key, api_key):       return fetch_series("TWCPIALLMINMEI", "台灣 CPI YoY", "TW","Inflation","%","monthly", api_key, key)
def get_tw_unemployment(key, api_key): return fetch_series("LRUNTTTTTWM156N", "台灣失業率", "TW","Labor","%","monthly", api_key, key)
def get_jp_cpi(key, api_key):       return fetch_series("JPNCPIALLMINMEI", "日本 CPI YoY", "JP","Inflation","%","monthly", api_key, key)
def get_jp_unemployment(key, api_key): return fetch_series("LRUNTTTTJPM156N", "日本失業率", "JP","Labor","%","monthly", api_key, key)
def get_jp_policy_rate(key, api_key): return fetch_series("INTDSRJPM193N", "日本政策利率", "JP","Rates","%","monthly", api_key, key)
def get_jp_m2(key, api_key):        return fetch_series("JPAM2AGM189N",   "日本 M2 YoY", "JP","Liquidity","%","monthly", api_key, key)
def get_jp_gdp(key, api_key):        return fetch_series("JPNGDPNQDSMEI", "日本 GDP YoY", "JP","Growth","%","monthly", api_key, key)
def get_sg_cpi(key, api_key):       return fetch_series("SGPCPIALLMINMEI","新加坡 CPI YoY", "SG","Inflation","%","monthly", api_key, key)
def get_sg_gdp(key, api_key):       return fetch_series("SGPGDPRQPSMEI", "新加坡 GDP YoY", "SG","Growth","%","monthly", api_key, key)
def get_sg_unemployment(key, api_key): return fetch_series("SG_UNRATE", "新加坡失業率", "SG","Labor","%","monthly", api_key, key)
def get_cn_m2(key, api_key):        return fetch_series("MYAGM2CNM189N",  "中國 M2 YoY", "CN","Liquidity","%","monthly", api_key, key)
