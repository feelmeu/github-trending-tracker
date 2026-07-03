(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();

  var chartSales = echarts.init(document.getElementById('chart-sales'), null, { renderer: 'svg' });
  chartSales.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      appendToBody: true,
      formatter: function(params) {
        var p = params[0];
        return p.name + '<br/>1-6月累计: ' + p.value + ' 万辆';
      }
    },
    grid: {
      left: '2%',
      right: '4%',
      bottom: '2%',
      top: '6%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: [
        '智己', '蔚来', '上汽', '启源', '埃安',
        '深蓝', '小米', '长城', '赛力斯', '五菱',
        '小鹏', '理想', '特斯拉', '零跑', '鸿蒙智行',
        '极氪', '奇瑞', '吉利', '比亚迪'
      ],
      axisLine: { lineStyle: { color: rule } },
      axisLabel: {
        color: ink,
        fontSize: 10,
        fontWeight: 600,
        rotate: 38,
        interval: 0
      },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted, fontSize: 11 },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } },
      max: 230
    },
    series: [{
      type: 'bar',
      data: [
        { value: 2.08, itemStyle: { color: accent2 } },
        { value: 11.42, itemStyle: { color: accent2 } },
        { value: 12.00, itemStyle: { color: accent2 } },
        { value: 12.00, itemStyle: { color: accent2 } },
        { value: 12.51, itemStyle: { color: accent } },
        { value: 14.32, itemStyle: { color: accent } },
        { value: 15.00, itemStyle: { color: accent } },
        { value: 17.10, itemStyle: { color: accent } },
        { value: 17.80, itemStyle: { color: accent } },
        { value: 19.10, itemStyle: { color: accent } },
        { value: 19.72, itemStyle: { color: accent } },
        { value: 20.39, itemStyle: { color: accent } },
        { value: 22.00, itemStyle: { color: accent } },
        { value: 22.17, itemStyle: { color: accent } },
        { value: 23.00, itemStyle: { color: accent } },
        { value: 24.49, itemStyle: { color: accent } },
        { value: 36.00, itemStyle: { color: accent } },
        { value: 45.00, itemStyle: { color: accent } },
        { value: 214.60, itemStyle: { color: accent } }
      ],
      barWidth: '55%',
      label: {
        show: true,
        position: 'top',
        color: ink,
        fontSize: 9,
        fontFamily: 'IBMPlexMono, monospace',
        formatter: '{c}',
        rotate: 38
      },
      itemStyle: { borderRadius: [4, 4, 0, 0] }
    }]
  });
  window.addEventListener('resize', function() { chartSales.resize(); });
})();
