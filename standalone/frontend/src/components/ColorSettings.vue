<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <span>색상 지정</span>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <div class="color-list">
        <div class="color-row toggle-row">
          <label class="color-label">그리드(점) 표시</label>
          <input type="checkbox" v-model="colors.showGrid" class="toggle-input" />
        </div>
        <div v-for="key in colorKeys" :key="key" class="color-row">
          <label class="color-label">{{ COLOR_LABELS[key] }}</label>
          <div class="color-input-wrap">
            <input
              type="color"
              :value="colors[key]"
              @input="onChange(key, ($event.target as HTMLInputElement).value)"
              class="color-picker"
            />
            <span class="color-hex">{{ colors[key] }}</span>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-reset" @click="resetAll">기본값으로 초기화</button>
        <button class="btn-close" @click="$emit('close')">닫기</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { colors, COLOR_LABELS, DEFAULTS } from '@/store/colors'
import type { ColorSet } from '@/store/colors'

defineEmits<{ 'close': [] }>()

const colorKeys = computed(() => {
  return (Object.keys(DEFAULTS) as (keyof ColorSet)[]).filter(k => typeof DEFAULTS[k] === 'string')
})

function onChange(key: keyof ColorSet, value: string) {
  (colors as any)[key] = value
}

function resetAll() {
  const k = Object.keys(DEFAULTS) as (keyof ColorSet)[]
  k.forEach(key => { colors[key] = DEFAULTS[key] })
}
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
  width: 400px; max-width: 96vw;
  display: flex; flex-direction: column;
  box-shadow: 0 20px 60px rgba(0,0,0,0.6);
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid #2d3a52;
  font-size: 15px; font-weight: 600; color: #93c5fd;
}
.close-btn { background: none; border: none; color: #64748b; font-size: 16px; cursor: pointer; }
.close-btn:hover { color: #cbd5e1; }

.color-list { 
  padding: 12px 18px; 
  display: flex; 
  flex-direction: column; 
  gap: 10px; 
  max-height: 480px; 
  overflow-y: auto; 
}

.color-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.color-label { font-size: 12px; color: #94a3b8; flex: 1; }
.color-input-wrap { display: flex; align-items: center; gap: 8px; }

.color-picker {
  width: 36px; height: 28px;
  border: 1px solid #2d3a52; border-radius: 4px;
  background: none; padding: 0; cursor: pointer;
}
.color-picker::-webkit-color-swatch-wrapper { padding: 2px; }
.color-picker::-webkit-color-swatch { border-radius: 3px; border: none; }

.color-hex { font-size: 11px; color: #64748b; font-family: 'Consolas', monospace; width: 60px; }
.toggle-row { border-bottom: 1px solid #2d3a52; padding-bottom: 12px; margin-bottom: 4px; }
.toggle-input { width: 18px; height: 18px; cursor: pointer; accent-color: #3b82f6; }

.modal-footer {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 18px;
  border-top: 1px solid #2d3a52;
}
.btn-reset {
  background: none; border: 1px solid #475569; border-radius: 5px;
  color: #94a3b8; font-size: 11px; padding: 5px 12px; cursor: pointer;
}
.btn-reset:hover { border-color: #64748b; color: #cbd5e1; }
.btn-close {
  background: #1d4ed8; color: #fff; border: none; border-radius: 5px;
  font-size: 12px; padding: 5px 16px; cursor: pointer;
}
.btn-close:hover { background: #2563eb; }
</style>
