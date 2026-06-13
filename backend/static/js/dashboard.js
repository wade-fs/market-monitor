async function initDashboard() {
    await loadGlobalOverview();
}

function switchView(view) {
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`nav-${view}`)?.classList.add('active');
    
    document.getElementById('view-overview').classList.add('hidden');
    document.getElementById('view-country').classList.add('hidden');
    document.getElementById('view-market').classList.add('hidden');
    document.getElementById('view-stocks').classList.add('hidden');
    document.getElementById('view-stock-detail').classList.add('hidden');
    document.getElementById('left-sidebar').classList.add('hidden');
    
    document.getElementById(`view-${view}`).classList.remove('hidden');
    
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

function renderCountrySidebar() {
    const sidebar = document.getElementById('sidebar-content');
    const countries = {"US": "美國", "TW": "台灣", "JP": "日本", "SG": "新加坡"};
    sidebar.innerHTML = Object.entries(countries).map(([id, name]) => `
        <button onclick="loadCountryData('${id}')" class="w-full text-left p-4 hover:bg-zinc-800 border-b border-zinc-800 font-bold" id="c-${id}">${name}</button>
    `).join('');
    loadCountryData('US');
}

async function renderMarketSidebar() {
    const sidebar = document.getElementById('sidebar-content');
    sidebar.innerHTML = '<div class="p-4 text-zinc-500 animate-pulse italic">Loading Markets...</div>';
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
    // Select first one
    const firstCat = Object.keys(data)[0];
    const firstName = Object.keys(data[firstCat])[0];
    selectMarket(firstCat, firstName);
}

async function selectMarket(cat, name) {
    document.querySelectorAll('#sidebar-content button').forEach(b => b.classList.remove('bg-zinc-800', 'text-blue-500'));
    document.getElementById(`m-${name}`).classList.add('bg-zinc-800', 'text-blue-500');
    
    const data = await fetchMarkets();
    const asset = data[cat][name];
    document.getElementById('market-title').innerText = `${name} 行情趨勢`;
    document.getElementById('market-update-time').innerText = `SYNC: ${asset.updated_at}`;
    
    renderMarketChart('market-chart', name, asset.series);
}

async function loadValuation(country) {
    const body = document.getElementById('valuation-table-body');
    body.innerHTML = '<tr><td colspan="6" class="p-20 text-center animate-pulse italic text-zinc-600">正在計算估值矩陣...</td></tr>';
    const data = await fetchValuation(country);
    
    body.innerHTML = data.map(s => `
        <tr class="border-b border-zinc-900 hover:bg-zinc-900/50 transition-colors">
            <td class="p-4 mono text-zinc-400">${s.ticker}</td>
            <td class="p-4 font-bold text-white">${s.name}</td>
            <td class="p-4 mono">${s.pe}</td>
            <td class="p-4 mono">${s.pb}</td>
            <td class="p-4 mono text-green-500">${s.dy ?? '--'}%</td>
            <td class="p-4">
                <button onclick="loadStockDetail('${country}', '${s.ticker}')" class="text-blue-500 text-xs font-bold underline">查看快照</button>
            </td>
        </tr>
    `).join('');
}

async function loadStockDetail(country, ticker) {
    switchView('stock-detail');
    const data = await fetchStockDetail(country, ticker);
    
    document.getElementById('stock-detail-name').innerText = `${data.ticker} ${data.name}`;
    document.getElementById('stock-detail-info').innerHTML = `
        <div>價格: <span class="text-white mono">${data.quote.price}</span></div>
        <div>漲跌: <span class="${data.quote.change >= 0 ? 'text-green-500' : 'text-red-500'} mono">${data.quote.change} (${data.quote.pct}%)</span></div>
        <div>本益比: <span class="text-white mono">${data.valuation?.pe ?? '--'}</span></div>
        <div>股淨比: <span class="text-white mono">${data.valuation?.pb ?? '--'}</span></div>
    `;

    // Financial Chart
    renderFinancialChart('stock-financial-chart', data.fundamentals);

    // Financial Table
    const sorted = [...data.fundamentals].sort((a,b) => b.date.localeCompare(a.date));
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
}

async function loadCountryData(country) {
    const countryNames = {"US": "美國", "TW": "台灣", "JP": "日本", "SG": "新加坡"};
    document.getElementById('country-title').innerText = `${countryNames[country] || country} 總體經濟儀表板`;
    document.querySelectorAll('#country-sidebar button').forEach(btn => btn.classList.remove('text-blue-500'));
    document.getElementById(`c-${country}`).classList.add('text-blue-500');

    const response = await fetchCountryData(country);
    const indicatorsGrouped = response.indicators;
    
    // Flatten indicators for rendering while keeping category info
    const allIndicators = [];
    Object.entries(indicatorsGrouped).forEach(([cat, list]) => {
        list.forEach(ind => {
            allIndicators.push({...ind, category: cat});
        });
    });

    const grid = document.getElementById('country-indicators');
    grid.innerHTML = allIndicators.map((ind, idx) => {
        const colorClass = ind.trend === 'up' ? 'text-green-500' : (ind.trend === 'down' ? 'text-red-500' : 'text-zinc-500');
        
        const categoryLabels = {
            "Growth": "經濟成長", "Inflation": "通膨物價", "Liquidity": "資金流動性", 
            "Rates": "利率水準", "Labor": "勞動力市場", "Trade": "國際貿易", 
            "FX": "匯率走勢", "Asset": "資產市場", "Market": "市場行情"
        };
        const catLabel = categoryLabels[ind.category] || ind.category;

        return `
            <div class="panel p-4 flex flex-col gap-2">
                <div class="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">${catLabel}</div>
                <div class="flex justify-between items-end">
                    <span class="text-sm font-black text-white">${ind.name}</span>
                    <div class="flex flex-col items-end">
                        <span class="text-lg font-black mono text-white">${ind.current ?? '--'}${ind.unit}</span>
                        <span class="text-[10px] font-bold mono ${colorClass}">${ind.change >= 0 ? '+' : ''}${ind.change ?? ''}</span>
                    </div>
                </div>
                <div class="h-12 w-full mt-2" id="spark-${country}-${idx}"></div>
            </div>
        `;
    }).join('');

    setTimeout(() => {
        allIndicators.forEach((ind, idx) => {
            if (ind.series && ind.series.length > 0) {
                renderSparkline(`spark-${country}-${idx}`, ind.series, ind.trend === 'up' ? '#00ff41' : '#ef4444');
            }
        });
    }, 50);
}

// Start
initDashboard();