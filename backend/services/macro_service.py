from datetime import datetime
from data_sources.fetcher import fetch_yfinance_series, fetch_fred_series
from config import get_cache, set_cache

COUNTRIES = ["US", "TW", "JP", "SG"]
INDICATOR_REGISTRY = {
    "US": {
        "Growth": {"GDP YoY": "A191RL1Q225SBEA", "PMI": "MANPMI", "Retail Sales": "RETAILIRSA"},
        "Inflation": {"CPI": "CPIAUCSL", "Core CPI": "CPILFESL", "PPI": "PPIACO"},
        "Liquidity": {"M1": "WM1NS", "M2": "M2SL"},
        "Rates": {"Fed Rate": "FEDFUNDS", "10Y Yield": "^TNX", "2Y Yield": "^IRX"},
        "Labor": {"Unemployment": "UNRATE", "Payrolls": "PAYEMS"},
        "Trade": {"Exports": "EXPGS", "Imports": "IMPGS", "Trade Balance": "NETEXP"},
        "FX": {"DXY": "DX-Y.NYB"},
        "Asset": {"S&P 500": "^GSPC", "Nasdaq": "^IXIC"}
    },
    "TW": {
        "Growth": {"GDP Proxy": "^TWII", "Export Orders": "TWMORDERS"},
        "Inflation": {"CPI": "TWCPIALLMINMEI"},
        "Liquidity": {"M2": "MABMM201TWM189S", "M1B": "M1B_TW"},
        "Rates": {"10Y Yield": "TWM10Y=RR", "Policy Rate": "TWINTRATE"},
        "Labor": {"Unemployment": "TWMUNR"},
        "Trade": {"Exports": "TWNEXP", "Imports": "TWNIMP"},
        "FX": {"USD/TWD": "TWD=X"},
        "Asset": {"TAIEX": "^TWII", "Taiwan 50": "0050.TW"}
    },
    "JP": {
        "Growth": {"GDP YoY": "JPNGDPYOY", "PMI": "JPNMANPMI"},
        "Inflation": {"CPI": "JPNCPIALLMINMEI", "Core CPI": "JPNCPICORMINMEI"},
        "Liquidity": {"M2": "MABMM201JPNM189S"},
        "Rates": {"BOJ Rate": "JPNINTRATEM", "JGB 10Y": "JPN10Y=RR"},
        "Trade": {"Exports": "JPNEXP", "Imports": "JPNIMP"},
        "FX": {"USD/JPY": "JPY=X"},
        "Asset": {"Nikkei 225": "^N225", "TOPIX": "^TPX"}
    },
    "SG": {
        "Growth": {"GDP YoY": "SGPGDPYOY"},
        "Inflation": {"CPI": "SGPCPIALLMINMEI"},
        "Liquidity": {"M2": "MABMM201SGP189S"},
        "FX": {"USD/SGD": "SGD=X"},
        "Asset": {"STI": "^STI"}
    }
}

def sync_all_data():
    for country, categories in INDICATOR_REGISTRY.items():
        dashboard = []
        for cat, indicators in categories.items():
            for name, sym in indicators.items():
                is_yf = sym.startswith('^') or sym.endswith('=X') or 'DX-Y' in sym or '.TW' in sym
                series = fetch_yfinance_series(sym, is_vix='^VIX' in sym) if is_yf else fetch_fred_series(sym)
                if series:
                    cur = series[-1]["value"]
                    prev = series[-2]["value"] if len(series) > 1 else cur
                    dashboard.append({
                        "id": f"{country}_{name}".lower().replace(' ', '_'),
                        "country": country,
                        "category": cat,
                        "name": name,
                        "unit": "%" if not is_yf else "pts",
                        "current": cur,
                        "previous": prev,
                        "change": round(cur - prev, 2),
                        "trend": "up" if cur > prev else "down",
                        "updated_at": datetime.now().isoformat(),
                        "series": series
                    })
        set_cache(f"macro_{country}", dashboard)

def get_country_dashboard(country):
    data = get_cache(f"macro_{country}")
    if data: return data
    return []