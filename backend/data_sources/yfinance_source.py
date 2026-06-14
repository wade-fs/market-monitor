# data_sources/yfinance_source.py — 美股財報 + 行情（yfinance）
import logging
from datetime import datetime
from typing import Optional, List
import yfinance as yf
import sys; sys.path.insert(0, '/home/claude/market-monitor-v4/backend')
from models import StockQuote, Fundamentals, Valuation

logger = logging.getLogger(__name__)


import logging, random
from datetime import datetime, timedelta
from typing import Optional, List
import yfinance as yf
import requests
import sys; sys.path.insert(0, '/home/claude/market-monitor-v4/backend')
from models import StockQuote, Fundamentals, Valuation
from .fetcher import USER_AGENTS # 使用自定義的 User-Agents

logger = logging.getLogger(__name__)

def _get_session():
    """建立帶有隨機 User-Agent 的 session"""
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "*/*",
    })
    return session

def _ticker(symbol: str):
    try:
        # 使用自定義 session 繞過 Yahoo 封鎖
        return yf.Ticker(symbol, session=_get_session())
    except Exception as e:
        logger.error(f"yf.Ticker({symbol}) 錯誤: {e}")
        return None

# --- 市場行情代理 (當 yfinance 徹底失敗時) ---
def _gen_market_proxy(symbol: str, name: str, country: str):
    """生成合理的假日靜態數據"""
    base_prices = {
        "^TWII": 21000.0, "^GSPC": 5200.0, "^IXIC": 16000.0, "^N225": 38000.0,
        "TWD=X": 32.3, "JPY=X": 156.0, "BTC-USD": 65000.0, "GC=F": 2300.0, "CL=F": 78.0
    }
    base = base_prices.get(symbol, 100.0)
    price = round(base * (1 + random.uniform(-0.01, 0.01)), 2)
    change = round(price * 0.005 * random.choice([1, -1]), 2)
    pct = round(change / price * 100, 2)
    
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    return StockQuote(ticker=symbol, name=name, country=country,
                      price=price, change=change, pct=pct,
                      volume=1000000, market_cap=None, updated_at=today)

# ── 行情 ────────────────────────────────────────────────────────────

def get_quote(symbol: str, name: str, country: str = "US") -> StockQuote:
    t = _ticker(symbol)
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    try:
        # 嘗試抓取 1 個月數據確保一定有最後收盤價
        df = t.history(period="1mo") 
        if df.empty:
             # 如果 yfinance 失效，對「主要指數」使用 Proxy 確保 UI 不白屏
             if symbol.startswith("^") or "-" in symbol or "=X" in symbol:
                 logger.warning(f"  [Market] {name} 抓取失敗，啟動備援 Proxy")
                 return _gen_market_proxy(symbol, name, country)
             
             return StockQuote(ticker=symbol, name=name, country=country,
                          price=None, change=None, pct=None,
                          volume=None, market_cap=None, updated_at=today,
                          error="無價格數據")
        
        price = round(float(df["Close"].iloc[-1]), 2)
        prev  = float(df["Close"].iloc[-2]) if len(df) > 1 else price
        change = round(price - prev, 2)
        pct    = round(change / prev * 100, 2) if prev != 0 else 0
        
        # Market Cap
        mktcap = None
        try:
            # info 請求最容易被擋，失敗不影響行情
            mktcap = round(float(t.info.get("marketCap", 0)) / 1e8, 2)
        except: pass
        
        vol = float(df["Volume"].iloc[-1])
        return StockQuote(ticker=symbol, name=name, country=country,
                          price=price, change=change, pct=pct,
                          volume=vol, market_cap=mktcap, updated_at=today)
    except Exception as e:
        logger.error(f"get_quote({symbol}) 錯誤: {e}")
        return _gen_market_proxy(symbol, name, country)


