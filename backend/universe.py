# universe.py — 股票清單
# 台灣：TWSE 50 成分股（FinMind ID）
# 美國：S&P 100 成分股（yfinance ticker）

TW_TWSE50 = [
    # FinMind stock_id（不含 .TW）
    "2330",  # 台積電
    "2317",  # 鴻海
    "2454",  # 聯發科
    "2382",  # 廣達
    "2308",  # 台達電
    "3711",  # 日月光投控
    "2303",  # 聯電
    "2412",  # 中華電
    "2882",  # 國泰金
    "1301",  # 台塑
    "1303",  # 南亞
    "1326",  # 台化
    "2886",  # 兆豐金
    "2891",  # 中信金
    "2884",  # 玉山金
    "2881",  # 富邦金
    "5880",  # 合庫金
    "2885",  # 元大金
    "2892",  # 第一金
    "2883",  # 開發金
    "2887",  # 台新金
    "2890",  # 永豐金
    "2207",  # 和泰車
    "2357",  # 華碩
    "2408",  # 南亞科
    "2379",  # 瑞昱
    "3034",  # 聯詠
    "2395",  # 研華
    "4938",  # 和碩
    "2327",  # 國巨
    "2347",  # 聯強
    "2801",  # 彰銀
    "1402",  # 遠東新
    "1216",  # 統一
    "2912",  # 統一超
    "9910",  # 豐泰
    "2615",  # 萬海
    "2609",  # 陽明
    "2603",  # 長榮
    "2301",  # 光寶科
    "3008",  # 大立光
    "2356",  # 英業達
    "3045",  # 台灣大
    "4904",  # 遠傳
    "2353",  # 宏碁
    "2352",  # 佳世達
    "2388",  # 威盛
    "6505",  # 台塑化
    "1101",  # 台泥
    "2002",  # 中鋼
]

# yfinance ticker（加 .TW 用於行情，不加用於 FinMind）
TW_YFINANCE = {sid: f"{sid}.TW" for sid in TW_TWSE50}

US_SP100 = [
    # Mega cap / Tech
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "ORCL",
    # Financials
    "BRK-B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "AXP", "BLK",
    # Healthcare
    "LLY", "UNH", "JNJ", "ABBV", "MRK", "TMO", "ABT", "DHR", "BMY", "AMGN",
    # Consumer
    "WMT", "HD", "COST", "MCD", "NKE", "SBUX", "TGT", "LOW", "TJX", "PG",
    # Industrials / Energy
    "XOM", "CVX", "COP", "RTX", "HON", "UPS", "CAT", "DE", "GE", "BA",
    # Telecom / Media
    "T", "VZ", "CMCSA", "DIS", "NFLX",
    # Semis
    "AMD", "QCOM", "TXN", "INTC", "MU", "AMAT", "LRCX", "KLAC",
    # Other
    "CRM", "ADBE", "NOW", "INTU", "UBER", "ABNB", "PYPL", "SQ",
    "KO", "PEP", "PM", "MO",
    "NEE", "DUK", "SO",
    "PLD", "AMT", "EQIX",
]

# 顯示用名稱（部分常見）
TW_NAMES = {
    "2330": "台積電", "2317": "鴻海", "2454": "聯發科", "2382": "廣達",
    "2308": "台達電", "3711": "日月光", "2303": "聯電", "2412": "中華電",
    "2882": "國泰金", "1301": "台塑", "1303": "南亞", "3008": "大立光",
    "2603": "長榮", "2609": "陽明", "2615": "萬海", "6505": "台塑化",
}

US_NAMES = {
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "NVIDIA", "AMZN": "Amazon",
    "GOOGL": "Alphabet", "META": "Meta", "TSLA": "Tesla", "AVGO": "Broadcom",
    "JPM": "JPMorgan", "V": "Visa", "MA": "Mastercard", "BAC": "BofA",
    "LLY": "Eli Lilly", "UNH": "UnitedHealth", "JNJ": "J&J", "XOM": "ExxonMobil",
    "WMT": "Walmart", "HD": "Home Depot", "KO": "Coca-Cola", "PEP": "PepsiCo",
}
