import { useState, useMemo } from 'react'

interface Props {
  paths: string[]
  repoName: string
}

// Nested folder/file tree — null means file, object means folder
type Tree = { [key: string]: Tree | null }

function buildTree(paths: string[]): Tree {
  const root: Tree = {}
  for (const path of paths) {
    const parts = path.split('/')
    let node = root
    for (let i = 0; i < parts.length - 1; i++) {
      if (node[parts[i]] === undefined || node[parts[i]] === null) {
        node[parts[i]] = {}
      }
      node = node[parts[i]] as Tree
    }
    node[parts[parts.length - 1]] = null
  }
  return root
}

function sortEntries(entries: [string, Tree | null][]): [string, Tree | null][] {
  return entries.sort((a, b) => {
    const aDir = a[1] !== null
    const bDir = b[1] !== null
    if (aDir !== bDir) return aDir ? -1 : 1
    return a[0].localeCompare(b[0])
  })
}

function getFileExt(name: string): string {
  const dot = name.lastIndexOf('.')
  return dot === -1 ? '' : name.slice(dot + 1)
}

function fileColor(name: string): string {
  const ext = getFileExt(name)
  if (ext === 'tsx' || ext === 'jsx') return '#6366f1'
  if (ext === 'ts') return '#22d3ee'
  if (ext === 'js') return '#f59e0b'
  if (ext === 'py') return '#10b981'
  return '#9ca3af'
}

interface NodeProps {
  name: string
  node: Tree | null
  depth: number
  defaultOpen: boolean
}

function TreeNode({ name, node, depth, defaultOpen }: NodeProps) {
  const [open, setOpen] = useState(defaultOpen)
  const indent = depth * 14 + 12

  if (node === null) {
    return (
      <div
        title={name}
        style={{
          paddingLeft: indent,
          paddingTop: 3,
          paddingBottom: 3,
          paddingRight: 12,
          fontSize: 12,
          color: '#4b5563',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          display: 'flex',
          alignItems: 'center',
          gap: 6,
        }}
      >
        <span style={{ width: 6, height: 6, borderRadius: '50%', background: fileColor(name), flexShrink: 0 }} />
        {name}
      </div>
    )
  }

  const entries = sortEntries(Object.entries(node))

  return (
    <div>
      <div
        onClick={() => setOpen((o) => !o)}
        style={{
          paddingLeft: indent - 2,
          paddingTop: 4,
          paddingBottom: 4,
          paddingRight: 12,
          fontSize: 12,
          fontWeight: 500,
          color: '#111827',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: 5,
          userSelect: 'none',
        }}
      >
        <span style={{
          fontSize: 8,
          color: '#9ca3af',
          display: 'inline-block',
          transform: open ? 'rotate(90deg)' : 'none',
          transition: 'transform 0.12s',
          flexShrink: 0,
          width: 8,
        }}>
          ▶
        </span>
        <span style={{ color: '#6b7280' }}>{name}</span>
      </div>
      {open && (
        <div>
          {entries.map(([childName, childNode]) => (
            <TreeNode
              key={childName}
              name={childName}
              node={childNode}
              depth={depth + 1}
              defaultOpen={false}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default function FileTree({ paths, repoName }: Props) {
  const tree = useMemo(() => buildTree(paths), [paths])
  const entries = sortEntries(Object.entries(tree))

  return (
    <div style={{
      width: 220,
      flexShrink: 0,
      borderRight: '1px solid #f0f0f0',
      background: '#ffffff',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      fontFamily: 'Inter, system-ui, sans-serif',
    }}>
      <div style={{
        padding: '14px 12px 10px',
        borderBottom: '1px solid #f3f4f6',
        flexShrink: 0,
      }}>
        <p style={{ margin: 0, fontSize: 10, fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          Files
        </p>
        <p style={{
          margin: '3px 0 0',
          fontSize: 12,
          color: '#111827',
          fontWeight: 500,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}>
          {repoName}
        </p>
        <p style={{ margin: '2px 0 0', fontSize: 11, color: '#9ca3af' }}>
          {paths.length} files
        </p>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '6px 0' }}>
        {entries.map(([name, node]) => (
          <TreeNode
            key={name}
            name={name}
            node={node}
            depth={0}
            defaultOpen={node !== null}
          />
        ))}
      </div>
    </div>
  )
}
