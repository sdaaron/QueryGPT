<script lang="ts" setup>
import { computed } from 'vue'
import { NAvatar } from 'naive-ui'
import { useUserStore } from '@/store'
import { isString } from '@/utils/is'
import defaultAvatar from '@/assets/avatar.png'

interface Props {
  image?: boolean
}
defineProps<Props>()

const userStore = useUserStore()

const avatar = computed(() => userStore.userInfo.avatar)
</script>

<template>
  <NAvatar v-if="image && isString(avatar) && avatar.length > 0" :src="avatar" :fallback-src="defaultAvatar" />
  <NAvatar v-else round :src="defaultAvatar" />
</template>
