from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading
from services import macro_service, heatmap_service, risk_service, market_service

app = FastAPI(title="Macro Intelligence Platform v4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    threading.Thread(target=macro_service.sync_all_data, daemon=True).start()

@app.get("/api/global")
def get_global():
    return {
        "risk_score": risk_service.calculate_risk_score(),
        "major_markets": market_service.get_major_markets()
    }

@app.get("/api/macro/{country}")
def get_macro_country(country: str):
    return macro_service.get_country_dashboard(country.upper())

@app.get("/api/heatmap")
def get_heatmap():
    return heatmap_service.get_heatmap()

@app.get("/api/risk")
def get_risk():
    return {"risk_score": risk_service.calculate_risk_score()}

@app.get("/api/markets")
def get_markets():
    return market_service.get_all_markets()
