<template>
  <g>
    <!-- 기본 Edge (Barker가 아닌 경우) -->
    <template v-if="notation !== 'Barker'">
      <BaseEdge :id="id" :path="edgePath" :style="edgeStyle" />
    </template>

    <!-- Barker: source-half / target-half 각각 다른 dash 적용 -->
    <template v-else>
      <path
        :id="id + '-source'"
        :d="edgePath"
        :style="{
          stroke: color,
          strokeWidth: '1.5',
          fill: 'none',
          strokeDasharray: sourceOpt ? '5, 5' : 'none',
          clipPath: `url(#clip-source-${id})`
        }"
      />
      <path
        :id="id + '-target'"
        :d="edgePath"
        :style="{
          stroke: color,
          strokeWidth: '1.5',
          fill: 'none',
          strokeDasharray: targetOpt ? '5, 5' : 'none',
          clipPath: `url(#clip-target-${id})`
        }"
      />
      <defs>
        <clipPath :id="`clip-source-${id}`">
          <rect v-bind="clipRects.src" />
        </clipPath>
        <clipPath :id="`clip-target-${id}`">
          <rect v-bind="clipRects.tgt" />
        </clipPath>
      </defs>
    </template>

    <!-- ── Source 마커 그룹 (좌표계를 sourcePosition 방향으로 회전) ── -->
    <g :transform="`translate(${sourceX}, ${sourceY}) rotate(${srcRotation})`">
      <!-- stub -->
      <line x1="0" y1="0" :x2="MK" y2="0" :stroke="color" stroke-width="1.5" />

      <!-- IE 표기법 source 마커 -->
      <template v-if="notation === 'IE'">
        <template v-if="sourceMult === 'many' && sourceOpt">
          <!-- o{ 0..N -->
          <circle cx="11" cy="0" r="3" :stroke="color" stroke-width="1.5" fill="none" />
          <line x1="6" y1="-8" x2="6" y2="8" :stroke="color" stroke-width="1.5" />
          <line x1="0" y1="-8" x2="6" y2="0" :stroke="color" stroke-width="1.5" />
          <line x1="0" y1="8"  x2="6" y2="0" :stroke="color" stroke-width="1.5" />
        </template>
        <template v-else-if="sourceMult === 'many'">
          <!-- |{ 1..N -->
          <line x1="9" y1="-8" x2="9" y2="8" :stroke="color" stroke-width="1.5" />
          <line x1="0" y1="-8" x2="6" y2="0" :stroke="color" stroke-width="1.5" />
          <line x1="0" y1="8"  x2="6" y2="0" :stroke="color" stroke-width="1.5" />
        </template>
        <template v-else-if="sourceOpt">
          <!-- o| 0..1 -->
          <circle cx="5" cy="0" r="3" :stroke="color" stroke-width="1.5" fill="none" />
          <line x1="11" y1="-8" x2="11" y2="8" :stroke="color" stroke-width="1.5" />
        </template>
        <template v-else>
          <!-- || 1..1 -->
          <line x1="4" y1="-8" x2="4" y2="8" :stroke="color" stroke-width="1.5" />
          <line x1="9" y1="-8" x2="9" y2="8" :stroke="color" stroke-width="1.5" />
        </template>
      </template>

      <!-- Barker 표기법 source 마커 -->
      <template v-else-if="notation === 'Barker' && sourceMult === 'many'">
        <line x1="0" y1="-8" x2="12" y2="0" :stroke="color" stroke-width="1.5" />
        <line x1="0" y1="0"  x2="12" y2="0" :stroke="color" stroke-width="1.5" />
        <line x1="0" y1="8"  x2="12" y2="0" :stroke="color" stroke-width="1.5" />
      </template>
    </g>

    <!-- ── Target 마커 그룹 (좌표계를 targetPosition 방향으로 회전) ── -->
    <g :transform="`translate(${targetX}, ${targetY}) rotate(${tgtRotation})`">
      <!-- stub -->
      <line :x1="-MK" y1="0" x2="0" y2="0" :stroke="color" stroke-width="1.5" />

      <!-- IE 표기법 target 마커 -->
      <template v-if="notation === 'IE'">
        <template v-if="targetMult === 'many' && targetOpt">
          <!-- o{ 0..N -->
          <circle cx="-11" cy="0" r="3" :stroke="color" stroke-width="1.5" fill="none" />
          <line x1="-6" y1="-8" x2="-6" y2="8" :stroke="color" stroke-width="1.5" />
          <line x1="0" y1="-8" x2="-6" y2="0" :stroke="color" stroke-width="1.5" />
          <line x1="0" y1="8"  x2="-6" y2="0" :stroke="color" stroke-width="1.5" />
        </template>
        <template v-else-if="targetMult === 'many'">
          <!-- |{ 1..N -->
          <line x1="-9" y1="-8" x2="-9" y2="8" :stroke="color" stroke-width="1.5" />
          <line x1="0" y1="-8" x2="-6" y2="0" :stroke="color" stroke-width="1.5" />
          <line x1="0" y1="8"  x2="-6" y2="0" :stroke="color" stroke-width="1.5" />
        </template>
        <template v-else-if="targetOpt">
          <!-- o| 0..1 -->
          <circle cx="-5" cy="0" r="3" :stroke="color" stroke-width="1.5" fill="none" />
          <line x1="-11" y1="-8" x2="-11" y2="8" :stroke="color" stroke-width="1.5" />
        </template>
        <template v-else>
          <!-- || 1..1 -->
          <line x1="-4" y1="-8" x2="-4" y2="8" :stroke="color" stroke-width="1.5" />
          <line x1="-9" y1="-8" x2="-9" y2="8" :stroke="color" stroke-width="1.5" />
        </template>
      </template>

      <!-- Barker 표기법 target 마커 -->
      <template v-else-if="notation === 'Barker' && targetMult === 'many'">
        <line x1="0"   y1="-8" x2="-12" y2="0" :stroke="color" stroke-width="1.5" />
        <line x1="0"   y1="0"  x2="-12" y2="0" :stroke="color" stroke-width="1.5" />
        <line x1="0"   y1="8"  x2="-12" y2="0" :stroke="color" stroke-width="1.5" />
      </template>
    </g>

    <!-- 카디널리티 레이블 -->
    <text
      v-if="cardLabel"
      :x="labelX"
      :y="labelY + 6"
      text-anchor="middle"
      dominant-baseline="middle"
      font-size="9"
      fill="#94a3b8"
      style="pointer-events: none;"
    >{{ cardLabel }}</text>
  </g>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { BaseEdge, getSmoothStepPath, type EdgeProps } from '@vue-flow/core'
import { colors } from '@/store/colors'
import type { Cardinality } from '@/types'

const MK = 16

interface EdgeData {
  notation?: string
  edgeType?: 'fk' | 'inferred' | 'custom'
  cardinality?: Cardinality
  from_required?: boolean
  to_required?: boolean
}

const props = defineProps<EdgeProps & { data?: EdgeData }>()

const notation    = computed(() => props.data?.notation ?? 'IE')
const cardinality = computed(() => props.data?.cardinality as Cardinality | undefined)
const edgeType    = computed(() => props.data?.edgeType ?? 'inferred')

const sourceMult = computed(() => {
  if (!cardinality.value) return 'many'
  return cardinality.value.split(':')[0] === 'N' ? 'many' : 'one'
})
const targetMult = computed(() => {
  if (!cardinality.value) return 'one'
  return cardinality.value.split(':')[1] === 'N' ? 'many' : 'one'
})

const sourceOpt = computed(() => {
  const req = props.data?.from_required
  if (req === undefined) return true
  return !req
})
const targetOpt = computed(() => {
  const req = props.data?.to_required
  if (req === undefined) return false
  return !req
})

const cardLabel = computed(() => cardinality.value ?? null)

// ── 방향 계산 ────────────────────────────────────────────────────────────

// source 마커 그룹 회전각: edge가 source에서 나가는 방향으로 +x축을 맞춤
const srcRotation = computed(() => {
  switch (props.sourcePosition) {
    case 'left':   return 180
    case 'bottom': return 90
    case 'top':    return -90
    default:       return 0   // right
  }
})

// target 마커 그룹 회전각: edge가 target에 도착하는 방향으로 -x축을 맞춤
const tgtRotation = computed(() => {
  switch (props.targetPosition) {
    case 'right':  return 180
    case 'top':    return 90    // 위쪽 도착: stub이 위로 뻗어야 함
    case 'bottom': return -90   // 아래쪽 도착: stub이 아래로 뻗어야 함
    default:       return 0     // left
  }
})

// stub 길이 만큼 offset된 path 시작/끝 좌표
const srcPathX = computed(() => {
  switch (props.sourcePosition) {
    case 'right':  return props.sourceX + MK
    case 'left':   return props.sourceX - MK
    default:       return props.sourceX
  }
})
const srcPathY = computed(() => {
  switch (props.sourcePosition) {
    case 'bottom': return props.sourceY + MK
    case 'top':    return props.sourceY - MK
    default:       return props.sourceY
  }
})
const tgtPathX = computed(() => {
  switch (props.targetPosition) {
    case 'left':   return props.targetX - MK
    case 'right':  return props.targetX + MK
    default:       return props.targetX
  }
})
const tgtPathY = computed(() => {
  switch (props.targetPosition) {
    case 'top':    return props.targetY - MK
    case 'bottom': return props.targetY + MK
    default:       return props.targetY
  }
})

// ── Barker 클립 경로 ──────────────────────────────────────────────────────

const minX = computed(() => Math.min(props.sourceX, props.targetX))
const maxX = computed(() => Math.max(props.sourceX, props.targetX))
const minY = computed(() => Math.min(props.sourceY, props.targetY))
const maxY = computed(() => Math.max(props.sourceY, props.targetY))
const midX = computed(() => (props.sourceX + props.targetX) / 2)
const midY = computed(() => (props.sourceY + props.targetY) / 2)

const clipRects = computed(() => {
  const M  = 60
  const x0 = minX.value - M, y0 = minY.value - M
  const x1 = maxX.value + M, y1 = maxY.value + M
  const mx = midX.value,     my = midY.value

  const isHoriz = props.sourcePosition === 'right' || props.sourcePosition === 'left'
  let src, tgt

  if (isHoriz) {
    if (props.sourceX <= props.targetX) {
      src = { x: x0, y: y0, width: mx - x0,  height: y1 - y0 }
      tgt = { x: mx, y: y0, width: x1 - mx,  height: y1 - y0 }
    } else {
      src = { x: mx, y: y0, width: x1 - mx,  height: y1 - y0 }
      tgt = { x: x0, y: y0, width: mx - x0,  height: y1 - y0 }
    }
  } else {
    if (props.sourceY <= props.targetY) {
      src = { x: x0, y: y0, width: x1 - x0, height: my - y0 }
      tgt = { x: x0, y: my, width: x1 - x0, height: y1 - my }
    } else {
      src = { x: x0, y: my, width: x1 - x0, height: y1 - my }
      tgt = { x: x0, y: y0, width: x1 - x0, height: my - y0 }
    }
  }
  return { src, tgt }
})

// ── 색상 ────────────────────────────────────────────────────────────────

const color = computed(() => {
  const et = edgeType.value
  if (et === 'fk')     return colors.edgeFk
  if (et === 'custom') return colors.edgeCustom
  return colors.edgeInferred
})

const edgeStyle = computed(() => {
  const style: any = { stroke: color.value, strokeWidth: '1.5' }
  if (notation.value === 'Barker' && (sourceOpt.value || targetOpt.value)) {
    style.strokeDasharray = '5, 5'
  }
  return style
})

// ── 경로 ────────────────────────────────────────────────────────────────

const pathResult = computed(() =>
  getSmoothStepPath({
    sourceX:        srcPathX.value,
    sourceY:        srcPathY.value,
    sourcePosition: props.sourcePosition,
    targetX:        tgtPathX.value,
    targetY:        tgtPathY.value,
    targetPosition: props.targetPosition,
    borderRadius:   8,
  })
)

const edgePath = computed(() => pathResult.value[0])
const labelX   = computed(() => pathResult.value[1])
const labelY   = computed(() => pathResult.value[2])
</script>
