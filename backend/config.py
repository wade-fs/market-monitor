# config.py
import os
from pathlib import Path

DATA_DIR      = Path(os.getenv("DATA_DIR", "/data"))
CACHE_DIR     = DATA_DIR / "cache"
LOGS_DIR      = DATA_DIR / "logs"
SNAPSHOT_DIR  = DATA_DIR / "snapshots"

for d in [CACHE_DIR, LOGS_DIR, SNAPSHOT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

FRED_API_KEY  = os.getenv("FRED_API_KEY", "")
FINMIND_TOKEN = os.getenv("FINMIND_TOKEN", "")

SCHEDULE = {
    "market_minutes":     15,
    "macro_hours":         6,
    "fundamentals_hours": 24,
}

FRED_SERIES = {
    "US_M2":           ("M2SL",            "美國 M2",       "US","Liquidity","十億USD","monthly"),
    "US_CPI":          ("CPIAUCSL",        "美國 CPI",      "US","Inflation","index",  "monthly"),
    "US_CORE_CPI":     ("CPILFESL",        "Core CPI",      "US","Inflation","index",  "monthly"),
    "US_PPI":          ("PPIACO",          "美國 PPI",      "US","Inflation","index",  "monthly"),
    "US_FED_RATE":     ("FEDFUNDS",        "Fed 利率",      "US","Rates",    "%",      "monthly"),
    "US_10Y":          ("DGS10",           "美債 10Y",      "US","Rates",    "%",      "daily"),
    "US_2Y":           ("DGS2",            "美債 2Y",       "US","Rates",    "%",      "daily"),
    "US_10Y2Y":        ("T10Y2Y",          "10Y-2Y 利差",   "US","Rates",    "%",      "daily"),
    "US_GDP_YOY":      ("A191RL1Q225SBEA", "美國 GDP YoY",  "US","Growth",   "%",      "quarterly"),
    "US_UNEMPLOYMENT": ("UNRATE",          "美國失業率",     "US","Labor",    "%",      "monthly"),
    "US_NFP":          ("PAYEMS",          "非農就業",       "US","Labor",    "千人",   "monthly"),
    "US_RETAIL":       ("RSXFS",           "零售銷售",       "US","Growth",   "百萬USD","monthly"),
    "TW_CPI":          ("TWCPIALLMINMEI",  "台灣 CPI YoY",  "TW","Inflation","%",      "monthly"),
    "TW_UNEMPLOYMENT": ("LRUNTTTTTWM156N", "台灣失業率",     "TW","Labor",    "%",      "monthly"),
    "TW_EXPORTS":      ("XTEXVA01TWM667S", "台灣出口 YoY",  "TW","Trade",    "%",      "monthly"),
    "TW_FX_RESERVES":  ("TRESEGDTWM661N",  "外匯存底",      "TW","Asset",    "M$",     "monthly"),
    "TW_HOUSE_PRICE":  ("TWHPI",           "房價指數",      "TW","Asset",    "index",  "monthly"),
    "TW_TOURISM":      ("TW_TOUR_OUT",     "出國人次",      "TW","Growth",   "K",      "monthly"),
    "TW_POLICY_RATE":  ("INTDSRTWM193N",   "央行貼現率",     "TW","Rates",    "%",      "monthly"),
    "JP_CPI":          ("JPNCPIALLMINMEI", "日本 CPI YoY",  "JP","Inflation","%",      "monthly"),
    "JP_UNEMPLOYMENT": ("LRUNTTTTJPM156N", "日本失業率",     "JP","Labor",    "%",      "monthly"),
    "JP_M2":           ("MYAGM2JPM189N",   "日本 M2 YoY",   "JP","Liquidity","%",      "monthly"),
    "JP_POLICY_RATE":  ("IRSTCB01JPM156N", "日本政策利率",   "JP","Rates",    "%",      "monthly"),
    "JP_GDP_YOY":      ("JPNGDPRPCHTIQ",   "日本 GDP 成長",  "JP","Growth",   "%",      "quarterly"),
    "SG_CPI":          ("SGPCPIALLMINMEI", "新加坡 CPI YoY", "SG","Inflation","%",      "monthly"),
    "SG_GDP_YOY":      ("SGPGDPRQPSMEI",   "新加坡 GDP YoY", "SG","Growth",   "%",      "monthly"),
    "SG_UNEMPLOYMENT": ("LRUNTTTTSGM156N", "新加坡失業率",   "SG","Labor",    "%",      "monthly"),
    "CN_M2":           ("MYAGM2CNM189N",   "中國 M2 YoY",   "CN","Liquidity","%",      "monthly"),
    "CN_CPI":          ("CHNCPIALLMINMEI", "中國 CPI YoY",  "CN","Inflation","%",      "monthly"),
    "CN_GDP":          ("CHNGDPNQDSMEI",   "中國名目 GDP",  "CN","Growth",   "M$",     "quarterly"),
}

FINMIND_DATASETS = {
    "TW_M2":       "TaiwanMoneySupplyM2",
    "TW_M1B":      "TaiwanMoneySupplyM1b",
    "TW_PMI":      "TaiwanManufacturingPMI",
    "TW_INCOME":   "TaiwanStockFinancialStatements",
    "TW_BALANCE":  "TaiwanStockBalanceSheet",
    "TW_CASHFLOW": "TaiwanStockCashFlowsStatement",
    "TW_VALUATION":"TaiwanStockPER",
    "TW_DIVIDEND": "TaiwanStockDividend",
    "TW_EPS":      "TaiwanStockEPS",
    "TW_INST":     "TaiwanStockInstitutionalInvestorsBuySell",
}

MARKET_SYMBOLS = {
    "index":     {"TAIEX":"^TWII","SP500":"^GSPC","NASDAQ":"^IXIC","N225":"^N225"},
    "fx":        {"USD_TWD":"TWD=X","USD_JPY":"JPY=X","DXY":"DX-Y.NYB"},
    "rates":     {"US10Y":"^TNX","US30Y":"^TYX"},
    "crypto":    {"BTC":"BTC-USD","ETH":"ETH-USD"},
    "commodity": {"GOLD":"GC=F","OIL":"CL=F"},
}
