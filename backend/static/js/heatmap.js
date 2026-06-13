function renderHeatmapMatrix(domId, dataMap) {
    const dom = document.getElementById(domId);
    if (!dom) return;
    const myChart = echarts.init(dom, 'dark');

    const countries = Object.keys(dataMap);
    if (countries.length === 0) return;

    // Collect all unique indicators across all countries
    const indicatorSet = new Set();
    countries.forEach(c => Object.keys(dataMap[c]).forEach(i => indicatorSet.add(i)));
    const indicators = Array.from(indicatorSet);

    const data = [];
    countries.forEach((country, cIdx) => {
        indicators.forEach((indicator, iIdx) => {
            const val = dataMap[country][indicator];
            if (val !== undefined) {
                // val is 1 (green), 0 (yellow), -1 (red)
                data.push([cIdx, iIdx, val]);
            }
        });
    });

    const option = {
        backgroundColor: 'transparent',
        tooltip: {
            position: 'top',
            formatter: function (params) {
                const state = params.data[2] === 1 ? 'Positive' : (params.data[2] === -1 ? 'Negative' : 'Neutral');
                return `${countries[params.data[0]]} ${indicators[params.data[1]]}: ${state}`;
            }
        },
        grid: { top: 10, bottom: 30, left: 60, right: 10 },
        xAxis: { type: 'category', data: countries, splitArea: { show: true } },
        yAxis: { type: 'category', data: indicators, splitArea: { show: true } },
        visualMap: {
            min: -1, max: 1, show: false,
            inRange: { color: ['#ef4444', '#fbbf24', '#00ff41'] }
        },
        series: [{
            name: 'Heatmap', type: 'heatmap', data: data,
            label: { show: false },
            itemStyle: { borderWidth: 2, borderColor: '#09090b' }
        }]
    };
    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}