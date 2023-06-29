<script setup lang='ts'>
import { computed, ref } from 'vue'
import { NButton, NDivider, NModal } from 'naive-ui'

interface Props {
  visible: boolean
}

interface Emit {
  (e: 'update:visible', visible: boolean): void
}

const props = defineProps<Props>()

const emit = defineEmits<Emit>()

const active = ref('General')

const show = computed({
  get() {
    return props.visible
  },
  set(visible: boolean) {
    emit('update:visible', visible)
  },
})
</script>

<template>
  <NModal v-model:show="show" title="上传文件" :auto-focus="false" preset="card" style="width: 95%; max-width: 640px">
    <div>
      <NDivider />
      <NButton text style="font-size: 24px">
        <img src="@/assets/excel.png">
      </NButton>
    </div>
  </NModal>
</template>
