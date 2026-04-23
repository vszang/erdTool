<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <span>관계 관리</span>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <!-- 관계 추가 폼 -->
      <div class="section">
        <div class="section-title">관계 추가</div>
        <div class="form-row">
          <div class="form-col">
            <select v-model="form.from_table" class="sel">
              <option value="">-- FROM 테이블 --</option>
              <option v-for="id in tableIds" :key="id" :value="id">{{ id }}</option>
            </select>
            <div class="req-toggle">
              <button
                class="req-btn"
                :class="{ required: form.from_required, optional: !form.from_required }"
                @click="form.from_required = !form.from_required"
              >{{ form.from_required ? '필수' : '선택' }}</button>
            </div>
          </div>

          <select v-model="form.cardinality" class="sel sel-card">
            <option v-for="c in cardinalities" :key="c" :value="c">{{ c }}</option>
          </select>

          <div class="form-col">
            <select v-model="form.to_table" class="sel">
              <option value="">-- TO 테이블 --</option>
              <option v-for="id in tableIds" :key="id" :value="id">{{ id }}</option>
            </select>
            <div class="req-toggle">
              <button
                class="req-btn"
                :class="{ required: form.to_required, optional: !form.to_required }"
                @click="form.to_required = !form.to_required"
              >{{ form.to_required ? '필수' : '선택' }}</button>
            </div>
          </div>

          <button class="btn btn-add" :disabled="!canAdd" @click="addRelation">추가</button>
        </div>
        <div class="req-hint">필수: 반드시 1개 이상 &nbsp;|&nbsp; 선택: 0일 수도 있음</div>
        <div v-if="formError" class="form-error">{{ formError }}</div>
      </div>

      <!-- 관계 목록 -->
      <div class="section list-section">
        <div class="section-title">전체 관계 목록 <span class="count">({{ allRelations.length }})</span></div>
        <div class="relation-list">
          <div v-if="!allRelations.length" class="empty">관계가 없습니다.</div>
          <div
            v-for="rel in allRelations"
            :key="rel.id"
            class="rel-row"
          >
            <span class="rel-from">{{ rel.from }}</span>
            <span class="rel-opt" :class="rel.fromOpt ? 'opt' : 'req'">{{ rel.fromOpt ? '선택' : '필수' }}</span>
            <span class="rel-card">{{ rel.card }}</span>
            <span class="rel-opt" :class="rel.toOpt ? 'opt' : 'req'">{{ rel.toOpt ? '선택' : '필수' }}</span>
            <span class="rel-to">{{ rel.to }}</span>
            <span class="rel-type-badge" :class="rel.source">{{ sourceLabel(rel.source) }}</span>
            <button class="del-btn" @click="$emit('delete-relation', rel.id)">삭제</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Tables, CustomRelation, Cardinality } from '@/types'

const props = defineProps<{
  tables: Tables
  customRelations: CustomRelation[]
  deletedRelIds: Set<string>
}>()

const emit = defineEmits<{
  'close': []
  'add-relation': [CustomRelation]
  'delete-relation': [string]
}>()

const cardinalities: Cardinality[] = ['1:1', '1:N', 'N:1', 'N:N']

const form = ref({
  from_table:    '',
  to_table:      '',
  cardinality:   '1:N' as Cardinality,
  from_required: true,
  to_required:   false,
})
const formError = ref('')

const tableIds = computed(() => Object.keys(props.tables).sort())
const canAdd   = computed(() =>
  !!form.value.from_table && !!form.value.to_table && form.value.from_table !== form.value.to_table
)

function addRelation() {
  formError.value = ''
  if (!form.value.from_table || !form.value.to_table) {
    formError.value = 'FROM / TO 테이블을 모두 선택하세요.'
    return
  }
  if (form.value.from_table === form.value.to_table) {
    formError.value = 'FROM과 TO는 서로 다른 테이블이어야 합니다.'
    return
  }
  const rel: CustomRelation = {
    id:            `custom_${Date.now()}`,
    from_table:    form.value.from_table,
    to_table:      form.value.to_table,
    cardinality:   form.value.cardinality,
    from_required: form.value.from_required,
    to_required:   form.value.to_required,
  }
  emit('add-relation', rel)
  form.value.from_table = ''
  form.value.to_table   = ''
}

function sourceLabel(source: string) {
  if (source === 'custom')   return '수동'
  if (source === 'fk')       return 'FK'
  return 'FK추론'
}

interface DisplayRel {
  id: string
  from: string
  fromOpt: boolean
  card: string
  toOpt: boolean
  to: string
  source: 'fk' | 'inferred' | 'custom'
}

