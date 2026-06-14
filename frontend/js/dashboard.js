/**
 * Macro Intelligence Platform v4.0 - Dashboard Logic
 */

async function initDashboard() {
    console.log("Initializing Dashboard...");
    await loadGlobalOverview();
}

/**
 * Switch between main views: overview, country, market, stocks
 */
function switchView(view) {
    console.log("Switching view to:", view);
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    const activeBtn = document.getElementById(`nav-${view}`);
    if (activeBtn) activeBtn.classList.add('active');
    
    document.getElementById('view-overview').classList.add('hidden');
    document.getElementById('view-country').classList.add('hidden');
    document.getElementById('view-market').classList.add('hidden');
    document.getElementById('view-stocks').classList.add('hidden');
    document.getElementById('view-stock-detail').classList.add('hidden');
    document.getElementById('left-sidebar').classList.add('hidden');
    
    const targetView = document.getElementById(`view-${view}`);
    if (targetView) targetView.classList.remove('hidden');
    
    if (view === 'country') {
        document.getElementById('left-sidebar').classList.remove('hidden');
        renderCountrySidebar();
    } else if (view === 'market') {
        document.getElementById('left-sidebar').classList.remove('hidden');
        renderMarketSidebar();
    } else if (view === 'stocks') {
        loadValuation('TW');
    } else if (view === 'overview') {
        loadGlobalOverview();
    }
}

/**
 * GLOBAL OVERVIEW: Risk Gauge, Heatmaps, Major Markets
 */
async function loadGlobalOverview() {
    console.log("Loading Global Overview...");
    try {
        const data = await fetchGlobalOverview();
        if(data) {
            if (typeof renderRiskGauge === 'function') {
                renderRiskGauge(data.risk_score);
            }
            
            const marketsGrid = document.getElementById('markets-grid');
            if (marketsGrid) {
                marketsGrid.innerHTML = (data.major_markets || []).map(m => `
                    <div class="p-3 border border-zinc-800 rounded bg-zinc-900/50">
                        <div class="text-xs text-zinc-500 font-bold mb-1">${m.country} ${m.name}</div>
                        <div class="text-lg font-black ${m.trend === 'up' ? 'text-green-500' : 'text-red-500'}">${m.current}</div>
                    </div>
                `).join('');
            }
        }

        const heatmaps = await fetchHeatmap();
        if(heatmaps && typeof renderHeatmapMatrix === 'function') {
            renderHeatmapMatrix('liquidity-heatmap', heatmaps.Liquidity);
            renderHeatmapMatrix('inflation-heatmap', heatmaps.Inflation);
        }
    } catch (e) {
        console.error("Error in loadGlobalOverview:", e);
    }
}

/**
 * COUNTRY DASHBOARD: Indicator Grids & Sparklines
 */
/**
 * 將專業單位轉換為直觀的中文化單位
 */
function formatMacroValue(val, unit, category) {
    if (val === null || val === undefined) return '--';
    
    let displayVal = val;
    let displayUnit = unit;

    // 單位換算邏輯
    if (unit === 'B$') {
        displayVal = (val / 1000).toFixed(2);
        displayUnit = ' 兆 USD';
    } else if (unit === 'M$') {
        displayVal = (val / 1000).toFixed(1);
        displayUnit = ' 億 USD';
    } else if (unit === 'K') {
        if (val > 100000) {
            displayVal = (val / 100000).toFixed(2);
            displayUnit = ' 億人';
        } else {
            displayVal = (val / 10).toFixed(0);
            displayUnit = ' 萬人';
        }
    } else if (unit === 'index') {
        // 指數類數據，通常 100 為基準
        displayUnit = ' 點';
    }

    return `${displayVal}${displayUnit}`;
}

/**
 * 根據指標特性決定漲跌顏色 (語意化顏色)
 */
function getTrendColor(change, category) {
    if (!change || change === 0) return 'text-zinc-500';
    
    // 正向指標 (越高越好): 成長、貿易、資產
    const positiveIsGood = ["Growth", "Trade", "Asset", "Liquidity"].includes(category);
    // 負向指標 (越低越好): 通膨、失業、利率(通常)
    const negativeIsGood = ["Inflation", "Labor", "Rates"].includes(category);

    if (positiveIsGood) {
        return change > 0 ? 'text-green-400' : 'text-red-400';
    }
    if (negativeIsGood) {
        return change > 0 ? 'text-red-400' : 'text-green-400';
    }
    
    // 預設 (金融市場風格: 紅漲綠跌)
    return change > 0 ? 'text-red-500' : 'text-green-500';
}

