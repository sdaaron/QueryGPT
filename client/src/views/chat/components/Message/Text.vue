<script lang="ts" setup>
import { computed, onMounted, onUnmounted, onUpdated, ref, toRefs, watch } from 'vue'
import MarkdownIt from 'markdown-it'
import mdKatex from '@traptitech/markdown-it-katex'
import mila from 'markdown-it-link-attributes'
import hljs from 'highlight.js'

import { useBasicLayout } from '@/hooks/useBasicLayout'
import { t } from '@/locales'
import { copyToClip } from '@/utils/copy'
import { useChatStore } from '@/store'
import BarLine from '@/views/chat/components/echarts/barline.vue'
interface Props {
  inversion?: boolean
  error?: boolean
  dataecharts?: object
  text?: string
  xAxisData?: any[]
  seriesData?: any[]
  loading?: boolean
  asRawText?: boolean
  tableData?: any[]
  type?: string
}

const props = defineProps<Props>()

const { isMobile } = useBasicLayout()

const textRef = ref<HTMLElement>()
const store = useChatStore()
const { showModal } = toRefs(store)
const originalTableData = ref<any[]>([])
const total = ref(0)
const pageIndex = ref(1)
const mockText = ref('')
const setTimer = ref<any>(null)
const textIndex = ref(0)

const fullText = `加载数据库中...%
						启动取数Agent中...%
						正在理解您的问题...%
						生成取数代码中...%
						执行取数代码中...%
						正在生成图表...%
						`
const mdi = new MarkdownIt({
  html: false,
  linkify: true,
  highlight(code, language) {
    const validLang = !!(language && hljs.getLanguage(language))
    if (validLang) {
      const lang = language ?? ''
      return highlightBlock(hljs.highlight(code, { language: lang }).value, lang)
    }
    return highlightBlock(hljs.highlightAuto(code).value, '')
  },
})

mdi.use(mila, { attrs: { target: '_blank', rel: 'noopener' } })
mdi.use(mdKatex, { blockClass: 'katexmath-block rounded-md p-[10px]', errorColor: ' #cc0000' })

const wrapClass = computed(() => {
  return [
    'text-wrap',
    'min-w-[20px]',
    'rounded-md',
    isMobile.value ? 'p-2' : 'px-3 py-2',
    props.inversion ? 'bg-[#d2f9d1]' : 'bg-[#f4f6f8]',
    props.inversion ? 'dark:bg-[#a1dc95]' : 'dark:bg-[#1e1e20]',
    props.inversion ? 'message-request' : 'message-reply',
    { 'text-red-500': props.error },
  ]
})
const text = computed(() => {
  const value = props.text ?? ''
  if (!props.asRawText)
    return mdi.render(value)
  return value
})

function highlightBlock(str: string, lang?: string) {
  return `<pre class="code-block-wrapper"><div class="code-block-header"><span class="code-block-header__lang">${lang}</span><span class="code-block-header__copy">${t('chat.copyCode')}</span></div><code class="hljs code-block-body ${lang}">${str}</code></pre>`
}

function addCopyEvents() {
  if (textRef.value) {
    const copyBtn = textRef.value.querySelectorAll('.code-block-header__copy')
    copyBtn.forEach((btn) => {
      btn.addEventListener('click', () => {
        const code = btn.parentElement?.nextElementSibling?.textContent
        if (code) {
          copyToClip(code).then(() => {
            btn.textContent = '复制成功'
            setTimeout(() => {
              btn.textContent = '复制代码'
            }, 1000)
          })
        }
      })
    })
  }
}

function removeCopyEvents() {
  if (textRef.value) {
    const copyBtn = textRef.value.querySelectorAll('.code-block-header__copy')
    copyBtn.forEach((btn) => {
      btn.removeEventListener('click', () => {})
    })
  }
}
watch(() => props.tableData, (val) => {
  if (val) {
    originalTableData.value = val
    total.value = val.length
  }
})
watch(() => props.loading, (val) => {
  if (!val) {
    clearInterval(setTimer.value)
    console.log(111111111122222222222, props)
  }
})

onMounted(() => {
  if (props.loading) {
    setTimer.value = setInterval(() => {
      if (textIndex.value === fullText.length)
        textIndex.value = 0

      mockText.value = fullText.slice(0, textIndex.value)
      textIndex.value++
    }, 100)
  }
  originalTableData.value = props.tableData ?? []
  total.value = props.tableData?.length ?? 0
  addCopyEvents()
})

onUpdated(() => {
  addCopyEvents()
})

onUnmounted(() => {
  removeCopyEvents()
})
</script>

<template>
  <div class="text-black" :class="wrapClass">
    <div ref="textRef" class="leading-relaxed break-words">
      <div v-if="!inversion" @click="showModal = true">
        <div v-if="!asRawText" class="markdown-body" v-html="text" />
        <div v-else class="whitespace-pre-wrap" v-text="text" />
        <template v-if="Object.values(props.dataecharts ?? {})[0]?.length !== 0">
          <template v-if="props.type">
            <div v-if="props.type" style=" width: 800px;">
              <el-table :data="tableData?.slice((pageIndex - 1) * 10, (pageIndex) * 10)">
                <template v-for="(item, index) in Object.keys(dataecharts ?? {})" :key="index">
                  <el-table-column :label="item" :prop="item" />
                </template>
              </el-table>
              <el-pagination
                v-model:current-page="pageIndex"
                :page-size="10"
                layout="prev, pager, next"
                :total="total"
              />

              <div style=" height: 500px;" class=" mt-4">
                <BarLine :type="(props.type === 'none' ? 'line' : props.type).toLowerCase()" :x="xAxisData" :data="seriesData" />
              </div>
            </div>
          </template>
        </template>
      </div>
      <div v-else class="whitespace-pre-wrap" v-text="text" />
      <template v-if="loading">
        <!-- <span class="dark:text-white w-[4px] h-[20px] block animate-blink" /> -->
        <template v-for="item in mockText.split('%')">
          <div>
            {{ item }}
          </div>
        </template>
        <!-- <div style="height: auto;">
          <div>
            加载数据库中...
          </div>
          <div>
            启动取数Agent中...
          </div>
          <div>
            正在理解您的问题...
          </div>
          <div>
            生成取数代码中...
          </div>
          <div>
            执行取数代码中...
          </div>
          <div>输出数据中...</div>
        </div> -->
      </template>
    </div>
  </div>
</template>

<style lang="less">
@import url(./style.less);
</style>
