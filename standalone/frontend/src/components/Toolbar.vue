<template>
  <div class="toolbar">
    <div class="toolbar-left">
      <a class="btn btn-ghost" href="/api/template" download>양식다운로드</a>
      <label class="btn btn-primary">
        <input type="file" accept=".xls,.xlsx" @change="onFileChange" style="display:none" />
        엑셀업로드
      </label>
      <label class="btn btn-primary btn-import">
        <input type="file" accept=".json" @change="onProjectImport" style="display:none" />
        JSON불러오기
      </label>
    </div>

    <div class="toolbar-center">
      <span v-if="filename" class="filename">{{ filename }}</span>
      <span v-if="tableCount" class="count">{{ tableCount }}개 테이블</span>
    </div>

    <div class="toolbar-right">
      <!-- 컬럼 표시 -->
      <span class="label">컬럼:</span>
      <button class="btn toggle-btn" :class="{ active: showType }" @click="$emit('update:showType', !showType)">타입</button>
      <button class="btn toggle-btn" :class="{ active: showDesc }" @click="$emit('update:showDesc', !showDesc)">설명</button>

      <div class="divider" />

      <!-- ERD 표기법 -->
      <span class="label">표기법:</span>
      <button
        v-for="n in notations"
        :key="n"
        class="btn"
        :class="{ active: notation === n }"
        @click="$emit('update:notation', n)"
      >{{ n }}</button>

      <div class="divider" />

      <!-- 설정 드롭다운 -->
      <div class="settings-wrap" ref="settingsRef">
        <button class="btn btn-settings" ref="settingsBtnRef" @click.stop="toggleMenu">
          설정 <span class="caret">▾</span>
        </button>
      </div>
      <Teleport to="body">
        <div v-if="showMenu" class="settings-menu" :style="menuStyle">
          <button class="menu-item" @click="open('relations')">관계 관리</button>
          <button class="menu-item" @click="open('colors')">색상 지정</button>
        </div>
      </Teleport>

      <div class="divider" />

      <!-- 내보내기 -->
      <span class="label">내보내기:</span>
      <button class="btn btn-ghost" @click="$emit('export', 'json')">JSON</button>
      <button class="btn btn-ghost" @click="$emit('export', 'svg')">SVG</button>
      <button class="btn btn-ghost" @click="$emit('export', 'png')">PNG</button>
      <button class="btn btn-ghost" @click="$emit('export', 'excel')">Excel</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import type { Notation } from '@/types'

defineProps<{
  showType: boolean
  showDesc: boolean
  notation: Notation
  filename?: string
  tableCount?: number
}>()

const emit = defineEmits<{
  'update:showType':  [boolean]
  'update:showDesc':  [boolean]
  'update:notation':  [Notation]
  'file-upload':      [File]
  'import-project':   [File]
  'export':           ['svg' | 'png' | 'excel' | 'json']
  'open-settings':    ['relations' | 'colors']
}>()

const notations: Notation[] = ['IE', 'Barker']
const showMenu       = ref(false)
const settingsRef    = ref<HTMLElement>()
const settingsBtnRef = ref<HTMLElement>()
const menuStyle = ref<Record<string, string>>({})

function toggleMenu() {
  if (!showMenu.value && settingsBtnRef.value) {
    const rect = settingsBtnRef.value.getBoundingClientRect()
    menuStyle.value = {
      position: 'fixed',
      top:      `${rect.bottom + 6}px`,
      right:    `${window.innerWidth - rect.right}px`,
      zIndex:   '9999',
    }
  }
  showMenu.value = !showMenu.value
}

function open(panel: 'relations' | 'colors') {
  showMenu.value = false
  emit('open-settings', panel)
}

function onDocClick(e: MouseEvent) {
  if (settingsRef.value && !settingsRef.value.contains(e.target as Node)) {
    showMenu.value = false
  }
}

onMounted(() => document.addEventListener('click', onDocClick))
onUnmounted(() => document.removeEventListener('click', onDocClick))

function onFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) emit('file-upload', file)
  ;(e.target as HTMLInputElement).value = ''
}

function onProjectImport(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) emit('import-project', file)
  ;(e.target as HTMLInputElement).value = ''
}
</script>

<style scoped>
.toolbar {
  height: 48px;
  background: var(--erd-toolbar-bg, #161b27);
  border-bottom: 1px solid #2d3a52;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
  flex-shrink: 0;
  overflow-x: auto;
}
.toolbar-left, .toolbar-right { display: flex; align-items: center; gap: 6px; }
.toolbar-center { flex: 1; display: flex; align-items: center; gap: 10px; min-width: 0; }
.filename { color: #93c5fd; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.count    { color: #64748b; font-size: 11px; white-space: nowrap; }
.label    { color: #64748b; font-size: 11px; white-space: nowrap; }
.divider  { width: 1px; height: 24px; background: #2d3a52; flex-shrink: 0; }

.btn { background: #2d3a52; color: #cbd5e1; padding: 4px 10px; font-size: 11px; white-space: nowrap; border: none; border-radius: 4px; cursor: pointer; }
.btn:hover { background: #374760; }
.btn.active { background: #1d4ed8; color: #fff; }
.btn-primary { background: #1d4ed8; color: #fff; padding: 5px 12px; font-size: 12px; display: inline-flex; align-items: center; cursor: pointer; }
.btn-primary:hover { background: #2563eb; }
.btn-import { background: #0f766e; border-color: #0f766e; }
.btn-import:hover { background: #115e59; }
.btn-ghost { background: transparent; color: #64748b; border: 1px solid #2d3a52; }
.btn-ghost:hover { color: #cbd5e1; border-color: #374760; }
.toggle-btn { border: 1px solid #3b4a6b; }
.toggle-btn.active { border-color: #3b82f6; }

/* 설정 드롭다운 */
.settings-wrap { position: relative; }
.btn-settings { background: #164e63; color: #67e8f9; border: 1px solid #155e75; }
.btn-settings:hover { background: #155e75; }
.caret { font-size: 9px; margin-left: 2px; }
</style>

<!-- Teleport된 요소는 scoped 적용 안 됨 → 전역 스타일 -->
<style>
.settings-menu {
  background: #1a2132;
  border: 1px solid #2d3a52;
  border-radius: 6px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.5);
  min-width: 130px;
  overflow: hidden;
}
.settings-menu .menu-item {
  display: block; width: 100%; text-align: left;
  background: none; border: none; color: #cbd5e1;
  font-size: 12px; padding: 9px 14px; cursor: pointer;
}
.settings-menu .menu-item:hover { background: #2d3a52; }
</style>