async function loadCountryData(country) {
    const countryNames = {"US": "美國", "TW": "台灣", "JP": "日本", "SG": "新加坡", "CN": "中國"};
    const titleEl = document.getElementById('country-title');
    if (titleEl) titleEl.innerText = `${countryNames[country] || country} 總體經濟儀表板`;
    
    document.querySelectorAll('#left-sidebar button').forEach(btn => btn.classList.remove('text-blue-500', 'bg-zinc-800'));
    const activeBtn = document.getElementById(`c-${country}`);
    if (activeBtn) activeBtn.classList.add('text-blue-500', 'bg-zinc-800');

    try {
        const response = await fetchCountryData(country);
        const indicatorsGrouped = response.indicators || [];
        
        const grid = document.getElementById('country-indicators');
        if (!grid) return;

        grid.innerHTML = indicatorsGrouped.map((ind, idx) => {
            const colorClass = getTrendColor(ind.change, ind.category);
            const categoryLabels = {
                "Growth": "經濟成長", "Inflation": "通膨物價", "Liquidity": "資金流動性", 
                "Rates": "利率水準", "Labor": "勞動力市場", "Trade": "國際貿易", 
                "FX": "匯率走勢", "Asset": "資產市場"
            };
            const catLabel = categoryLabels[ind.category] || ind.category;
            const formattedVal = formatMacroValue(ind.current, ind.unit, ind.category);

            return `
                <div class="panel p-4 flex flex-col gap-2">
                    <div class="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">${catLabel}</div>
                    <div class="flex justify-between items-end">
                        <span class="text-sm font-black text-white">${ind.name}</span>
                        <div class="flex flex-col items-end">
                            <span class="text-lg font-black mono text-white">${formattedVal}</span>
                            <span class="text-[10px] font-bold mono ${colorClass}">${ind.change > 0 ? '▲' : '▼'} ${Math.abs(ind.change ?? 0)}</span>
                        </div>
                    </div>
                    <div class="h-12 w-full mt-2" id="spark-${country}-${idx}"></div>
                </div>
            `;
        }).join('');

        // Render Sparklines after DOM update
        setTimeout(() => {
            indicatorsGrouped.forEach((ind, idx) => {
                if (ind.series && ind.series.length > 0 && typeof renderSparkline === 'function') {
                    renderSparkline(`spark-${country}-${idx}`, ind.series, ind.trend === 'up' ? '#00ff41' : '#ef4444');
                }
            });
        }, 100);
    } catch (e) {
        console.error("Error loading country data:", e);
    }
}

function renderCountrySidebar() {
    const sidebar = document.getElementById('sidebar-content');
    if (!sidebar) return;
    const countries = {"US": "美國", "TW": "台灣", "JP": "日本", "SG": "新加坡", "CN": "中國"};
    sidebar.innerHTML = Object.entries(countries).map(([id, name]) => `
        <button onclick="loadCountryData('${id}')" class="w-full text-left p-4 hover:bg-zinc-800 border-b border-zinc-800 font-bold" id="c-${id}">${name}</button>
    `).join('');
    loadCountryData('US');
}

/**
 * MARKET TERMINAL: Live Quotes & Charts
 */
async function renderMarketSidebar() {
    const sidebar = document.getElementById('sidebar-content');
    if (!sidebar) return;
    sidebar.innerHTML = '<div class="p-4 text-zinc-500 animate-pulse italic">Loading Markets...</div>';
    
    try {
        const data = await fetchMarkets();
        const categories = {
            "index": "主要指數", "fx": "匯率行情", "crypto": "加密貨幣", "rates": "利率債券", "commodity": "大宗商品"
        };

        let html = '';
        Object.entries(data).forEach(([cat, items]) => {
            html += `<div class="text-[10px] font-bold text-zinc-600 uppercase tracking-widest p-4 pb-1">${categories[cat] || cat}</div>`;
            Object.entries(items).forEach(([name, v]) => {
                html += `
                    <button onclick="selectMarket('${cat}', '${name}')" class="w-full text-left px-4 py-2 hover:bg-zinc-800 flex justify-between items-center text-xs" id="m-${name}">
                        <span class="font-bold">${name}</span>
                        <span class="mono ${v.change >= 0 ? 'text-green-500' : 'text-red-500'}">${v.current ?? '--'}</span>
                    </button>
                `;
            });
        });
        sidebar.innerHTML = html;
        
        // Auto-select first available asset
        const firstCat = Object.keys(data)[0];
        if (firstCat) {
            const firstName = Object.keys(data[firstCat])[0];
            if (firstName) selectMarket(firstCat, firstName);
        }
    } catch (e) {
        console.error("Error rendering market sidebar:", e);
    }
}

