import time, logging, requests
from datetime import datetime, timedelta
from typing import Optional, List
import sys; sys.path.insert(0, '/home/claude/market-monitor-v4/backend')
from models import Indicator, SeriesPoint, Fundamentals, Valuation

logger = logging.getLogger(__name__)
BASE = "https://api.finmindtrade.com/api/v4/data"

def _get(dataset, params, token=""):
    p = {"dataset": dataset, **params}
    if token: p["token"] = token
    for attempt in range(3):
        try:
            r = requests.get(BASE, params=p, timeout=20)
            if r.status_code == 200:
                j = r.json()
                if j.get("status") == 200: return j.get("data", [])
                logger.warning(f"FinMind {dataset}: {j.get('msg')}"); return None
            if r.status_code == 429: time.sleep(2**attempt*10)
            else: return None
        except Exception as e:
            logger.error(f"FinMind({attempt+1}/3): {e}"); time.sleep(2**attempt)
    return None

def _safe_float(v):
    try: return round(float(v), 4) if v is not None else None
    except: return None

def get_tw_m2(token=""):
    start = (datetime.now()-timedelta(days=365*5)).strftime("%Y-%m-%d")
    rows = _get("TaiwanMoneySupplyM2", {"start_date": start}, token)
    if not rows: return None
    series = sorted([SeriesPoint(t=r["date"], v=round(float(r.get("annual_growth_rate",0)),4))
                     for r in rows if r.get("annual_growth_rate") is not None], key=lambda x:x.t)
    if not series: return None
    cur=series[-1].v; prev=series[-2].v if len(series)>1 else cur; chg=round(cur-prev,4)
    return Indicator(id="tw_m2",country="TW",category="Liquidity",name="台灣 M2 YoY",
        unit="%",frequency="monthly",current=cur,previous=prev,change=chg,
        trend="up" if chg>0 else "down",updated_at=series[-1].t,series=series,source="finmind")

def get_tw_m1b(token=""):
    start = (datetime.now()-timedelta(days=365*5)).strftime("%Y-%m-%d")
    rows = _get("TaiwanMoneySupplyM1b", {"start_date": start}, token)
    if not rows: return None
    series = sorted([SeriesPoint(t=r["date"], v=round(float(r.get("annual_growth_rate",0)),4))
                     for r in rows if r.get("annual_growth_rate") is not None], key=lambda x:x.t)
    if not series: return None
    cur=series[-1].v; prev=series[-2].v if len(series)>1 else cur; chg=round(cur-prev,4)
    return Indicator(id="tw_m1b",country="TW",category="Liquidity",name="台灣 M1B YoY",
        unit="%",frequency="monthly",current=cur,previous=prev,change=chg,
        trend="up" if chg>0 else "down",updated_at=series[-1].t,series=series,source="finmind")

def get_tw_fundamentals(stock_id, name, token="", quarters=8):
    start = (datetime.now()-timedelta(days=365*3)).strftime("%Y-%m-%d")
    income_rows  = _get("TaiwanStockFinancialStatements", {"data_id":stock_id,"start_date":start}, token) or []
    cf_rows      = _get("TaiwanStockCashFlowsStatement",  {"data_id":stock_id,"start_date":start}, token) or []
    eps_rows     = _get("TaiwanStockEPS",                 {"data_id":stock_id,"start_date":start}, token) or []

    income_map={}
    for r in income_rows:
        period=r.get("date",""); t=r.get("type",""); v=r.get("value")
        if v is None: continue
        income_map.setdefault(period,{})[t]=float(v)
    cf_map={}
    for r in cf_rows:
        period=r.get("date",""); t=r.get("type",""); v=r.get("value")
        if v is None: continue
        cf_map.setdefault(period,{})[t]=float(v)
    eps_map={r.get("date",""): float(r.get("EPS",0)) for r in eps_rows if r.get("EPS") is not None}

    results=[]
    for period in sorted(income_map.keys(),reverse=True)[:quarters]:
        inc=income_map[period]; cf=cf_map.get(period,{})
        rev     = inc.get("營業收入合計") or inc.get("收入")
        gross   = inc.get("營業毛利（毛損）") or inc.get("毛利")
        op_inc  = inc.get("營業利益（損失）") or inc.get("營業利益")
        net_inc = inc.get("本期淨利（淨損）") or inc.get("淨利")
        cfo     = cf.get("營業活動之淨現金流入（流出）") or cf.get("營業活動現金流")
        capex   = cf.get("取得不動產、廠房及設備") or cf.get("資本支出")
        eps     = eps_map.get(period)
        def pct(a,b): return round(a/b*100,2) if a and b else None
        fcf = (cfo+capex) if (cfo is not None and capex is not None) else None
        results.append(Fundamentals(
            ticker=stock_id,name=name,country="TW",period=period,
            revenue=rev,gross_profit=gross,operating_income=op_inc,net_income=net_inc,eps=eps,
            gross_margin=pct(gross,rev),op_margin=pct(op_inc,rev),net_margin=pct(net_inc,rev),
            cfo=cfo,capex=capex,fcf=fcf,source="finmind"))
    return results

def get_tw_valuation(stock_id, name, token=""):
    start = (datetime.now()-timedelta(days=90)).strftime("%Y-%m-%d")
    rows = _get("TaiwanStockPER", {"data_id":stock_id,"start_date":start}, token)
    if not rows: return Valuation(ticker=stock_id,name=name,country="TW",
        date=datetime.now().strftime("%Y-%m-%d"),error="FinMind 無回應",source="finmind")
    latest = sorted(rows, key=lambda x:x.get("date",""), reverse=True)[0]
    return Valuation(ticker=stock_id,name=name,country="TW",date=latest.get("date",""),
        pe=_safe_float(latest.get("PER")), pb=_safe_float(latest.get("PBR")),
        dividend_yield=_safe_float(latest.get("DividendYield")), source="finmind")

def get_tw_institutional(stock_id, token="", days=60):
    start = (datetime.now()-timedelta(days=days)).strftime("%Y-%m-%d")
    rows = _get("TaiwanStockInstitutionalInvestorsBuySell",{"data_id":stock_id,"start_date":start},token) or []
    result={}
    for r in rows:
        inv=r.get("name",""); net=int(r.get("buy",0))-int(r.get("sell",0))
        result.setdefault(inv,[]).append({"t":r["date"],"v":net})
    return result
