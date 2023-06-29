<!-- chart.js bar chart -->

<script setup lang='ts'>
import { Utils } from 'chart.js'
import { defineProps } from 'vue'
const props = defineProps(['chartId'])
const DATA_COUNT = 7
const NUMBER_CFG = { count: DATA_COUNT, min: -100, max: 100 }

const labels = Utils.months({ count: 7 })
const data = {
  labels,
  datasets: [
    {
      label: 'Dataset 1',
      data: labels.map(() => {
        return [Utils.rand(-100, 100), Utils.rand(-100, 100)]
      }),
      backgroundColor: Utils.CHART_COLORS.red,
    },
    {
      label: 'Dataset 2',
      data: labels.map(() => {
        return [Utils.rand(-100, 100), Utils.rand(-100, 100)]
      }),
      backgroundColor: Utils.CHART_COLORS.blue,
    },
  ],
}
const config = {
  type: 'bar',
  data,
  options: {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Chart.js Floating Bar Chart',
      },
    },
  },
}
onMounted(() => {
  const ctx = document.getElementById(props.chartId)
  // eslint-disable-next-line no-new
  new Chart(ctx, config)
})
</script>

<template>
  <div class="chart-container" style="position: relative; height:40vh; width:80vw">
    <canvas :id="chartId" ref="chartRef" />
  </div>
</template>
