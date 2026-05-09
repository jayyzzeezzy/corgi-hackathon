import type { GraphNode } from '../types/graph'
import { NODE_COLORS } from '../types/graph'

interface Props {
  node: GraphNode | null
  explanation: string
  loading: boolean
  onClose: () => void
}

export default function NodeSidebar({ node, explanation, loading, onClose }: Props) {
  if (!node) return null

  const color = NODE_COLORS[node.type] ?? '#9ca3af'

  return (
    <div style={{
      position: 'absolute',
      right: 0, top: 0, bottom: 0,
      width: 300,
      background: 'white',
      borderLeft: '1px solid #e5e7eb',
      display: 'flex',
      flexDirection: 'column',
      padding: 20,
      gap: 12,
      overflowY: 'auto',
      zIndex: 10,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <h3 style={{ margin: 0, fontSize: 15, fontWeight: 700, color: '#111827' }}>{node.label}</h3>
          <span style={{
            fontSize: 11,
            fontWeight: 600,
            padding: '2px 8px',
            borderRadius: 12,
            background: color + '20',
            color,
            display: 'inline-block',
            width: 'fit-content',
          }}>
            {node.type}
          </span>
        </div>
        <button
          onClick={onClose}
          style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 22, color: '#9ca3af', lineHeight: 1, padding: 0 }}
        >
          ×
        </button>
      </div>

      <p style={{ margin: 0, fontSize: 13, color: '#4b5563', lineHeight: 1.6 }}>
        {node.description}
      </p>

      <hr style={{ border: 'none', borderTop: '1px solid #f3f4f6', margin: 0 }} />

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        <p style={{ margin: 0, fontSize: 11, fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          AI Explanation
        </p>
        {loading
          ? <p style={{ margin: 0, fontSize: 13, color: '#9ca3af' }}>Loading...</p>
          : <p style={{ margin: 0, fontSize: 13, color: '#374151', lineHeight: 1.7 }}>{explanation}</p>
        }
      </div>
    </div>
  )
}
