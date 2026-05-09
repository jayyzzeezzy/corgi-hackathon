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
      right: 212,
      top: 0, bottom: 0,
      width: 272,
      background: '#ffffff',
      borderLeft: '1px solid #e5e7eb',
      display: 'flex',
      flexDirection: 'column',
      overflowY: 'auto',
      zIndex: 10,
      fontFamily: 'Inter, system-ui, sans-serif',
    }}>
      {/* Header */}
      <div style={{
        padding: '16px 20px',
        borderBottom: '1px solid #f3f4f6',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        gap: 12,
        flexShrink: 0,
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 5, minWidth: 0 }}>
          <h3 style={{
            margin: 0,
            fontSize: 14,
            fontWeight: 600,
            color: '#111827',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}>
            {node.label}
          </h3>
          <span style={{
            display: 'flex',
            alignItems: 'center',
            gap: 5,
            fontSize: 10,
            fontWeight: 600,
            color: '#6b7280',
            textTransform: 'uppercase',
            letterSpacing: '0.07em',
          }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: color, flexShrink: 0 }} />
            {node.type}
          </span>
        </div>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: '#9ca3af',
            fontSize: 18,
            lineHeight: 1,
            padding: 0,
            flexShrink: 0,
            marginTop: 1,
          }}
        >
          ×
        </button>
      </div>

      {/* Description */}
      <div style={{ padding: '16px 20px', borderBottom: '1px solid #f3f4f6', flexShrink: 0 }}>
        <p style={{ margin: 0, fontSize: 13, color: '#4b5563', lineHeight: 1.65 }}>
          {node.description}
        </p>
      </div>

      {/* AI Explanation */}
      <div style={{ padding: '16px 20px', flex: 1 }}>
        <p style={{
          margin: '0 0 10px',
          fontSize: 10,
          fontWeight: 600,
          color: '#9ca3af',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
        }}>
          AI Explanation
        </p>
        {loading ? (
          <p style={{ margin: 0, fontSize: 13, color: '#9ca3af' }}>Loading…</p>
        ) : (
          <p style={{ margin: 0, fontSize: 13, color: '#374151', lineHeight: 1.7 }}>
            {explanation}
          </p>
        )}
      </div>
    </div>
  )
}
