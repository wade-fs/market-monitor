# config.py — 所有符號、FRED 序列 ID、排程設定集中管理

from pathlib import Path

# ── 儲存路徑（Docker volume 掛載點）──────────────────────────────────
DATA_DIR = Path("/data")
CACHE_DIR = DATA_DIR / "cache"
LOGS_DIR  = DATA_DIR / "logs"

# ── 排程設定 ────────────────────────────────────────────────────────
SCHEDULER = {
    "market_interval_minutes": 15,   # 市場行情（yfinance）
    "macro_interval_hours":    6,    # 宏觀數據（FRED / FinMind）
    "heatmap_interval_hours":  6,    # Heatmap 重算
}

# ── yfinance 市場符號 ────────────────────────────────────────────────
MARKET_SYMBOLS = {
    "equity": {
        "TAIEX":    "^TWII",
        "SP500":    "^GSPC",
        "NASDAQ":   "^IXIC",
        "N225":     "^N225",
        "TOPIX":    "1306.T",    # TOPIX ETF proxy
        "STI":      "^STI",
        "DAX":      "^GDAXI",
        "NIFTY":    "^NSEI",
    },
    "fx": {
        "USD_TWD":  "TWD=X",
        "USD_JPY":  "JPY=X",
        "USD_SGD":  "SGD=X",
        "DXY":      "DX-Y.NYB",
        "EUR_USD":  "EURUSD=X",
    },
    "rates": {
        "US10Y":    "^TNX",
        "US2Y":     "^IRX",     # proxy: 13-week T-Bill (closer available)
        "US30Y":    "^TYX",
    },
    "crypto": {
        "BTC":      "BTC-USD",
        "ETH":      "ETH-USD",
    },
    "commodity": {
        "GOLD":     "GC=F",
        "OIL_WTI":  "CL=F",
    },
}

# ── FRED Series ID ──────────────────────────────────────────────────
# 注意：需要 FRED_API_KEY 環境變數
FRED_SERIES = {
    # 美國
    "US_M2":          "M2SL",          # M2 貨幣供給（十億美元，月）
    "US_CPI":         "CPIAUCSL",      # CPI 全項（月）
    "US_CORE_CPI":    "CPILFESL",      # Core CPI（月）
    "US_PPI":         "PPIACO",        # PPI（月）
    "US_FED_RATE":    "FEDFUNDS",      # 聯邦基金利率（月）
    "US_10Y2Y":       "T10Y2Y",        # 10Y-2Y 利差（日）
    "US_GDP":         "GDPC1",         # 實質 GDP（季）
    "US_UNEMPLOYMENT":"UNRATE",        # 失業率（月）
    "US_NFP":         "PAYEMS",        # 非農就業（月）
    # 台灣（FRED 有部分台灣數據）
    "TW_CPI":         "TWCPIALLMINMEI",  # 台灣 CPI YoY（月）
    "TW_UNEMPLOYMENT":"LRUNTTTTTWM156N", # 台灣失業率（月）
    "TW_EXPORTS":     "XTEXVA01TWM667S", # 台灣出口（月）
    # 日本
    "JP_CPI":         "JPNCPIALLMINMEI",  # 日本 CPI（月）
    "JP_UNEMPLOYMENT":"LRUNTTTTJPM156N",  # 日本失業率（月）
    "JP_M2":          "MYAGM2JPM189N",    # 日本 M2（月）
    "JP_POLICY_RATE": "IRSTCB01JPM156N",  # 日本政策利率（月）
    # 中國（未來擴充）
    "CN_M2":          "MYAGM2CNM189N",    # 中國 M2 YoY（月）
    # 新加坡
    "SG_CPI":         "SGPCPIALLMINMEI",  # 新加坡 CPI（月）
}

