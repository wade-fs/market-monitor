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