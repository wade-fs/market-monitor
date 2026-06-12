from services.cache_service import get_cache
from services.macro_service import COUNTRIES

def get_heatmap():
    heatmap = {"Liquidity": {}, "Inflation": {}}
    for country in COUNTRIES:
        heatmap["Liquidity"][country] = {}
        heatmap["Inflation"][country] = {}
        data = get_cache(f"macro_{country}")
        if not data: continue
        
        for item in data:
            if item["category"] == "Liquidity":
                val = 1 if item["trend"] == "up" else -1
                heatmap["Liquidity"][country][item["name"]] = val
            elif item["category"] == "Inflation":
                val = -1 if item["trend"] == "up" else 1
                heatmap["Inflation"][country][item["name"]] = val
    return heatmap