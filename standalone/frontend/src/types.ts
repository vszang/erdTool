export interface Column {
  name: string
  description: string
  type: string
  pk: boolean
  null: string
  default: string
  fk_table?: string | null
  fk_column?: string | null
}

export interface Relation {
  type: 'FK' | 'FK_INFERRED'
  column: string
  ref_table: string | null
  ref_column: string
}

export interface Table {
  table_id: string
  table_name: string
  table_space: string
  columns: Column[]
  relations: Relation[]
}

export type Tables = Record<string, Table>

export type Notation = 'IE' | 'Barker'

export type Cardinality = '1:1' | '1:N' | 'N:1' | 'N:N'

export interface CustomRelation {
  id: string
  from_table: string
  to_table: string
  cardinality: Cardinality
  from_required: boolean
  to_required: boolean
}