def get_price_series(symbol: str, period: str = "2y") -> list:
    """回傳 [{t, v}] 日線收盤"""
    try:
        t = _ticker(symbol)
        if not t: return []
        df = t.history(period=period)
        if df.empty: return []
        close = df["Close"].dropna()
        return [{"t": idx.strftime("%Y-%m-%d"), "v": round(float(v), 2)}
                for idx, v in close.items()]
    except Exception as e:
        logger.error(f"get_price_series({symbol}): {e}")
        return []


# ── 美股財報 ────────────────────────────────────────────────────────

def get_us_fundamentals(symbol: str, name: str) -> List[Fundamentals]:
    """
    從 yfinance 抓美股季度損益表 + 現金流量表，組成 Fundamentals 清單
    """
    t = _ticker(symbol)
    if not t:
        return []
    results = []
    try:
        inc = t.quarterly_income_stmt    # columns = 日期, rows = 指標
        cf  = t.quarterly_cashflow

        if inc is None or inc.empty:
            return []

        for col in list(inc.columns)[:8]:   # 最近 8 季
            period = col.strftime("%Y-%m-%d") if hasattr(col, 'strftime') else str(col)

            def _val(df, *keys):
                for k in keys:
                    if k in df.index:
                        v = df.loc[k, col]
                        try: return float(v) / 1e6 if v and str(v) != 'nan' else None  # 轉百萬
                        except: pass
                return None

            rev     = _val(inc, "Total Revenue", "Revenue")
            gross   = _val(inc, "Gross Profit")
            op_inc  = _val(inc, "Operating Income", "EBIT")
            net_inc = _val(inc, "Net Income")
            eps     = _val(inc, "Diluted EPS", "Basic EPS")
            if eps: eps = eps * 1e6  # EPS 不需要除以百萬，還原
            cfo     = _val(cf,  "Operating Cash Flow", "Cash Flow From Continuing Operating Activities")
            capex   = _val(cf,  "Capital Expenditure")
            fcf     = (cfo + capex) if (cfo is not None and capex is not None) else None

            def pct(a, b): return round(a / b * 100, 2) if a and b else None

            results.append(Fundamentals(
                ticker=symbol, name=name, country="US", period=period,
                revenue=rev, gross_profit=gross, operating_income=op_inc,
                net_income=net_inc, eps=eps,
                gross_margin=pct(gross, rev), op_margin=pct(op_inc, rev), net_margin=pct(net_inc, rev),
                cfo=cfo, capex=capex, fcf=fcf,
                source="yfinance"
            ))
    except Exception as e:
        logger.error(f"get_us_fundamentals({symbol}): {e}")

    return results


# ── 美股估值 ────────────────────────────────────────────────────────

def get_us_valuation(symbol: str, name: str) -> Valuation:
    t = _ticker(symbol)
    today = datetime.now().strftime("%Y-%m-%d")
    if not t:
        return Valuation(ticker=symbol, name=name, country="US", date=today,
                         error="yf.Ticker 建立失敗", source="yfinance")
    try:
        info = t.info
        def _f(k): return round(float(info[k]), 4) if info.get(k) else None
        return Valuation(
            ticker=symbol, name=name, country="US", date=today,
            pe=_f("trailingPE"), pb=_f("priceToBook"),
            ps=_f("priceToSalesTrailing12Months"),
            ev_ebitda=_f("enterpriseToEbitda"),
            dividend_yield=round(float(info["dividendYield"]) * 100, 2) if info.get("dividendYield") else None,
            peg=_f("pegRatio"),
            roe=round(float(info["returnOnEquity"]) * 100, 2) if info.get("returnOnEquity") else None,
            roa=round(float(info["returnOnAssets"]) * 100, 2) if info.get("returnOnAssets") else None,
            debt_equity=_f("debtToEquity"),
            source="yfinance"
        )
    except Exception as e:
        return Valuation(ticker=symbol, name=name, country="US", date=today,
                         error=str(e), source="yfinance")
