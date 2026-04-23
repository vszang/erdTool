import { reactive, watch } from 'vue'

export interface ColorSet {
  canvasBg:     string
  canvasGrid:   string
  showGrid:     boolean
  nodeBg:       string
  nodeHeader:   string
  nodeBorder:   string
  tableIdColor: string
  tableNameColor: string
  pkColor:      string
  attributeColor: string
  attributeTypeColor: string
  edgeFk:       string
  edgeInferred: string
  edgeCustom:   string
  toolbarBg:    string
}

export const DEFAULTS: ColorSet = {
  canvasBg:     '#0f1117',
  canvasGrid:   '#1e2330',
  showGrid:     true,
  nodeBg:       '#1e2330',
  nodeHeader:   '#2d3a52',
  nodeBorder:   '#3b4a6b',
  tableIdColor: '#93c5fd',
  tableNameColor: '#94a3b8',
  pkColor:      '#fbbf24',
  attributeColor: '#cbd5e1',
  attributeTypeColor: '#64748b',
  edgeFk:       '#60a5fa',
  edgeInferred: '#475569',
  edgeCustom:   '#34d399',
  toolbarBg:    '#161b27',
}

export const COLOR_LABELS: Record<string, string> = {
  canvasBg:     '캔버스 배경',
  canvasGrid:   '그리드 색상',
  nodeBg:       '노드 배경',
  nodeHeader:   '노드 헤더',
  nodeBorder:   '노드 테두리',
  tableIdColor: '테이블 ID(코드)',
  tableNameColor: '테이블명(코멘트)',
  pkColor:      'PK 색상',
  attributeColor: '컬럼명 색상',
  attributeTypeColor: '데이터 타입 색상',
  edgeFk:       'FK 관계선',
  edgeInferred: '추론 관계선',
  edgeCustom:   '커스텀 관계선',
  toolbarBg:    '툴바 배경',
}

function load(): ColorSet {
  try {
    const s = localStorage.getItem('erd-colors')
    return s ? { ...DEFAULTS, ...JSON.parse(s) } : { ...DEFAULTS }
  } catch {
    return { ...DEFAULTS }
  }
}

export const colors = reactive<ColorSet>(load())

export function applyCssVars() {
  const s = document.documentElement.style
  s.setProperty('--erd-canvas-bg',   colors.canvasBg)
  s.setProperty('--erd-canvas-grid', colors.canvasGrid)
  s.setProperty('--erd-node-bg',     colors.nodeBg)
  s.setProperty('--erd-node-header', colors.nodeHeader)
  s.setProperty('--erd-node-border', colors.nodeBorder)
  s.setProperty('--erd-id-color',    colors.tableIdColor)
  s.setProperty('--erd-name-color',  colors.tableNameColor)
  s.setProperty('--erd-pk',          colors.pkColor)
  s.setProperty('--erd-attr-color',  colors.attributeColor)
  s.setProperty('--erd-type-color',  colors.attributeTypeColor)
  s.setProperty('--erd-toolbar-bg',  colors.toolbarBg)
}

watch(colors, () => {
  localStorage.setItem('erd-colors', JSON.stringify({ ...colors }))
  applyCssVars()
}, { deep: true })
