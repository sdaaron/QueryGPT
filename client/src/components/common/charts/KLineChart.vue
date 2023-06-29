<script setup lang="ts">
import * as echarts from 'echarts'
import { nextTick, onMounted } from 'vue'
const props = defineProps(['chartDomId', 'type', 'x', 'data'])
onMounted(() => {
  nextTick(() => {
    const myChart = echarts.init(document.getElementById(props.chartDomId) as HTMLDivElement)
    window.addEventListener('resize', () => {
      myChart.resize()
    })
    const option = {
      title: {
        text: 'Accumulated Waterfall Chart',
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow',
        },
        formatter(params: any) {
          let tar
          if (params[1] && params[1].value !== '-')
            tar = params[1]
          else
            tar = params[2]

          return tar && `${tar.name}<br/>${tar.seriesName} : ${tar.value}`
        },
      },
      legend: {
        data: ['Expenses', 'Income'],
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: (function () {
          const list = []
          for (let i = 1; i <= 11; i++)
            list.push(`Nov ${i}`)

          return list
        })(),
      },
      yAxis: {
        type: 'value',
      },
      series: [
        {
          name: 'Placeholder',
          type: 'bar',
          stack: 'Total',
          silent: true,
          itemStyle: {
            borderColor: 'transparent',
            color: 'transparent',
          },
          emphasis: {
            itemStyle: {
              borderColor: 'transparent',
              color: 'transparent',
            },
          },
          data: [0, 900, 1245, 1530, 1376, 1376, 1511, 1689, 1856, 1495, 1292],
        },
        {
          name: 'Income',
          type: 'bar',
          stack: 'Total',
          label: {
            show: true,
            position: 'top',
          },
          data: [900, 345, 393, '-', '-', 135, 178, 286, '-', '-', '-'],
        },
        {
          name: 'Expenses',
          type: 'bar',
          stack: 'Total',
          label: {
            show: true,
            position: 'bottom',
          },
          data: ['-', '-', '-', 108, 154, '-', '-', '-', 119, 361, 203],
        },
      ],
    }

    myChart.setOption(option, true)
  })
})
</script>

<template>
  <!-- 重点项目完成率 开工率 -->
  <div :id="props.chartDomId" ref="box" :style="{ width: '100%', height: '100%' }" />
</template>

<style lang="scss" scoped></style>