async function selectMarket(cat, name) {
    document.querySelectorAll('#sidebar-content button').forEach(b => b.classList.remove('bg-zinc-800', 'text-blue-500'));
    const btn = document.getElementById(`m-${name}`);
    if (btn) btn.classList.add('bg-zinc-800', 'text-blue-500');
    
    try {
        const data = await fetchMarkets();
        const asset = data[cat][name];
        document.getElementById('market-title').innerText = `${name} 行情趨勢`;
        document.getElementById('market-update-time').innerText = `SYNC: ${asset.updated_at || '--'}`;
        
        if (typeof renderMarketChart === 'function') {
            renderMarketChart('market-chart', name, asset.series || []);
        }
    } catch (e) {
        console.error("Error selecting market:", e);
    }
}

/**
 * STOCK ANALYSIS: Valuation Rankings & Details
 */
async function loadValuation(country) {
    const body = document.getElementById('valuation-table-body');
    if (!body) return;
    body.innerHTML = '<tr><td colspan="6" class="p-20 text-center animate-pulse italic text-zinc-600">正在計算估值矩陣...</td></tr>';
    
    try {
        const data = await fetchValuation(country);
        body.innerHTML = data.map(s => `
            <tr class="border-b border-zinc-900 hover:bg-zinc-900/50 transition-colors">
                <td class="p-4 mono text-zinc-400">${s.ticker}</td>
                <td class="p-4 font-bold text-white">${s.name}</td>
                <td class="p-4 mono">${s.pe ?? '--'}</td>
                <td class="p-4 mono">${s.pb ?? '--'}</td>
                <td class="p-4 mono text-green-500">${s.dy ?? '--'}%</td>
                <td class="p-4">
                    <button onclick="loadStockDetail('${country}', '${s.ticker}')" class="text-blue-500 text-xs font-bold underline">查看快照</button>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        body.innerHTML = '<tr><td colspan="6" class="p-10 text-center text-red-500">無法載入估值數據</td></tr>';
    }
}

async function loadStockDetail(country, ticker) {
    switchView('stock-detail');
    try {
        const data = await fetchStockDetail(country, ticker);
        
        document.getElementById('stock-detail-name').innerText = `${data.ticker} ${data.name}`;
        document.getElementById('stock-detail-info').innerHTML = `
            <div>價格: <span class="text-white mono">${data.quote?.price ?? '--'}</span></div>
            <div>漲跌: <span class="${(data.quote?.change || 0) >= 0 ? 'text-green-500' : 'text-red-500'} mono">${data.quote?.change ?? '--'} (${data.quote?.pct ?? '--'}%)</span></div>
            <div>本益比: <span class="text-white mono">${data.valuation?.pe ?? '--'}</span></div>
            <div>股淨比: <span class="text-white mono">${data.valuation?.pb ?? '--'}</span></div>
        `;

        if (typeof renderFinancialChart === 'function') {
            renderFinancialChart('stock-financial-chart', data.fundamentals || []);
        }

        // Financial Table
        const sorted = [...(data.fundamentals || [])].sort((a,b) => b.date.localeCompare(a.date));
        const head = document.getElementById('financial-table-head');
        head.innerHTML = `<tr><th class="p-2">項目 / 季度</th>` + sorted.map(f => `<th class="p-2">${f.date}</th>`).join('') + `</tr>`;
        
        const body = document.getElementById('financial-table-body');
        const rows = [
            { label: "營業收入", key: "revenue" },
            { label: "營業毛利", key: "gross_profit" },
            { label: "營業利益", key: "operating_income" },
            { label: "稅後淨利", key: "net_income" },
            { label: "每股盈餘 (EPS)", key: "eps" }
        ];

        body.innerHTML = rows.map(r => `
            <tr class="border-b border-zinc-900">
                <td class="p-2 font-bold text-zinc-500">${r.label}</td>
                ${sorted.map(f => `<td class="p-2 mono">${f[r.key]?.toLocaleString() ?? '--'}</td>`).join('')}
            </tr>
        `).join('');
    } catch (e) {
        console.error("Error loading stock detail:", e);
    }
}

// Global Startup
document.addEventListener('DOMContentLoaded', initDashboard);