# ── FinMind Dataset ─────────────────────────────────────────────────
FINMIND_DATASETS = {
    "TW_M2":          "TaiwanMoneySupplyM2",           # 台灣 M2
    "TW_M1B":         "TaiwanMoneySupplyM1b",          # 台灣 M1B
    "TW_INSTITUTIONAL": "TaiwanStockInstitutionalInvestorsBuySell",
    "TW_MARGIN":      "TaiwanStockMarginPurchaseShortSale",
    "TW_PMI":         "TaiwanManufacturingPMI",
    "TW_TRADE":       "TaiwanImportExport",
}

# ── Heatmap 指標映射 ────────────────────────────────────────────────
HEATMAP_CONFIG = {
    "liquidity": {
        "label": "Liquidity",
        "indicators": {
            "M2":     {"TW": "TW_M2", "US": "US_M2", "JP": "JP_M2",  "SG": None},
            "M1":     {"TW": "TW_M1B","US": None,     "JP": None,     "SG": None},
        }
    },
    "inflation": {
        "label": "Inflation",
        "indicators": {
            "CPI":      {"TW": "TW_CPI", "US": "US_CPI",      "JP": "JP_CPI", "SG": "SG_CPI"},
            "Core CPI": {"TW": None,     "US": "US_CORE_CPI", "JP": None,     "SG": None},
            "PPI":      {"TW": None,     "US": "US_PPI",      "JP": None,     "SG": None},
        }
    },
    "rates": {
        "label": "Rates",
        "indicators": {
            "Policy Rate": {"TW": None, "US": "US_FED_RATE", "JP": "JP_POLICY_RATE", "SG": None},
            "10Y Yield":   {"TW": None, "US": "US_10Y2Y",    "JP": None,             "SG": None},
        }
    },
}

# ── 國家 Dashboard 指標清單 ─────────────────────────────────────────
COUNTRY_INDICATORS = {
    "TW": {
        "growth":    ["TW_EXPORTS"],
        "inflation": ["TW_CPI"],
        "liquidity": ["TW_M2", "TW_M1B"],
        "labor":     ["TW_UNEMPLOYMENT"],
        "fx":        ["USD_TWD"],
        "markets":   ["TAIEX"],
    },
    "US": {
        "growth":    ["US_GDP", "US_NFP"],
        "inflation": ["US_CPI", "US_CORE_CPI", "US_PPI"],
        "liquidity": ["US_M2"],
        "rates":     ["US_FED_RATE", "US_10Y2Y"],
        "labor":     ["US_UNEMPLOYMENT"],
        "fx":        ["DXY"],
        "markets":   ["SP500", "NASDAQ"],
    },
    "JP": {
        "growth":    [],
        "inflation": ["JP_CPI"],
        "liquidity": ["JP_M2"],
        "rates":     ["JP_POLICY_RATE"],
        "labor":     ["JP_UNEMPLOYMENT"],
        "fx":        ["USD_JPY"],
        "markets":   ["N225"],
    },
    "SG": {
        "growth":    [],
        "inflation": ["SG_CPI"],
        "liquidity": [],
        "fx":        ["USD_SGD"],
        "markets":   ["STI"],
    },
}

# ── 信號閾值（用於 Heatmap 顏色判斷）──────────────────────────────
SIGNAL_THRESHOLDS = {
    # (series_key, direction): "up" = 數值上升為正面; "down" = 數值上升為負面
    "US_M2":       {"direction": "up",   "neutral_range": (-1, 3)},
    "TW_M2":       {"direction": "up",   "neutral_range": (3,  7)},
    "JP_M2":       {"direction": "up",   "neutral_range": (1,  5)},
    "US_CPI":      {"direction": "down", "neutral_range": (2,  3)},
    "TW_CPI":      {"direction": "down", "neutral_range": (1,  2.5)},
    "JP_CPI":      {"direction": "down", "neutral_range": (0,  2)},
    "SG_CPI":      {"direction": "down", "neutral_range": (1,  3)},
    "US_CORE_CPI": {"direction": "down", "neutral_range": (2,  3)},
}