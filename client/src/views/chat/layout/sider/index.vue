<script setup lang='ts'>
import type { CSSProperties, Component } from 'vue'
import { computed, defineAsyncComponent, h, ref, watch } from 'vue'
import { NButton, NDivider, NIcon, NLayoutSider, NMenu } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import {
  ArrowUpCircleOutline as ArrowUpIcon,
  PersonOutline as PersonIcon,
  SettingsOutline as SettingsIcon,
} from '@vicons/ionicons5'
import List from './List.vue'
import Footer from './Footer.vue'
import { useAppStore, useChatStore } from '@/store'
import { useBasicLayout } from '@/hooks/useBasicLayout'
const appStore = useAppStore()
const chatStore = useChatStore()

const { isMobile } = useBasicLayout()

const menu = ref(1)

const collapsed = computed(() => appStore.siderCollapsed)

function handleAdd() {
  menu.value = 1
  chatStore.addHistory({ title: 'New Chat', uuid: Date.now(), isEdit: false })
  if (isMobile.value)
    appStore.setSiderCollapsed(true)
}

function handleUpdateCollapsed() {
  appStore.setSiderCollapsed(!collapsed.value)
}

const getMobileClass = computed<CSSProperties>(() => {
  if (isMobile.value) {
    return {
      position: 'fixed',
      zIndex: 50,
    }
  }
  return {}
})

const mobileSafeArea = computed(() => {
  if (isMobile.value) {
    return {
      paddingBottom: 'env(safe-area-inset-bottom)',
    }
  }
  return {}
})

/* const songs = [
  {
    value: 1,
    label: '会话',
  },
  {
    value: 2,
    label: '模型',
  },
  {
    value: 3,
    label: '知识库',
  },
  {
    value: 4,
    label: '提示词',
  },
] */
//
watch(
  isMobile,
  (val) => {
    appStore.setSiderCollapsed(val)
  },
  {
    immediate: true,
    flush: 'post',
  },
)

function renderIcon(icon: Component) {
  return () => h(NIcon, null, { default: () => h(icon) })
}
const showset = ref<boolean>(false)
const showupfiles = ref<boolean>(false)
const handleUpdateValue = (key: string, item: MenuOption) => {
  if (key === 'set')
    showset.value = true
  if (key === 'up')
    showupfiles.value = true
}
const menuOptions: MenuOption[] = [
  {
    label: () =>
      h(
        'a',
        '上传数据',
      ),
    key: 'up',
    icon: renderIcon(ArrowUpIcon),
  },
  {
    label: () =>
      h(
        'a',
        '设置',
      ),
    key: 'set',
    icon: renderIcon(SettingsIcon),
  },
  {
    label: () =>
      h(
        'a',
        '且听风吟',
      ),
    key: 'hear-the-wind-sing',
    icon: renderIcon(PersonIcon),
  },
]
const Setting = defineAsyncComponent(() => import('@/components/common/Setting/index.vue'))
const Upfiles = defineAsyncComponent(() => import('@/components/common/UpFiles/index.vue'))
</script>

<template>
  <NLayoutSider
    :collapsed="collapsed"
    :collapsed-width="0"
    :width="260"
    :show-trigger="isMobile ? false : 'arrow-circle'"
    collapse-mode="transform"
    position="absolute"
    bordered
    :style="getMobileClass"
    @update-collapsed="handleUpdateCollapsed"
  >
    <div class="flex flex-col h-full " :style="mobileSafeArea">
      <main class="flex flex-col flex-1 min-h-0">
        <!-- 知识库界面 -->
        <!-- <div v-if="menu === 3">
          <div class="p-4">
            <Knowledge />
          </div>
        </div> -->
        <!-- 会话界面 -->
        <Footer />
        <NDivider />
        <div class="p-4">
          <NButton dashed block @click="handleAdd">
            +   添加新对话
          </NButton>
        </div>
        <div class="p-2 flex-1 min-h-0 pb-4 overflow-hidden">
          <List />
        </div>
        <NDivider />
        <NMenu :options="menuOptions" @update:value="handleUpdateValue" />
      </main>
      <Setting v-if="showset" v-model:visible="showset" />
      <Upfiles v-if="showupfiles" v-model:visible="showupfiles" />
    </div>
  </NLayoutSider>
  <template v-if="isMobile">
    <div v-show="!collapsed" class="fixed inset-0 z-40 w-full h-full bg-black/40" @click="handleUpdateCollapsed" />
  </template>
  <!-- <PromptStore v-model:visible="show" /> -->
</template>
