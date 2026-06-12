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

function renderSparkline(domId, data, color) {
    const dom = document.getElementById(domId);
    if (!dom) return;
    const myChart = echarts.init(dom, 'dark');
    const option = {
        backgroundColor: 'transparent',
        grid: { left: 0, right: 0, top: 0, bottom: 0 },
        xAxis: { type: 'category', data: data.map(d => d.date), show: false },
        yAxis: { type: 'value', show: false, min: 'dataMin' },
        series: [{
            data: data.map(d => d.value),
            type: 'line',
            smooth: true,
            showSymbol: false,
            lineStyle: { width: 2, color: color },
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: color + '80' },
                    { offset: 1, color: 'transparent' }
                ])
            }
        }]
    };
    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
}