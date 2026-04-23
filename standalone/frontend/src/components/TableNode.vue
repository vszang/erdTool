<template>
  <div
    class="table-node"
    :class="{
      selected: props.selected,
      'with-type': data.showType,
      'with-desc': data.showDesc,
    }"
  >
    <div class="table-header">
      <span class="table-id">{{ data.table_id }}</span>
      <span class="table-name">{{ data.table_name }}</span>
    </div>
    <div class="columns" :class="{ 'with-type': data.showType, 'with-desc': data.showDesc }">
      <div
        v-for="col in data.columns"
        :key="col.name"
        class="col-row"
        :class="{ 'col-pk': col.pk, 'col-fk': !!col.fk_table && !col.pk }"
      >
        <span class="col-key">{{ col.pk ? '🔑' : '\u00a0\u00a0' }}</span>
        <span class="col-name">{{ col.name }}</span>
        <span v-if="data.showType" class="col-type">{{ col.type }}</span>
        <span v-if="data.showDesc" class="col-desc">{{ col.description }}</span>
      </div>
    </div>
    <Handle id="right"  type="source" :position="Position.Right"  />
    <Handle id="left"   type="source" :position="Position.Left"   />
    <Handle id="top"    type="source" :position="Position.Top"    />
    <Handle id="bottom" type="source" :position="Position.Bottom" />
    <Handle id="right"  type="target" :position="Position.Right"  />
    <Handle id="left"   type="target" :position="Position.Left"   />
    <Handle id="top"    type="target" :position="Position.Top"    />
    <Handle id="bottom" type="target" :position="Position.Bottom" />
  </div>
</template>

<script setup lang="ts">
import { toRef } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import type { NodeProps } from '@vue-flow/core'
import type { Table } from '@/types'

interface NodeData extends Table {
  showType: boolean
  showDesc: boolean
}

const props = defineProps<NodeProps<NodeData>>()
const data  = toRef(props, 'data')
</script>

<style scoped>
.table-node {
  background: var(--erd-node-bg, #1e2330);
  border: 1.5px solid var(--erd-node-border, #3b4a6b);
  border-radius: 8px;
  min-width: 220px;
  font-size: 12px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.4);
  overflow: hidden;
  user-select: none;
}
.table-node.with-type          { min-width: 300px; }
.table-node.with-desc          { min-width: 340px; }
.table-node.with-type.with-desc { min-width: 460px; }
.table-node.selected { border-color: #60a5fa; }

.table-header {
  background: var(--erd-node-header, #2d3a52);
  padding: 6px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.table-id   { font-weight: 700; color: var(--erd-id-color, #93c5fd); font-size: 13px; }
.table-name { color: var(--erd-name-color, #94a3b8); font-size: 11px; }

.columns { padding: 4px 0; }

/* grid template: key | name */
.col-row {
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr);
  align-items: center;
  column-gap: 5px;
  padding: 2px 10px;
  color: var(--erd-attr-color, #cbd5e1);
  min-height: 22px;
}
/* key | name | type */
.columns.with-type .col-row {
  grid-template-columns: 18px minmax(0, 1fr) 90px;
}
/* key | name | desc */
.columns.with-desc .col-row {
  grid-template-columns: 18px minmax(0, 1fr) 130px;
}
/* key | name | type | desc */
.columns.with-type.with-desc .col-row {
  grid-template-columns: 18px minmax(0, 1fr) 90px 130px;
}

.col-row:hover { background: #263249; }
.col-pk { color: var(--erd-pk, #fbbf24); }
.col-fk { color: #86efac; }

.col-key  { font-size: 11px; text-align: center; line-height: 1; }
.col-name { font-family: 'Consolas', monospace; font-size: 11px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.col-type { color: var(--erd-type-color, #64748b); font-size: 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.col-desc { color: #94a3b8; font-size: 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* 핸들을 0px로 만들어 overflow:hidden 클리핑 오류 및 시각적 점 제거 */
:deep(.vue-flow__handle) {
  width: 0;
  height: 0;
  min-width: 0;
  min-height: 0;
  border: none;
  background: transparent;
  padding: 0;
}
</style>
