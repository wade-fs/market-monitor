# scheduler/collector.py
# docker run 啟動就開始抓資料，不需要前端連線
# 三條獨立排程：市場行情 / 總經 / 財報估值

import logging, time, json
from datetime import datetime
from pathlib import Path
from threading import Thread
import sys; sys.path.insert(0, '/home/claude/market-monitor-v4/backend')

from config import (FRED_API_KEY, FINMIND_TOKEN, SCHEDULE,
                    FRED_SERIES, MARKET_SYMBOLS, CACHE_DIR, SNAPSHOT_DIR, LOGS_DIR)
from universe import TW_TWSE50, TW_NAMES, US_SP100, US_NAMES, TW_YFINANCE
from cache import FileCache
from data_sources import fred as fred_src
from data_sources import finmind as fm_src
from data_sources import yfinance_source as yf_src

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(str(LOGS_DIR / "collector.log"), encoding="utf-8")
    ]
)
logger = logging.getLogger("collector")

cache = FileCache(CACHE_DIR)
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def _save_snapshot(name: str, data: dict):
    """每次抓完存一份有時間戳的快照（方便 debug）"""
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    path = SNAPSHOT_DIR / f"{name}_{ts}.json"
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, default=str)
    except Exception as e:
        logger.warning(f"快照儲存失敗 {name}: {e}")


# ── Loop 1：市場行情（每 15 分鐘）────────────────────────────────────

def collect_market():
    logger.info("=== [市場行情] 排程啟動 ===")
    while True:
        try:
            logger.info("[市場行情] 開始抓取指數 / FX / Crypto / Commodity")
            result = {}
            for cat, symbols in MARKET_SYMBOLS.items():
                result[cat] = {}
                for name, sym in symbols.items():
                    series = yf_src.get_price_series(sym, period="1y")
                    quote  = yf_src.get_quote(sym, name, country="MARKET")
                    result[cat][name] = {
                        **quote.to_dict(),
                        "series": series[-90:]  # 最近 90 天
                    }
                    time.sleep(0.5)

            cache.set("market_all", result)
            _save_snapshot("market", result)
            logger.info(f"[市場行情] 完成，共 {sum(len(v) for v in result.values())} 筆")

        except Exception as e:
            logger.error(f"[市場行情] 例外: {e}")

        time.sleep(SCHEDULE["market_minutes"] * 60)


# ── Loop 2：總經指標（每 6 小時）─────────────────────────────────────

def collect_macro():
    logger.info("=== [總經] 排程啟動 ===")
    while True:
        try:
            result = {}

            # FRED
            if FRED_API_KEY:
                logger.info("[總經] 開始抓 FRED 指標")
                for key, cfg in FRED_SERIES.items():
                    series_id, label, country, category, unit, frequency = cfg
                    ind = fred_src.fetch_series(
                        series_id, label, country, category, unit, frequency,
                        FRED_API_KEY, key
                    )
                    if ind:
                        result[key] = ind.to_dict()
                    time.sleep(0.3)
                logger.info(f"[總經] FRED 完成，{len(result)} 筆")
            else:
                logger.warning("[總經] FRED_API_KEY 未設定，跳過")

            # FinMind 台灣 M2 / M1B
            if FINMIND_TOKEN:
                logger.info("[總經] 開始抓 FinMind M2/M1B")
                for fn, key in [
                    (fm_src.get_tw_m2,  "TW_M2"),
                    (fm_src.get_tw_m1b, "TW_M1B"),
                ]:
                    ind = fn(FINMIND_TOKEN)
                    if ind:
                        result[key] = ind.to_dict()
            else:
                logger.warning("[總經] FINMIND_TOKEN 未設定，跳過 M2/M1B")

            cache.set("macro_all", result)
            _save_snapshot("macro", result)
            logger.info(f"[總經] 完成，共 {len(result)} 筆指標")

        except Exception as e:
            logger.error(f"[總經] 例外: {e}")

        time.sleep(SCHEDULE["macro_hours"] * 3600)


# ── Loop 3：財報 + 估值（每 24 小時）────────────────────────────────

def collect_fundamentals():
    logger.info("=== [財報/估值] 排程啟動 ===")
    while True:
        try:
            tw_result = {}
            us_result = {}

            # ── 台灣：TWSE50 FinMind ──────────────────────────────
            if FINMIND_TOKEN:
                logger.info(f"[財報] 開始抓台灣 TWSE50 ({len(TW_TWSE50)} 檔)")
                for i, stock_id in enumerate(TW_TWSE50):
                    name = TW_NAMES.get(stock_id, stock_id)
                    try:
                        fundamentals = fm_src.get_tw_fundamentals(stock_id, name, FINMIND_TOKEN)
                        valuation    = fm_src.get_tw_valuation(stock_id, name, FINMIND_TOKEN)
                        quote        = yf_src.get_quote(TW_YFINANCE[stock_id], name, "TW")
                        tw_result[stock_id] = {
                            "ticker":      stock_id,
                            "name":        name,
                            "country":     "TW",
                            "quote":       quote.to_dict(),
                            "fundamentals":[f.to_dict() for f in fundamentals],
                            "valuation":   valuation.to_dict() if valuation else None,
                        }
                        logger.info(f"  TW [{i+1}/{len(TW_TWSE50)}] {stock_id} {name} OK")
                    except Exception as e:
                        logger.warning(f"  TW {stock_id} 失敗: {e}")
                    time.sleep(1.5)   # FinMind 免費版友善限速

                cache.set("fundamentals_tw", tw_result)
                _save_snapshot("fundamentals_tw", tw_result)
                logger.info(f"[財報] 台灣完成，{len(tw_result)} 檔")
            else:
                logger.warning("[財報] FINMIND_TOKEN 未設定，跳過台股財報")

            # ── 美國：S&P100 yfinance ──────────────────────────────
            logger.info(f"[財報] 開始抓美國 S&P100 ({len(US_SP100)} 檔)")
            for i, sym in enumerate(US_SP100):
                name = US_NAMES.get(sym, sym)
                try:
                    fundamentals = yf_src.get_us_fundamentals(sym, name)
                    valuation    = yf_src.get_us_valuation(sym, name)
                    quote        = yf_src.get_quote(sym, name, "US")
                    us_result[sym] = {
                        "ticker":      sym,
                        "name":        name,
                        "country":     "US",
                        "quote":       quote.to_dict(),
                        "fundamentals":[f.to_dict() for f in fundamentals],
                        "valuation":   valuation.to_dict() if valuation else None,
                    }
                    logger.info(f"  US [{i+1}/{len(US_SP100)}] {sym} {name} OK")
                except Exception as e:
                    logger.warning(f"  US {sym} 失敗: {e}")
                time.sleep(1.0)

            cache.set("fundamentals_us", us_result)
            _save_snapshot("fundamentals_us", us_result)
            logger.info(f"[財報] 美國完成，{len(us_result)} 檔")

        except Exception as e:
            logger.error(f"[財報/估值] 例外: {e}")

        time.sleep(SCHEDULE["fundamentals_hours"] * 3600)


# ── 啟動所有 loop（daemon threads）──────────────────────────────────

def start_all():
    threads = [
        Thread(target=collect_market,       name="market",       daemon=True),
        Thread(target=collect_macro,        name="macro",        daemon=True),
        Thread(target=collect_fundamentals, name="fundamentals", daemon=True),
    ]
    for t in threads:
        t.start()
        logger.info(f"Thread [{t.name}] 已啟動")
    return threads
