import { useEffect, useRef } from 'react'
import type { GraphNode } from '../types/graph'

interface Props {
  nodes: GraphNode[]
  currentIndex: number
  onJumpTo: (index: number) => void
}

export default function TraversalList({ nodes, currentIndex, onJumpTo }: Props) {
  const currentRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    currentRef.current?.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
  }, [currentIndex])

  return (
    <div style={{
      position: 'absolute',
      right: 0, top: 0, bottom: 0,
      width: 212,
      background: '#ffffff',
      borderLeft: '1px solid #e5e7eb',
      display: 'flex',
      flexDirection: 'column',
      zIndex: 5,
      fontFamily: 'Inter, system-ui, sans-serif',
    }}>
      <div style={{
        padding: '14px 16px 12px',
        borderBottom: '1px solid #f3f4f6',
        flexShrink: 0,
      }}>
        <p style={{ margin: 0, fontSize: 10, fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          Traversal
        </p>
        <p style={{ margin: '3px 0 0', fontSize: 12, color: '#111827', fontWeight: 500 }}>
          {currentIndex + 1}{' '}
          <span style={{ color: '#9ca3af', fontWeight: 400 }}>of {nodes.length}</span>
        </p>
      </div>

      <div style={{ flex: 1, overflowY: 'auto' }}>
        {nodes.map((node, i) => {
          const isCurrent = i === currentIndex
          const isVisited = i < currentIndex
          const isFuture = i > currentIndex

          return (
            <button
              key={node.id}
              ref={isCurrent ? currentRef : undefined}
              onClick={() => onJumpTo(i)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                width: '100%',
                textAlign: 'left',
                padding: '7px 16px 7px 14px',
                border: 'none',
                borderLeft: isCurrent ? '2px solid #111827' : '2px solid transparent',
                borderBottom: '1px solid #f9fafb',
                background: isCurrent ? '#f9fafb' : 'white',
                cursor: 'pointer',
                opacity: isFuture ? 0.28 : 1,
              }}
            >
              <span style={{
                fontSize: 10,
                color: isCurrent ? '#111827' : '#d1d5db',
                fontWeight: isCurrent ? 600 : 400,
                width: 16,
                flexShrink: 0,
                textAlign: 'right',
                fontVariantNumeric: 'tabular-nums',
              }}>
                {i + 1}
              </span>

              <span style={{
                fontSize: 12,
                fontWeight: isCurrent ? 500 : 400,
                color: isCurrent ? '#111827' : isVisited ? '#374151' : '#9ca3af',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                flex: 1,
              }}>
                {node.label}
              </span>

              {isVisited && (
                <span style={{
                  width: 5,
                  height: 5,
                  borderRadius: '50%',
                  background: '#d1d5db',
                  flexShrink: 0,
                }} />
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}
