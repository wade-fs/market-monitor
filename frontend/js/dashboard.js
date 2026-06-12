async function initDashboard() {
    await loadGlobalOverview();
}

function switchView(view) {
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`nav-${view}`).classList.add('active');
    
    document.getElementById('view-overview').classList.add('hidden');
    document.getElementById('view-country').classList.add('hidden');
    document.getElementById('country-sidebar').classList.add('hidden');
    
    document.getElementById(`view-${view}`).classList.remove('hidden');
    
    if (view === 'country') {
        document.getElementById('country-sidebar').classList.remove('hidden');
        loadCountryData('US'); // default
    } else {
        loadGlobalOverview();
    }
}

async function loadGlobalOverview() {
    const data = await fetchGlobalOverview();
    if(data) {
        renderRiskGauge(data.risk_score);
        
        const marketsGrid = document.getElementById('markets-grid');
        marketsGrid.innerHTML = data.major_markets.map(m => `
            <div class="p-3 border border-zinc-800 rounded bg-zinc-900/50">
                <div class="text-xs text-zinc-500 font-bold mb-1">${m.country} ${m.name}</div>
                <div class="text-lg font-black ${m.trend === 'up' ? 'text-green-500' : 'text-red-500'}">${m.current}</div>
            </div>
        `).join('');
    }

    const heatmaps = await fetchHeatmap();
    if(heatmaps) {
        renderHeatmapMatrix('liquidity-heatmap', heatmaps.Liquidity);
        renderHeatmapMatrix('inflation-heatmap', heatmaps.Inflation);
    }
}

async function loadCountryData(country) {
    document.getElementById('country-title').innerText = `${country} Macro Dashboard`;
    document.querySelectorAll('#country-sidebar button').forEach(btn => btn.classList.remove('text-blue-500'));
    document.getElementById(`c-${country}`).classList.add('text-blue-500');

    const data = await fetchCountryData(country);
    const grid = document.getElementById('country-indicators');
    grid.innerHTML = data.map((ind, idx) => {
        const color = ind.trend === 'up' ? '#00ff41' : '#ef4444';
        const colorClass = ind.trend === 'up' ? 'text-green-500' : 'text-red-500';
        return `
            <div class="panel p-4 flex flex-col gap-2">
                <div class="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">${ind.category}</div>
                <div class="flex justify-between items-end">
                    <span class="text-sm font-black text-white">${ind.name}</span>
                    <div class="flex flex-col items-end">
                        <span class="text-lg font-black mono text-white">${ind.current}${ind.unit}</span>
                        <span class="text-[10px] font-bold mono ${colorClass}">${ind.change >= 0 ? '+' : ''}${ind.change}</span>
                    </div>
                </div>
                <div class="h-12 w-full mt-2" id="spark-${country}-${idx}"></div>
            </div>
        `;
    }).join('');

    setTimeout(() => {
        data.forEach((ind, idx) => {
            renderSparkline(`spark-${country}-${idx}`, ind.series, ind.trend === 'up' ? '#00ff41' : '#ef4444');
        });
    }, 50);
}

// Start
initDashboard();