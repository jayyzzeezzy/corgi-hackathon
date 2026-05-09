export type NodeType = 'component' | 'function' | 'class' | 'hook' | 'util'
export type EdgeRelationship = 'imports' | 'calls' | 'extends' | 'uses'
export type DataFlowType = 'user_input' | 'api_call' | 'db_read' | 'prop' | 'state'

export interface GraphNode {
  id: string
  label: string
  type: NodeType
  description: string
  x?: number
  y?: number
  vx?: number
  vy?: number
  fx?: number | null
  fy?: number | null
}

export interface GraphEdge {
  source: string | GraphNode
  target: string | GraphNode
  relationship: EdgeRelationship
}

export interface DataFlow {
  id: string
  label: string
  origin: string
  type: DataFlowType
  path: string[]
  description: string
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  dataFlows: DataFlow[]
}

export const FLOW_COLORS: Record<DataFlowType, string> = {
  user_input: '#60a5fa',
  api_call:   '#f59e0b',
  db_read:    '#34d399',
  prop:       '#a78bfa',
  state:      '#fb7185',
}

export const NODE_COLORS: Record<NodeType, string> = {
  component: '#6366f1',
  function:  '#22d3ee',
  class:     '#f59e0b',
  hook:      '#ec4899',
  util:      '#10b981',
}
