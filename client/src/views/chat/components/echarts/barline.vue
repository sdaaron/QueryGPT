<script lang="ts" setup>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
} from 'echarts/components'
import VChart, { THEME_KEY } from 'vue-echarts'
import { onMounted, provide, ref } from 'vue'
const props = defineProps(['project', 'x', 'data', 'type'])
onMounted(async () => {})
use([
  CanvasRenderer,
  PieChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  BarChart,
])

provide(THEME_KEY, 'dark')

const option = ref({
  // backgroundColor: 'rgb(244,246,248)',
  backgroundColor: 'rgb(255,255,255)',
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow',
    },
  },
  legend: {
    top: 0,

  },
  // textStyle: {
  //   color: 'white',
  // },
  // tooltip: {
  //     trigger: 'axis',
  //     axisPointer: {
  //         type: 'shadow'
  //     }
  // },
  grid: {
    // top: '3%',
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true,
  },
  xAxis: {
    type: 'category',
    data: props.x,

    // axisLine: {
    //   show: true,
    //   lineStyle: {
    //     color: 'rgba(0,0,255,0.3)',
    //   },
    // },
    axisLabel: {
      color: 'rgb(0,0,0)',
      // rotate: 45,
    },
    // // interval:20,
    // splitLine: {
    //   lineStyle: {
    //     color: 'rgba(0,0,255,0.3)',
    //   },
    // },
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      color: 'rgb(0,0,0)',
    },
    splitLine: {
      show: true,
      lineStyle: {

        color: 'rgba(0,0,0,0.1)',
      },
    },
    // axisTick: {
    //   show: false,
    // },
    // axisLine: {
    //   show: false,
    // },
  },

  // series: [
  //   {
  //     type: props.type,
  //     data: props.data,
  //     // barWidth: '20',
  //     itemStyle: {
  //       // borderRadius: 20,
  //       color: 'rgba(28, 142, 255, 1)',
  //     },
  //   },
  // ],
  series: props.data,
})
</script>

<template>
  <VChart class="chart" :option="option" autoresize />
  <!-- Bar组件封装 -->
</template>

  <style scoped>
  .chart {
    height: 100%;
  }
  </style>
