# app.py — FastAPI v4
import logging, os
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys; sys.path.insert(0, '/home/claude/market-monitor-v4/backend')

from config import CACHE_DIR, LOGS_DIR, SNAPSHOT_DIR
from cache import FileCache
from scheduler.collector import start_all
from services.macro_service import (
    get_global_overview, get_country_macro, get_heatmap,
    get_market_all, get_fundamentals_tw, get_fundamentals_us,
    get_company, get_valuation_table,
)

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("app")

# ── 確保目錄存在 ────────────────────────────────────────────────────
for d in [CACHE_DIR, LOGS_DIR, SNAPSHOT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

cache = FileCache(CACHE_DIR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """docker run 一啟動就開始後台抓取，不需等前端連線"""
    logger.info("🚀 啟動後台資料收集器...")
    threads = start_all()
    logger.info(f"✅ {len(threads)} 條排程執行緒已啟動")
    yield
    logger.info("🛑 服務關閉")


app = FastAPI(title="Macro Intelligence Platform v4", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── 總覽 ────────────────────────────────────────────────────────────

@app.get("/api/global")
def api_global():
    """首頁 KPI + 主要市場行情"""
    return get_global_overview()


@app.get("/api/heatmap")
def api_heatmap():
    """Liquidity / Inflation Heatmap（含 signal 1/0/-1）"""
    return get_heatmap()


# ── 國家 Dashboard ──────────────────────────────────────────────────

@app.get("/api/macro/countries")
def api_countries():
    return ["TW", "US", "JP"]


@app.get("/api/macro/{country}")
def api_macro_country(country: str):
    """指定國家的總經指標（按 category 分組）"""
    country = country.upper()
    if country not in ["TW", "US", "JP"]:
        raise HTTPException(status_code=404, detail=f"不支援國家: {country}")
    return {
        "country": country,
        "indicators": get_country_macro(country),
    }


# ── 市場行情 ────────────────────────────────────────────────────────

@app.get("/api/markets")
def api_markets():
    """所有市場行情（指數 / FX / Crypto / Commodity）"""
    return get_market_all()


# ── 個股 & 財報 ─────────────────────────────────────────────────────

@app.get("/api/stocks/{country}/universe")
def api_stock_universe(country: str):
    """回傳成分股清單"""
    import sys; sys.path.insert(0, '/home/claude/market-monitor-v4/backend')
    from universe import TW_TWSE50, TW_NAMES, US_SP100, US_NAMES
    country = country.upper()
    if country == "TW":
        return [{"ticker": s, "name": TW_NAMES.get(s, s)} for s in TW_TWSE50]
    elif country == "US":
        return [{"ticker": s, "name": US_NAMES.get(s, s)} for s in US_SP100]
    raise HTTPException(status_code=404, detail=f"不支援: {country}")


@app.get("/api/stocks/{country}/valuation")
def api_valuation_table(country: str):
    """估值排行表（P/E、P/B、殖利率、ROE）"""
    country = country.upper()
    if country not in ["TW", "US"]:
        raise HTTPException(status_code=404, detail=f"不支援: {country}")
    return get_valuation_table(country)


@app.get("/api/stocks/{country}/{ticker}")
def api_company(country: str, ticker: str):
    """單一公司完整快照（行情 + 財報 + 估值）"""
    country = country.upper()
    data = get_company(ticker.upper(), country)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data


@app.get("/api/stocks/{country}/{ticker}/fundamentals")
def api_fundamentals(country: str, ticker: str):
    """單一公司財報時序（最近 8 季）"""
    data = get_company(ticker.upper(), country.upper())
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data.get("fundamentals", [])


@app.get("/api/stocks/{country}/{ticker}/valuation")
def api_stock_valuation(country: str, ticker: str):
    data = get_company(ticker.upper(), country.upper())
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data.get("valuation", {})


# ── 系統狀態 ────────────────────────────────────────────────────────

@app.get("/api/status")
def api_status():
    """Cache 狀態 + 各資料集最後更新時間"""
    stats = cache.stats()
    macro_data = cache.get("macro_all", 999999) or {}
    market_data = cache.get("market_all", 999999) or {}
    tw_data = cache.get("fundamentals_tw", 999999) or {}
    us_data = cache.get("fundamentals_us", 999999) or {}
    return {
        "cache": stats,
        "datasets": {
            "macro":          {"count": len(macro_data),  "ready": len(macro_data) > 0},
            "market":         {"count": len(market_data), "ready": len(market_data) > 0},
            "fundamentals_tw":{"count": len(tw_data),     "ready": len(tw_data) > 0},
            "fundamentals_us":{"count": len(us_data),     "ready": len(us_data) > 0},
        }
    }


# ── 靜態前端 ────────────────────────────────────────────────────────
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
