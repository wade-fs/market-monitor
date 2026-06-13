import os, time, logging, requests
from datetime import datetime, timedelta
from typing import Optional
import sys; sys.path.insert(0, '/home/claude/market-monitor-v4/backend')
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
        except Exception as e:
            logger.error(f"FRED err({attempt+1}/3): {e}")
            time.sleep(2**attempt)
    return None

def fetch_series(series_id, label, country, category, unit, frequency, api_key, key, years=5):
    start = (datetime.now()-timedelta(days=365*years)).strftime("%Y-%m-%d")
    data = _get("series/observations", {"series_id":series_id,"observation_start":start,"sort_order":"asc"}, api_key)
    def err(msg): return Indicator(id=key, country=country, category=category, name=label,
        unit=unit, frequency=frequency, current=None, previous=None, change=None,
        trend="unknown", updated_at=datetime.now().strftime("%Y-%m-%d"), error=msg, source="fred")
    if not data: return err("FRED 無回應")
    clean = [(o["date"],float(o["value"])) for o in data.get("observations",[]) if o["value"] not in (".","")]
    if not clean: return err("資料全為空值")
    dates, values = zip(*clean)
    cur=round(values[-1],4); prev=round(values[-2],4) if len(values)>1 else cur; chg=round(cur-prev,4)
    return Indicator(id=key, country=country, category=category, name=label, unit=unit, frequency=frequency,
        current=cur, previous=prev, change=chg,
        trend="up" if chg>0 else ("down" if chg<0 else "flat"),
        updated_at=dates[-1], series=[SeriesPoint(t=d,v=round(v,4)) for d,v in clean], source="fred")
