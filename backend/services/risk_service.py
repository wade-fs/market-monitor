from config import get_cache
from services.macro_service import COUNTRIES

def calculate_risk_score():
    total_assets = 0
    up_assets = 0
    for country in COUNTRIES:
        data = get_cache(f"macro_{country}")
        if not data: continue
        for item in data:
            if item["category"] == "Asset":
                total_assets += 1
                if item["trend"] == "up": up_assets += 1
    if total_assets == 0: return 50
    return round(up_assets / total_assets * 100)