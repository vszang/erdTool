<template>
  <Toolbar
    v-model:showType="showType"
    v-model:showDesc="showDesc"
    v-model:notation="notation"
    :filename="filename"
    :table-count="Object.keys(tables).length || undefined"
    @file-upload="uploadFile"
    @import-project="importProject"
    @export="handleExport"
    @open-settings="handleOpenSettings"
  />

  <div
    class="flow-wrap"
    ref="flowWrapRef"
    @dragover.prevent="onDragOver"
    @dragleave="onDragLeave"
    @drop.prevent="onDrop"
    :class="{ 'drag-over': isDragOver }"
  >
    <VueFlow
      v-if="nodes.length"
      v-model:nodes="nodes"
      v-model:edges="edges"
      :node-types="nodeTypes"
      :edge-types="edgeTypes"
      fit-view-on-init
      class="vue-flow"
    >
      <Background v-if="colors.showGrid" :pattern-color="colors.canvasGrid" :gap="24" />
      <Controls />
      <MiniMap node-color="#2d3a52" mask-color="rgba(0,0,0,0.6)" />
    </VueFlow>

    <div v-else class="empty-state">
      <div class="empty-icon">⬆</div>
      <p>XLS / XLSX / JSON 프로젝트 파일을 업로드하거나 여기에 드래그하세요.</p>
    </div>

    <div v-if="isDragOver" class="drag-overlay">
      <div class="drag-hint">파일을 놓으세요</div>
    </div>

    <div v-if="loading"  class="loading-overlay">파싱 중...</div>
    <div v-if="errorMsg" class="error-toast" @click="errorMsg = ''">{{ errorMsg }}</div>
  </div>

  <RelationManager
    v-if="showRelationManager"
    :tables="tables"
    :custom-relations="customRelations"
    :deleted-rel-ids="deletedRelIds"
    @close="showRelationManager = false"
    @add-relation="onAddRelation"
    @delete-relation="onDeleteRelation"
  />

  <ColorSettings
    v-if="showColorSettings"
    @close="showColorSettings = false"
  />
</template>

<script setup lang="ts">
import { ref, watch, markRaw, nextTick, onMounted, onUnmounted } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import type { Node, Edge } from '@vue-flow/core'
import { toPng, toSvg } from 'html-to-image'

import Toolbar       from '@/components/Toolbar.vue'
import TableNode     from '@/components/TableNode.vue'
import ErdEdge       from '@/components/ErdEdge.vue'
import RelationManager from '@/components/RelationManager.vue'
import ColorSettings   from '@/components/ColorSettings.vue'
import { colors }      from '@/store/colors'
import type { Tables, Notation, CustomRelation } from '@/types'

import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

const nodeTypes = { tableNode: markRaw(TableNode) }
const edgeTypes = { erdEdge:   markRaw(ErdEdge) }

const tables    = ref<Tables>({})
const nodes     = ref<Node[]>([])
const edges     = ref<Edge[]>([])
const showType  = ref(false)
const showDesc  = ref(false)
const notation  = ref<Notation>('IE')
const filename  = ref('')
const loading   = ref(false)
const errorMsg  = ref('')
const isDragOver = ref(false)
const showRelationManager = ref(false)
const showColorSettings   = ref(false)
const customRelations = ref<CustomRelation[]>([])
const deletedRelIds   = ref<Set<string>>(new Set())
const flowWrapRef     = ref<HTMLElement>()

// ── 하트비트 (브라우저 종료 감지) ──────────────────────────────────────────

let heartbeatTimer: any = null

function sendHeartbeat() {
  fetch('/api/heartbeat', { method: 'POST' }).catch(() => {
    // 서버가 꺼졌거나 네트워크 오류 시 무시 (어차피 서버가 종료됨)
  })
}

onMounted(() => {
  // 앱 기동 시 즉시 한 번 보내고 5초마다 반복
  sendHeartbeat()
  heartbeatTimer = setInterval(sendHeartbeat, 5000)
})

onUnmounted(() => {
  if (heartbeatTimer) clearInterval(heartbeatTimer)
})

// ── 레이아웃 계산 ────────────────────────────────────────────────────────

const NODE_W  = 240
const H_GAP   = 60
const V_GAP   = 40
const HEADER_H = 62
const COL_H   = 24
const PAD_B   = 10

function nodeHeight(numCols: number) {
  return HEADER_H + numCols * COL_H + PAD_B
}

