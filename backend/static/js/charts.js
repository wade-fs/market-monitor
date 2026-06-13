function renderRiskGauge(score) {
    const dom = document.getElementById('risk-gauge');
    const myChart = echarts.init(dom, 'dark');
    const option = {
        backgroundColor: 'transparent',
        series: [{
            type: 'gauge',
            startAngle: 180,
            endAngle: 0,
            min: 0,
            max: 100,
            splitNumber: 10,
            itemStyle: {
                color: '#3b82f6',
                shadowColor: 'rgba(0,138,255,0.45)',
                shadowBlur: 10,
                shadowOffsetX: 2,
                shadowOffsetY: 2
            },
            progress: { show: true, roundCap: true, width: 18 },
            pointer: { icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z', length: '12%', width: 20, offsetCenter: [0, '-60%'], itemStyle: { color: 'auto' } },
            axisLine: { roundCap: true, lineStyle: { width: 18 } },
            axisTick: { show: false },
            splitLine: { show: false },
            axisLabel: { show: false },
            title: { show: false },
            detail: { backgroundColor: 'transparent', width: '60%', lineHeight: 40, height: 40, borderRadius: 8, offsetCenter: [0, '35%'], valueAnimation: true, formatter: '{value}', color: 'inherit', fontSize: 40, fontWeight: 'bolder' },
            data: [{ value: score }]
        }]
    };
    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}

function renderFinancialChart(domId, data) {
    const dom = document.getElementById(domId);
    if (!dom) return;
    const myChart = echarts.init(dom, 'dark');
    
    // Sort by date ascending
    const sorted = [...data].sort((a,b) => a.date.localeCompare(b.date));
    
    const option = {
        backgroundColor: 'transparent',
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { data: ['營收', '毛利', '淨利'], textStyle: { color: '#aaa' }, bottom: 0 },
        grid: { top: 30, bottom: 50, left: 60, right: 20 },
        xAxis: { type: 'category', data: sorted.map(d => d.date) },
        yAxis: { type: 'value', splitLine: { lineStyle: { color: '#222' } } },
        series: [
            { name: '營收', type: 'bar', data: sorted.map(d => d.revenue), itemStyle: { color: '#3b82f6' } },
            { name: '毛利', type: 'bar', data: sorted.map(d => d.gross_profit), itemStyle: { color: '#10b981' } },
            { name: '淨利', type: 'bar', data: sorted.map(d => d.net_income), itemStyle: { color: '#f59e0b' } }
        ]
    };
    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}

function renderMarketChart(domId, name, series) {
    const dom = document.getElementById(domId);
    if (!dom) return;
    const myChart = echarts.init(dom, 'dark');
    const option = {
        backgroundColor: 'transparent',
        tooltip: { trigger: 'axis' },
        grid: { top: 20, bottom: 40, left: 60, right: 20 },
        xAxis: { type: 'category', data: series.map(d => d.t), axisLabel: { color: '#555' } },
        yAxis: { type: 'value', scale: true, splitLine: { lineStyle: { color: '#111' } } },
        series: [{
            name: name, type: 'line', data: series.map(d => d.v), smooth: true,
            lineStyle: { width: 3, color: '#3b82f6' },
            areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#3b82f640' }, { offset: 1, color: 'transparent' }]) }
        }]
    };
    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}