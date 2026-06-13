# app.py — FastAPI v4
import logging, os
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from config import CACHE_DIR, LOGS_DIR, SNAPSHOT_DIR
from cache import FileCache
from scheduler.collector import start_all
from services import macro_service, heatmap_service, risk_service, market_service

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("app")

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
    """首頁 KPI + 主要市場行情 (配合 V4 前端)"""
    overview = macro_service.get_global_overview()
    
    # 安全地獲取市場資料
    indices = overview.get("indices") or {}
    
    # 計算風險評分 (防呆：處理 None 或 空字典)
    up_count = 0
    total = 0
    for m in indices.values():
        total += 1
        # 如果 pct 是 None，視為不變 (0)
        pct = m.get("pct")
        if pct is not None and pct > 0:
            up_count += 1
            
    score = round((up_count / total * 100) if total > 0 else 50)

    # 轉換市場行情格式
    major_markets = []
    for name, data in indices.items():
        cur_val = data.get("current")
        pct_val = data.get("pct")
        major_markets.append({
            "name": name, 
            "country": data.get("country", "Global"), 
            "current": f"{cur_val:,}" if cur_val is not None and isinstance(cur_val, (int, float)) else "--", 
            "trend": "up" if (pct_val or 0) > 0 else "down"
        })

    return {
        "risk_score": score,
        "major_markets": major_markets,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@app.get("/api/heatmap")
def api_heatmap():
    """配合前端 renderHeatmapMatrix 的格式"""
    raw_heatmap = macro_service.get_heatmap()
    
    def transform(section):
        res = {}
        data = raw_heatmap.get(section, {})
        cols = data.get("cols", [])
        rows = data.get("rows", [])
        cells = data.get("cells", {})
        for c in cols:
            res[c] = {}
            for r in rows:
                signal = cells.get(f"{r}_{c}", {}).get("signal", 0)
                res[c][r] = signal
        return res

    return {
        "Liquidity": transform("liquidity"),
        "Inflation": transform("inflation")
    }


# ── 國家 Dashboard ──────────────────────────────────────────────────

@app.get("/api/macro/countries")
def api_countries():
    return ["TW", "US", "JP", "SG"]


@app.get("/api/macro/{country}")
def api_macro_country(country: str):
    """指定國家的總經指標（平鋪回列表供前端 map）"""
    country = country.upper()
    data = macro_service.get_country_macro(country) # 這是按 category 分組的字典
    
    flattened = []
    for cat, items in data.items():
        for item in items:
            # 確保欄位名稱與前端一致 {date, value}
            item["series"] = [{"date": p["t"], "value": p["v"]} for p in item.get("series", [])]
            flattened.append(item)
    
    return {"country": country, "indicators": flattened}


# ── 市場行情 ────────────────────────────────────────────────────────

@app.get("/api/markets")
def api_markets():
    """所有市場行情"""
    return macro_service.get_market_all()


# ── 個股 & 財報 ─────────────────────────────────────────────────────

@app.get("/api/stocks/{country}/valuation")
def api_valuation_table(country: str):
    """估值排行表"""
    return macro_service.get_valuation_table(country.upper())


@app.get("/api/stocks/{country}/{ticker}")
def api_company(country: str, ticker: str):
    """單一公司完整快照"""
    return macro_service.get_company(ticker.upper(), country.upper())


# ── 系統狀態 ────────────────────────────────────────────────────────

@app.get("/api/status")
def api_status():
    """系統狀態"""
    macro_data = macro_service.get_macro_all()
    market_data = macro_service.get_market_all()
    return {
        "status": "online",
        "datasets": {
            "macro": len(macro_data),
            "market": len(market_data)
        }
    }