function buildLayout(ids: string[], t: Tables): Map<string, { x: number; y: number }> {
  const total = ids.length
  const COLS  = total <= 2 ? total : total <= 6 ? 3 : 4
  const heights = ids.map(id => nodeHeight(t[id]?.columns.length ?? 0))

  const numRows = Math.ceil(total / COLS)
  const rowHeights = Array.from({ length: numRows }, (_, r) => {
    const s = r * COLS
    const e = Math.min(s + COLS, total)
    return Math.max(...heights.slice(s, e), HEADER_H + PAD_B)
  })

  const rowY: number[] = []
  let y = 40
  for (let r = 0; r < numRows; r++) {
    rowY[r] = y
    y += (rowHeights[r] ?? 0) + V_GAP
  }

  const posMap = new Map<string, { x: number; y: number }>()
  ids.forEach((id, i) => {
    posMap.set(id, {
      x: 40 + (i % COLS) * (NODE_W + H_GAP),
      y: rowY[Math.floor(i / COLS)] ?? 40,
    })
  })
  return posMap
}

// ── 그래프 빌드 ──────────────────────────────────────────────────────────

async function buildGraph(t: Tables, custom: CustomRelation[] = []) {
  const ids    = Object.keys(t)
  const posMap = buildLayout(ids, t)

  nodes.value = ids.map(id => ({
    id,
    type: 'tableNode',
    position: posMap.get(id) ?? { x: 0, y: 0 },
    data: {
      ...(t[id] as object),
      showType: showType.value,
      showDesc: showDesc.value,
    },
  })) as unknown as Node[]

  await nextTick()
  rebuildEdges(t, custom)
}

function rebuildEdges(t: Tables, custom: CustomRelation[]) {
  const newEdges: Edge[] = []
  const deleted = deletedRelIds.value

  for (const [id, tbl] of Object.entries(t)) {
    for (const rel of tbl.relations) {
      if (!rel.ref_table || !t[rel.ref_table]) continue
      const edgeId   = `${id}-${rel.column}-${rel.ref_table}`
      const parsedId = `parsed_${id}_${rel.column}_${rel.ref_table}`
      if (deleted.has(parsedId)) continue
      if (newEdges.find(e => e.id === edgeId)) continue

      const isFk = rel.type === 'FK'
      const { sourceHandle, targetHandle } = getBestHandles(id, rel.ref_table)
      newEdges.push({
        id: edgeId,
        type: 'erdEdge',
        source: id,
        target: rel.ref_table,
        sourceHandle,
        targetHandle,
        label: rel.column,
        data: {
          notation: notation.value,
          edgeType: isFk ? 'fk' : 'inferred',
          from_required: false,
          to_required: true,
        },
      })
    }
  }

  for (const cr of custom) {
    if (!t[cr.from_table] || !t[cr.to_table]) continue
    const { sourceHandle: crSH, targetHandle: crTH } = getBestHandles(cr.from_table, cr.to_table)
    newEdges.push({
      id: cr.id,
      type: 'erdEdge',
      source: cr.from_table,
      target: cr.to_table,
      sourceHandle: crSH,
      targetHandle: crTH,
      label: '',
      data: {
        notation: notation.value,
        edgeType: 'custom',
        cardinality: cr.cardinality,
        from_required: cr.from_required,
        to_required: cr.to_required,
      },
    })
  }

  edges.value = newEdges
}

// ── 반응형 업데이트 ──────────────────────────────────────────────────────

watch([showType, showDesc], ([st, sd]) => {
  nodes.value = nodes.value.map(n => ({
    ...n,
    data: { ...n.data, showType: st, showDesc: sd },
  }))
})

watch(notation, n => {
  edges.value = edges.value.map(e => ({
    ...e,
    data: { ...e.data, notation: n },
  }))
})

// ── 파일 처리 ─────────────────────────────────────────────────────────────

const ALLOWED_EXTS = ['.xls', '.xlsx']

function isValidFile(file: File): boolean {
  const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase()
  return ALLOWED_EXTS.includes(ext)
}

async function uploadFile(file: File) {
  if (!isValidFile(file)) {
    errorMsg.value = '잘못된 파일 형식입니다. XLS 또는 XLSX 파일만 업로드할 수 있습니다.'
    return
  }
  loading.value  = true
  errorMsg.value = ''
  filename.value = file.name
  const fd = new FormData()
  fd.append('file', file)
  try {
    const res  = await fetch('/api/parse', { method: 'POST', body: fd })
    const json = await res.json()
    if (!res.ok) { errorMsg.value = json.error ?? '파싱 실패'; return }
    tables.value          = json
    customRelations.value = []
    deletedRelIds.value   = new Set()
    await buildGraph(json)
  } catch (e) {
    errorMsg.value = String(e)
  } finally {
    loading.value = false
  }
}

