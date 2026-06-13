# services/macro_service.py — 讀 cache，組裝 API 回傳格式
import sys; sys.path.insert(0, '/home/claude/market-monitor-v4/backend')
from cache import FileCache
from config import CACHE_DIR, SCHEDULE

cache = FileCache(CACHE_DIR)

# TTL（秒）：比排程間隔稍長，避免剛好過期時短暫空值
_TTL = {
    "market":       SCHEDULE["market_minutes"] * 60 + 300,
    "macro":        SCHEDULE["macro_hours"] * 3600 + 3600,
    "fundamentals": SCHEDULE["fundamentals_hours"] * 3600 + 7200,
}

COUNTRY_MACRO_KEYS = {
    "TW": ["TW_CPI", "TW_UNEMPLOYMENT", "TW_EXPORTS", "TW_M2", "TW_M1B"],
    "US": ["US_M2", "US_CPI", "US_CORE_CPI", "US_PPI", "US_FED_RATE",
           "US_10Y", "US_2Y", "US_10Y2Y", "US_GDP_YOY", "US_UNEMPLOYMENT",
           "US_NFP", "US_RETAIL"],
    "JP": ["JP_CPI", "JP_UNEMPLOYMENT", "JP_M2", "JP_POLICY_RATE"],
}

CATEGORY_ORDER = ["Growth", "Inflation", "Liquidity", "Rates", "Labor", "Trade", "FX", "Market"]


def get_macro_all() -> dict:
    return cache.get("macro_all", _TTL["macro"]) or {}


def get_market_all() -> dict:
    return cache.get("market_all", _TTL["market"]) or {}


def get_fundamentals_tw() -> dict:
    return cache.get("fundamentals_tw", _TTL["fundamentals"]) or {}


def get_fundamentals_us() -> dict:
    return cache.get("fundamentals_us", _TTL["fundamentals"]) or {}


def get_country_macro(country: str) -> dict:
    """組裝單一國家的總經指標，按 category 分組"""
    macro = get_macro_all()
    keys  = COUNTRY_MACRO_KEYS.get(country, [])
    grouped: dict = {}
    for k in keys:
        ind = macro.get(k)
        if not ind:
            continue
        cat = ind.get("category", "Other")
        grouped.setdefault(cat, []).append(ind)
    # 按 category 排序
    return {cat: grouped[cat] for cat in CATEGORY_ORDER if cat in grouped}


def get_global_overview() -> dict:
    """首頁用：精選重要 KPI + 市場行情概覽"""
    macro  = get_macro_all()
    market = get_market_all()

    kpis = []
    for k in ["US_FED_RATE", "US_10Y2Y", "US_CPI", "US_M2", "TW_CPI", "TW_M2", "JP_CPI"]:
        ind = macro.get(k)
        if ind:
            kpis.append({
                "id":      ind["id"],
                "name":    ind["name"],
                "country": ind["country"],
                "current": ind["current"],
                "change":  ind["change"],
                "trend":   ind["trend"],
                "unit":    ind["unit"],
            })

    indices = {k: v for k, v in market.get("index", {}).items()}
    fx      = {k: v for k, v in market.get("fx", {}).items()}

    return {
        "kpis":    kpis,
        "indices": indices,
        "fx":      fx,
        "updated_at": max(
            (macro.get(k, {}).get("updated_at", "") for k in ["US_CPI", "US_M2"]),
            default=""
        ),
    }


def get_heatmap() -> dict:
    """
    Liquidity / Inflation heatmap
    signal: 1=positive 0=neutral -1=negative
    """
    macro = get_macro_all()

    THRESHOLDS = {
        "US_M2":       ("up",   -1,  3),
        "TW_M2":       ("up",    3,  7),
        "JP_M2":       ("up",    1,  5),
        "US_CPI":      ("down",  2,  3.5),
        "TW_CPI":      ("down",  1,  2.5),
        "JP_CPI":      ("down",  0,  2),
        "US_CORE_CPI": ("down",  2,  3.5),
        "US_FED_RATE": ("down",  2,  4),
        "US_10Y2Y":    ("up",   -0.5, 1),
    }

    def _signal(key, value):
        if key not in THRESHOLDS or value is None:
            return 0
        direction, lo, hi = THRESHOLDS[key]
        if lo <= value <= hi:
            return 0
        if direction == "up":
            return 1 if value > hi else -1
        else:
            return -1 if value > hi else 1

    heatmap = {
        "liquidity": {
            "rows": ["M2", "M1B"],
            "cols": ["TW", "US", "JP"],
            "cells": {}
        },
        "inflation": {
            "rows": ["CPI", "Core CPI", "PPI"],
            "cols": ["TW", "US", "JP"],
            "cells": {}
        },
    }

    mapping = {
        ("liquidity", "M2",      "TW"): "TW_M2",
        ("liquidity", "M2",      "US"): "US_M2",
        ("liquidity", "M2",      "JP"): "JP_M2",
        ("liquidity", "M1B",     "TW"): "TW_M1B",
        ("inflation", "CPI",     "TW"): "TW_CPI",
        ("inflation", "CPI",     "US"): "US_CPI",
        ("inflation", "CPI",     "JP"): "JP_CPI",
        ("inflation", "Core CPI","US"): "US_CORE_CPI",
        ("inflation", "PPI",     "US"): "US_PPI",
    }

    for (section, row, col), key in mapping.items():
        ind = macro.get(key)
        val = ind["current"] if ind else None
        heatmap[section]["cells"][f"{row}_{col}"] = {
            "value":  val,
            "signal": _signal(key, val),
            "label":  f"{val}" if val is not None else "N/A",
        }

    return heatmap


def get_company(ticker: str, country: str) -> dict:
    """取得單一公司快照"""
    if country == "TW":
        data = get_fundamentals_tw()
        return data.get(ticker, {"error": f"{ticker} 資料尚未載入"})
    else:
        data = get_fundamentals_us()
        return data.get(ticker, {"error": f"{ticker} 資料尚未載入"})


def get_valuation_table(country: str) -> list:
    """回傳估值排行表（按 P/E 排序）"""
    if country == "TW":
        data = get_fundamentals_tw()
    else:
        data = get_fundamentals_us()

    rows = []
    for ticker, company in data.items():
        val = company.get("valuation") or {}
        q   = company.get("quote") or {}
        fund_list = company.get("fundamentals") or [{}]
        latest_fund = fund_list[0] if fund_list else {}
        rows.append({
            "ticker":   ticker,
            "name":     company.get("name", ticker),
            "price":    q.get("price"),
            "mktcap":   q.get("market_cap"),
            "pe":       val.get("pe"),
            "pb":       val.get("pb"),
            "dy":       val.get("dividend_yield"),
            "roe":      val.get("roe"),
            "eps":      latest_fund.get("eps"),
            "net_margin": latest_fund.get("net_margin"),
            "revenue_yoy": latest_fund.get("revenue_yoy"),
        })

    rows.sort(key=lambda x: (x["pe"] is None, x["pe"] or 0))
    return rows