const allRelations = computed<DisplayRel[]>(() => {
  const list: DisplayRel[] = []

  for (const [tableId, table] of Object.entries(props.tables)) {
    for (const rel of table.relations) {
      if (!rel.ref_table) continue
      const relId = `parsed_${tableId}_${rel.column}_${rel.ref_table}`
      if (props.deletedRelIds.has(relId)) continue
      list.push({
        id:      relId,
        from:    tableId,
        fromOpt: true,    // FK default: 선택 (o{)
        card:    'N:1',
        toOpt:   false,   // FK ref table: 필수 (||)
        to:      rel.ref_table,
        source:  rel.type === 'FK' ? 'fk' : 'inferred',
      })
    }
  }

  for (const cr of props.customRelations) {
    list.push({
      id:      cr.id,
      from:    cr.from_table,
      fromOpt: !cr.from_required,
      card:    cr.cardinality,
      toOpt:   !cr.to_required,
      to:      cr.to_table,
      source:  'custom',
    })
  }

  return list
})
</script>

<style scoped>
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.65);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal {
  background: #1a2132;
  border: 1px solid #2d3a52;
  border-radius: 10px;
  width: 680px; max-width: 96vw; max-height: 80vh;
  display: flex; flex-direction: column;
  box-shadow: 0 20px 60px rgba(0,0,0,0.6);
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid #2d3a52;
  font-size: 15px; font-weight: 600; color: #93c5fd;
}
.close-btn { background: none; border: none; color: #64748b; font-size: 16px; cursor: pointer; line-height: 1; }
.close-btn:hover { color: #cbd5e1; }

.section { padding: 14px 18px; border-bottom: 1px solid #2d3a52; }
.list-section { overflow-y: auto; flex: 1; }
.section-title { font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 10px; }
.count { color: #475569; font-weight: 400; }

.form-row { display: flex; align-items: flex-start; gap: 8px; }
.form-col  { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 0; }

.sel { background: #0f1117; border: 1px solid #2d3a52; border-radius: 5px; color: #cbd5e1; font-size: 12px; padding: 5px 8px; width: 100%; }
.sel:focus { outline: none; border-color: #3b82f6; }
.sel-card { flex: 0 0 72px; text-align: center; width: 72px; }

.req-toggle { display: flex; }
.req-btn {
  width: 100%; font-size: 11px; font-weight: 700; padding: 3px 0;
  border-radius: 4px; border: 1px solid; cursor: pointer;
}
.req-btn.required { background: rgba(29,78,216,0.2); color: #60a5fa; border-color: #1d4ed8; }
.req-btn.optional  { background: rgba(100,116,139,0.2); color: #94a3b8; border-color: #475569; }

.req-hint { font-size: 10px; color: #475569; margin-top: 6px; }
.form-error { color: #f87171; font-size: 11px; margin-top: 6px; }

.btn-add {
  background: #1d4ed8; color: #fff; border: none; border-radius: 5px;
  padding: 5px 14px; font-size: 12px; cursor: pointer; white-space: nowrap; flex-shrink: 0; align-self: flex-start;
}
.btn-add:hover:not(:disabled) { background: #2563eb; }
.btn-add:disabled { opacity: 0.4; cursor: not-allowed; }

.relation-list { display: flex; flex-direction: column; gap: 4px; }
.empty { color: #475569; font-size: 12px; text-align: center; padding: 20px 0; }

.rel-row {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 10px;
  background: #0f1117; border-radius: 5px; border: 1px solid #1e2330;
  font-size: 12px;
}
.rel-from, .rel-to { flex: 1; font-family: 'Consolas', monospace; color: #93c5fd; }
.rel-card { flex: 0 0 44px; text-align: center; font-weight: 700; color: #fbbf24; font-size: 11px; }
.rel-opt { font-size: 10px; font-weight: 700; padding: 2px 5px; border-radius: 3px; flex-shrink: 0; }
.rel-opt.req { background: rgba(29,78,216,0.2); color: #60a5fa; }
.rel-opt.opt { background: rgba(100,116,139,0.15); color: #94a3b8; }

.rel-type-badge { font-size: 9px; font-weight: 700; padding: 2px 5px; border-radius: 3px; flex-shrink: 0; }
.rel-type-badge.fk       { background: rgba(59,130,246,0.2); color: #60a5fa; }
.rel-type-badge.inferred { background: rgba(100,116,139,0.2); color: #94a3b8; }
.rel-type-badge.custom   { background: rgba(16,185,129,0.2); color: #34d399; }

.del-btn {
  background: rgba(127,29,29,0.4); color: #fca5a5; border: 1px solid #7f1d1d;
  border-radius: 4px; font-size: 10px; padding: 2px 8px; cursor: pointer; flex-shrink: 0;
}
.del-btn:hover { background: rgba(127,29,29,0.7); }
</style>
