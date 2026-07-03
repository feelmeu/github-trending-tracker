(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();

  // --- Chart 1: Champions comparison (bar) ---
  var chart1 = echarts.init(document.getElementById('chart-champions'), null, { renderer: 'svg' });
  chart1.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      appendToBody: true,
      formatter: function(params) {
        var p = params[0];
        return p.name + '<br/>冠军片票房: ~' + p.value + ' 百万美元';
      }
    },
    grid: { left: '3%', right: '6%', bottom: '3%', top: '3%', containLabel: true },
    xAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted, fontSize: 11 },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } }
    },
    yAxis: {
      type: 'category',
      data: ['印度(全球)', '日本', '韩国(观影*千)', '法国', '美国', '中国'],
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: ink, fontSize: 11, fontWeight: 600 },
      axisTick: { show: false }
    },
    series: [{
      type: 'bar',
      data: [
        { value: 220, itemStyle: { color: accent } },
        { value: 90, itemStyle: { color: accent } },
        { value: 117, itemStyle: { color: accent2 } },
        { value: 50, itemStyle: { color: accent2 } },
        { value: 430, itemStyle: { color: accent } },
        { value: 611, itemStyle: { color: accent } }
      ],
      barWidth: '55%',
      label: {
        show: true,
        position: 'right',
        color: ink,
        fontSize: 10,
        fontFamily: 'IBMPlexMono, monospace',
        formatter: function(p) { return '~$' + p.value + 'M'; }
      },
      itemStyle: { borderRadius: [0, 4, 4, 0] }
    }]
  });
  window.addEventListener('resize', function() { chart1.resize(); });

  // --- Chart 2: Genre distribution of champions (pie) ---
  var chart2 = echarts.init(document.getElementById('chart-genres'), null, { renderer: 'svg' });
  chart2.setOption({
    animation: false,
    tooltip: { trigger: 'item', appendToBody: true, formatter: '{b}: {c} ({d}%)' },
    legend: {
      bottom: '2%',
      left: 'center',
      textStyle: { color: muted, fontSize: 11 },
      itemWidth: 12,
      itemHeight: 12
    },
    series: [{
      type: 'pie',
      radius: ['38%', '65%'],
      center: ['50%', '42%'],
      data: [
        { value: 2, name: '动作/惊悚', itemStyle: { color: accent } },
        { value: 1, name: '喜剧/运动', itemStyle: { color: accent2 } },
        { value: 1, name: '动画/悬疑', itemStyle: { color: accent + '99' } },
        { value: 1, name: '剧情/历史', itemStyle: { color: accent2 + '99' } },
        { value: 1, name: '动画/喜剧', itemStyle: { color: muted } }
      ],
      label: {
        color: ink,
        fontSize: 11,
        formatter: '{b}\n{d}%'
      },
      itemStyle: { borderColor: bg2, borderWidth: 2 }
    }]
  });
  window.addEventListener('resize', function() { chart2.resize(); });
})();
