<script setup lang='ts'>
import { NButton, NDataTable, NModal, useMessage } from 'naive-ui'
import { h, ref, toRefs } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import { useChatStore } from '@/store'
const store = useChatStore()
const { showModal } = toRefs(store)
const message = useMessage()

interface Information {
  time: string
  privateCoffer: string
  fund: string
  steady: string
  security: string
  gold: string
}
const title = ref('财富保有数据明细')
const subtille = ref('2023年5月11日至18日财富保有金额，最高为5月15日230.65亿，最低为100.36亿，以下为2023年5月1日至18日数据明细(单位:亿万元)')
// const createColumns = ({
//   play,
// }: {
//   play: (row: Song) => void
// }): DataTableColumns<Song> => {
//   return [
//     {
//       title: 'No',
//       key: 'no',
//     },
//     {
//       title: 'Title',
//       key: 'title',
//     },
//     {
//       title: 'Length',
//       key: 'length',
//     },
//     {
//       title: 'Action',
//       key: 'actions',
//       render(row) {
//         return h(
//           NButton,
//           {
//             strong: true,
//             tertiary: true,
//             size: 'small',
//             onClick: () => play(row),
//           },
//           { default: () => 'Play' },
//         )
//       },
//     },
//   ]
// }
const createColumns = ({
  play,
}: {
  play: (row: Information) => void
}): DataTableColumns<Information> => {
  return [
    {
      title: '时间',
      key: 'time',
    },
    {
      title: '小金库保有',
      key: 'privateCoffer',
    },
    {
      title: '基金保有',
      key: 'fund',
    },
    {
      title: '稳健保有',
      key: 'steady',
    },
    {
      title: '证券保有',
      key: 'security',
    },
    {
      title: '黄金保有',
      key: 'gold',
    },
    {
      title: '操作',
      key: 'actions',
      render(row) {
        return h(
          NButton,
          {
            strong: true,
            tertiary: true,
            size: 'small',
            onClick: () => play(row),
          },
          { default: () => 'Play' },
        )
      },
    },
  ]
}
const data: Information[] = [
  {
    time: '2023.5.1',
    privateCoffer: '100.36',
    fund: '100.36',
    steady: '100.36',
    security: '100.36',
    gold: '100.36',
  },
  {
    time: '2023.5.1',
    privateCoffer: '100.36',
    fund: '100.36',
    steady: '100.36',
    security: '100.36',
    gold: '100.36',
  }, {
    time: '2023.5.1',
    privateCoffer: '100.36',
    fund: '100.36',
    steady: '100.36',
    security: '100.36',
    gold: '100.36',
  }, {
    time: '2023.5.1',
    privateCoffer: '100.36',
    fund: '100.36',
    steady: '100.36',
    security: '100.36',
    gold: '100.36',
  }, {
    time: '2023.5.1',
    privateCoffer: '100.36',
    fund: '100.36',
    steady: '100.36',
    security: '100.36',
    gold: '100.36',
  }, {
    time: '2023.5.1',
    privateCoffer: '100.36',
    fund: '100.36',
    steady: '100.36',
    security: '100.36',
    gold: '100.36',
  }, {
    time: '2023.5.1',
    privateCoffer: '100.36',
    fund: '100.36',
    steady: '100.36',
    security: '100.36',
    gold: '100.36',
  },

]
const columns = createColumns({
  play(row: Information) {
    message.info(`Play ${row.time}`)
  },
})
const pagination = false as const
</script>

<template>
  <NModal v-model:show="showModal">
    <div class=" bg-white p-4">
      <div class=" text-center text-lg mb-4">
        {{ title }}
      </div>
      <div class=" text-sm mb-4 text-center">
        {{ subtille }}
      </div>
      <NDataTable :columns="columns" :data="data" :pagination="pagination" :bordered="false" />
      <div class="flex justify-end space-x-4">
        <NButton size="small" type="info" class="mr-2" @click="showModal = false">
          下载
        </NButton>
        <NButton size="small" type="default" class="mr-2" @click="showModal = false">
          确定
        </NButton>
      </div>
    </div>
  </NModal>
</template>