async function importProject(file: File) {
  if (!file.name.toLowerCase().endsWith('.json')) {
    errorMsg.value = '잘못된 파일 형식입니다. JSON 파일만 업로드할 수 있습니다.'
    return
  }
  loading.value = true
  errorMsg.value = ''
  
  try {
    const text = await file.text()
    const data = JSON.parse(text)
    
    if (data.tables) tables.value = data.tables
    if (data.nodes) nodes.value = data.nodes
    if (data.edges) edges.value = data.edges
    if (data.customRelations) customRelations.value = data.customRelations
    if (data.deletedRelIds) deletedRelIds.value = new Set(data.deletedRelIds)
    if (data.colors) {
      Object.assign(colors, data.colors)
    }
    if (data.notation) notation.value = data.notation
    if (data.showType !== undefined) showType.value = data.showType
    if (data.showDesc !== undefined) showDesc.value = data.showDesc
    filename.value = data.filename || file.name
  } catch (e) {
    errorMsg.value = '프로젝트 불러오기 실패: ' + String(e)
  } finally {
    loading.value = false
  }
}

// ── 드래그 & 드롭 ────────────────────────────────────────────────────────

function onDragOver() { isDragOver.value = true }
function onDragLeave() { isDragOver.value = false }

function onDrop(e: DragEvent) {
  isDragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (!file) return
  
  if (file.name.toLowerCase().endsWith('.json')) {
    importProject(file)
    return
  }
  
  if (!isValidFile(file)) {
    errorMsg.value = '잘못된 파일 형식입니다. XLS, XLSX 또는 JSON 파일만 드롭할 수 있습니다.'
    return
  }
  uploadFile(file)
}

// ── 설정 ────────────────────────────────────────────────────────────────

function handleOpenSettings(panel: 'relations' | 'colors') {
  if (panel === 'relations') showRelationManager.value = true
  else showColorSettings.value = true
}

// ── 관계 관리 ────────────────────────────────────────────────────────────

function onAddRelation(rel: CustomRelation) {
  customRelations.value = [...customRelations.value, rel]
  rebuildEdges(tables.value, customRelations.value)
}

function onDeleteRelation(id: string) {
  if (id.startsWith('parsed_')) {
    deletedRelIds.value = new Set([...deletedRelIds.value, id])
  } else {
    customRelations.value = customRelations.value.filter(r => r.id !== id)
  }
  rebuildEdges(tables.value, customRelations.value)
}

// ── 내보내기 ─────────────────────────────────────────────────────────────

const { fitView, getNodes, onNodeDragStop } = useVueFlow()

function getBestHandles(srcId: string, tgtId: string): { sourceHandle: string; targetHandle: string } {
  const srcNode = getNodes.value.find(n => n.id === srcId)
  const tgtNode = getNodes.value.find(n => n.id === tgtId)
  if (!srcNode || !tgtNode) return { sourceHandle: 'right', targetHandle: 'left' }

  const srcCX = srcNode.position.x + (srcNode.dimensions?.width  ?? NODE_W) / 2
  const srcCY = srcNode.position.y + (srcNode.dimensions?.height ?? 200)    / 2
  const tgtCX = tgtNode.position.x + (tgtNode.dimensions?.width  ?? NODE_W) / 2
  const tgtCY = tgtNode.position.y + (tgtNode.dimensions?.height ?? 200)    / 2

  const dx = tgtCX - srcCX
  const dy = tgtCY - srcCY

  if (Math.abs(dx) >= Math.abs(dy)) {
    return dx >= 0
      ? { sourceHandle: 'right', targetHandle: 'left'  }
      : { sourceHandle: 'left',  targetHandle: 'right' }
  } else {
    return dy >= 0
      ? { sourceHandle: 'bottom', targetHandle: 'top'    }
      : { sourceHandle: 'top',    targetHandle: 'bottom' }
  }
}

onNodeDragStop(() => {
  edges.value = edges.value.map(e => {
    const { sourceHandle, targetHandle } = getBestHandles(e.source, e.target)
    return { ...e, sourceHandle, targetHandle }
  })
})

