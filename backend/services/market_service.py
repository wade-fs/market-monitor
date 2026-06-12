from services.cache_service import get_cache
from services.macro_service import COUNTRIES

def get_major_markets():
    markets = []
    for country in COUNTRIES:
        data = get_cache(f"macro_{country}")
        if not data: continue
        for item in data:
            if item["category"] == "Asset":
                markets.append(item)
    return markets

def get_all_markets():
    return get_major_markets()