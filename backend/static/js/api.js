const API_BASE = '/api';

async function fetchGlobalOverview() {
    const res = await fetch(`${API_BASE}/global`);
    return await res.json();
}

async function fetchCountryData(country) {
    const res = await fetch(`${API_BASE}/macro/${country}`);
    return await res.json();
}

async function fetchHeatmap() {
    const res = await fetch(`${API_BASE}/heatmap`);
    return await res.json();
}

async function fetchValuation(country) {
    const res = await fetch(`${API_BASE}/stocks/${country}/valuation`);
    return await res.json();
}

async function fetchStockDetail(country, ticker) {
    const res = await fetch(`${API_BASE}/stocks/${country}/${ticker}`);
    return await res.json();
}

async function fetchMarkets() {
    const res = await fetch(`${API_BASE}/markets`);
    return await res.json();
}