async function handleExport(type: 'svg' | 'png' | 'excel' | 'json') {
  if (type === 'excel') await exportExcel()
  else if (type === 'json') await exportJson()
  else await exportImage(type)
}

async function exportImage(type: 'svg' | 'png') {
  const el = document.querySelector('.vue-flow') as HTMLElement | null
  if (!el) { errorMsg.value = '캔버스를 찾을 수 없습니다.'; return }

  await fitView({ padding: 0.1, duration: 200 })
  await nextTick()
  await new Promise(r => setTimeout(r, 300))

  try {
    let dataUrl: string
    if (type === 'svg') {
      dataUrl = await toSvg(el, { backgroundColor: colors.canvasBg, skipFonts: true })
    } else {
      dataUrl = await toPng(el, { backgroundColor: colors.canvasBg, pixelRatio: 2, skipFonts: true })
    }
    const a = document.createElement('a')
    a.href = dataUrl
    a.download = `erd.${type}`
    a.click()
  } catch (e) {
    errorMsg.value = `내보내기 실패: ${e}`
  }
}

async function exportJson() {
  if (!nodes.value.length) {
    errorMsg.value = '내보낼 데이터가 없습니다.'
    return
  }
  try {
    const currentNodes = getNodes.value.map(n => ({
      id: n.id,
      type: n.type,
      position: { ...n.position },
      data: { ...n.data },
    }))

    const currentEdges = edges.value.map(e => ({
      id: e.id,
      type: e.type,
      source: e.source,
      target: e.target,
      label: e.label,
      data: { ...e.data }
    }))

    const projectData = {
      version: '1.0',
      tables: tables.value,
      nodes: currentNodes,
      edges: currentEdges,
      customRelations: customRelations.value,
      deletedRelIds: Array.from(deletedRelIds.value),
      colors: { ...colors },
      notation: notation.value,
      showType: showType.value,
      showDesc: showDesc.value,
      filename: filename.value
    }
    
    const blob = new Blob([JSON.stringify(projectData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    let outName = filename.value ? filename.value.split('.')[0] : 'erd'
    a.download = outName + '_export.json'
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    errorMsg.value = String(e)
  }
}

async function exportExcel() {
  if (!nodes.value.length) {
    errorMsg.value = '먼저 파일을 업로드해 주세요.'
    return
  }
  try {
    const payload = {
      nodes: getNodes.value.map(n => ({
        id:     n.id,
        x:      Math.round(n.position.x),
        y:      Math.round(n.position.y),
        width:  Math.round(n.dimensions?.width  ?? 240),
        height: Math.round(n.dimensions?.height ?? 300),
        data:   n.data,
      })),
      edges: edges.value.map(e => ({
        source:   e.source,
        target:   e.target,
        edgeType: (e.data?.edgeType as string) ?? 'inferred',
      })),
    }
    const res = await fetch('/api/export/excel', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      let msg = 'Excel 내보내기 실패'
      try { const j = await res.json(); msg = j.error ?? msg } catch { /* ignore */ }
      errorMsg.value = msg
      return
    }
    const blob = await res.blob()
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = 'erd_export.xlsx'
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    errorMsg.value = String(e)
  }
}
</script>

<style scoped>
.flow-wrap {
  flex: 1;
  position: relative;
  overflow: hidden;
}
.vue-flow { 
  width: 100%; 
  height: 100%; 
  background-color: var(--erd-canvas-bg, #0f1117);
}

.flow-wrap.drag-over { outline: 2px dashed #3b82f6; outline-offset: -4px; }

.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 100%; color: #475569; font-size: 15px; gap: 10px; pointer-events: none;
}
.empty-icon { font-size: 32px; opacity: 0.4; }

.drag-overlay {
  position: absolute; inset: 0;
  background: rgba(59,130,246,0.12);
  display: flex; align-items: center; justify-content: center;
  pointer-events: none;
}
.drag-hint { background: #1d4ed8; color: #fff; padding: 12px 28px; border-radius: 8px; font-size: 16px; font-weight: 600; }

.loading-overlay {
  position: absolute; inset: 0;
  background: rgba(0,0,0,0.55);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; color: #93c5fd;
}
.error-toast {
  position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
  background: #7f1d1d; color: #fca5a5;
  padding: 10px 20px; border-radius: 8px; cursor: pointer; white-space: nowrap; z-index: 100;
}
</style>
