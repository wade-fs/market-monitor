# scheduler/collector.py — Spirit 5 高穩定性排程引擎
import logging
import time
import random
from datetime import datetime, timezone
import pytz
from threading import Thread
import os

from config import (FRED_API_KEY, FINMIND_TOKEN, SCHEDULE,
                    FRED_SERIES, MARKET_SYMBOLS, CACHE_DIR, LOGS_DIR)
from universe import TW_TWSE50, TW_NAMES, US_SP100, US_NAMES, TW_YFINANCE
from cache import FileCache
from data_sources import fred as fred_src
from data_sources import finmind as fm_src
from data_sources import yfinance_source as yf_src

logger = logging.getLogger("collector")
cache = FileCache(CACHE_DIR)

# --- 時區設定 ---
TZ_MAP = {
    "TW": pytz.timezone("Asia/Taipei"),
    "US": pytz.timezone("America/New_York"),
    "JP": pytz.timezone("Asia/Tokyo"),
    "SG": pytz.timezone("Asia/Singapore")
}

def is_market_open(country_code):
    """判斷該地區是否處於交易時段 (9:00 - 16:00)"""
    tz = TZ_MAP.get(country_code, timezone.utc)
    now = datetime.now(tz)
    # 週末不抓行情
    if now.weekday() >= 5: return False
    return 9 <= now.hour <= 16

# --- 核心邏輯 1: 慢速分批同步市場行情 ---
def collect_market():
    logger.info("=== [Spirit 5] 市場行情排程啟動 ===")
    while True:
        try:
            all_tasks = []
            for cat, symbols in MARKET_SYMBOLS.items():
                for name, sym in symbols.items():
                    country = "US"
                    if "TAIEX" in name or "TWD" in name: country = "TW"
                    elif "N225" in name or "JPY" in name: country = "JP"
                    elif "STI" in name or "SGD" in name: country = "SG"
                    all_tasks.append((cat, name, sym, country))
            
            random.shuffle(all_tasks)
            for cat, name, sym, country in all_tasks:
                current_cache = cache.get("market_all", 7*24*3600) or {}

                # 判定：是否需要更新？ (開盤中 OR 快取內沒資料 OR 快取內資料是空的/null)
                cached_item = current_cache.get(cat, {}).get(name, {})
                has_data = cached_item.get("price") is not None

                needs_update = is_market_open(country) or not has_data

                if needs_update:
                    try:
                        logger.info(f"  [Market] 正在抓取: {name} ({sym})...")
                        series = yf_src.get_price_series(sym, period="1y")
                        quote  = yf_src.get_quote(sym, name, country=country)

                        if cat not in current_cache: current_cache[cat] = {}
                        current_cache[cat][name] = {**quote.to_dict(), "series": series[-60:]}

                        # 抓到一筆存一筆，確保持久化
                        cache.set("market_all", current_cache)
                        time.sleep(random.uniform(3, 8)) # 稍微加快初次填滿速度
                    except Exception as e:
                        logger.warning(f"  [Market] {name} 失敗: {e}")

            
            logger.info("✅ 市場行情一輪同步結束。")
        except Exception as e:
            logger.error(f"[Market] 全域例外: {e}")
        
        time.sleep(SCHEDULE["market_minutes"] * 60)

# --- 核心邏輯 2: 低頻同步總經指標 ---
def collect_macro():
    logger.info("=== [Spirit 5] 總經指標排程啟動 ===")
    first_run = True
    while True:
        try:
            result = cache.get("macro_all", 7*24*3600) or {}
            
            items = list(FRED_SERIES.items())
            if first_run: random.shuffle(items)
            
            for key, cfg in items:
                series_id, label, country, category, unit, frequency = cfg
                # 如果快取已有且非初次啟動，可以跳過加速
                if not first_run and key in result: continue
                
                ind = fred_src.fetch_series(series_id, label, country, category, unit, frequency, FRED_API_KEY, key)
                if ind:
                    result[key] = ind.to_dict()
                    cache.set("macro_all", result)
                    logger.info(f"  [Macro] {label} 同步完成")
                
                # 初次啟動時加速 (2-5秒)，之後恢復慢速 (10-20秒)
                time.sleep(random.uniform(2, 5) if first_run else random.uniform(10, 20))

            # 2. FinMind 台灣資料
            for fn, key in [(fm_src.get_tw_m2, "TW_M2"), (fm_src.get_tw_m1b, "TW_M1B"), (fm_src.get_tw_pmi, "TW_PMI")]:
                try:
                    res = fn(FINMIND_TOKEN)
                    if res: 
                        result[key] = res.to_dict()
                        cache.set("macro_all", result)
                        logger.info(f"  [Macro] {key} 同步完成")
                except: pass
                time.sleep(2 if first_run else 5)

            first_run = False
            logger.info("✅ 總經指標一輪同步完成。")
        except Exception as e:
            logger.error(f"[Macro] 例外: {e}")
        
        time.sleep(24 * 3600)

# --- 核心邏輯 3: 超慢速同步個股財報 ---
def collect_fundamentals():
    logger.info("=== [Spirit 5] 財報估值排程啟動 ===")
    while True:
        try:
            # 台灣 50 檔
            tw_cache = cache.get("fundamentals_tw", 7*24*3600) or {}
            for stock_id in TW_TWSE50:
                if stock_id in tw_cache and not is_market_open("TW"): continue
                try:
                    name = TW_NAMES.get(stock_id, stock_id)
                    fundamentals = fm_src.get_tw_fundamentals(stock_id, name, FINMIND_TOKEN)
                    valuation    = fm_src.get_tw_valuation(stock_id, name, FINMIND_TOKEN)
                    quote        = yf_src.get_quote(TW_YFINANCE[stock_id], name, "TW")
                    tw_cache[stock_id] = {
                        "ticker":      stock_id, "name":        name, "country":     "TW",
                        "quote":       quote.to_dict(),
                        "fundamentals":[f.to_dict() for f in fundamentals],
                        "valuation":   valuation.to_dict() if valuation else None,
                    }
                    cache.set("fundamentals_tw", tw_cache)
                    logger.info(f"  [Fundamentals] TW {stock_id} OK")
                except: pass
                time.sleep(random.uniform(30, 60))

            # 美國 100 檔
            us_cache = cache.get("fundamentals_us", 7*24*3600) or {}
            for sym in US_SP100:
                if sym in us_cache and not is_market_open("US"): continue
                try:
                    name = US_NAMES.get(sym, sym)
                    fundamentals = yf_src.get_us_fundamentals(sym, name)
                    valuation    = yf_src.get_us_valuation(sym, name)
                    quote        = yf_src.get_quote(sym, name, "US")
                    us_cache[sym] = {
                        "ticker":      sym, "name":        name, "country":     "US",
                        "quote":       quote.to_dict(),
                        "fundamentals":[f.to_dict() for f in fundamentals],
                        "valuation":   valuation.to_dict() if valuation else None,
                    }
                    cache.set("fundamentals_us", us_cache)
                    logger.info(f"  [Fundamentals] US {sym} OK")
                except: pass
                time.sleep(random.uniform(30, 60))

        except Exception as e:
            logger.error(f"[Fundamentals] 例外: {e}")
        
        time.sleep(12 * 3600)

def start_all():
    threads = [
        Thread(target=collect_market, name="market", daemon=True),
        Thread(target=collect_macro, name="macro", daemon=True),
        Thread(target=collect_fundamentals, name="fundamentals", daemon=True),
    ]
    for t in threads: t.start()
    return threads
