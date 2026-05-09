import { useState, useRef, useCallback } from 'react'
import type { GraphData, GraphNode, DataFlow } from './types/graph'
import { FLOW_COLORS } from './types/graph'
import GraphView from './components/GraphView'
import NodeSidebar from './components/NodeSidebar'
import { parseCode, explainNode } from './services/pipeshift'
import { highlightFlow, clearFlow } from './utils/highlightFlow'

function toRawGitHubUrl(url: string): string {
  // https://github.com/user/repo/blob/branch/path/file.ts
  // → https://raw.githubusercontent.com/user/repo/branch/path/file.ts
  const match = url.match(/github\.com\/([^/]+)\/([^/]+)\/blob\/(.+)/)
  if (match) return `https://raw.githubusercontent.com/${match[1]}/${match[2]}/${match[3]}`
  return url
}

export default function App() {
  const [code, setCode] = useState('')
  const [githubUrl, setGithubUrl] = useState('')
  const [githubLoading, setGithubLoading] = useState(false)
  const [graphData, setGraphData] = useState<GraphData | null>(null)
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [explanation, setExplanation] = useState('')
  const [explanationLoading, setExplanationLoading] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const svgRef = useRef<SVGSVGElement>(null)

  const handleFetchGitHub = async () => {
    const url = githubUrl.trim()
    if (!url) return
    setGithubLoading(true)
    setError('')
    try {
      const rawUrl = toRawGitHubUrl(url)
      const res = await fetch(rawUrl)
      if (!res.ok) throw new Error(`GitHub fetch failed (${res.status}) — make sure the file is public`)
      const text = await res.text()
      setCode(text)
      setGithubUrl('')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch from GitHub')
    } finally {
      setGithubLoading(false)
    }
  }

  const handleMapIt = async () => {
    if (!code.trim()) return
    setLoading(true)
    setError('')
    setGraphData(null)
    setSelectedNode(null)
    try {
      const data = await parseCode(code)
      setGraphData(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to analyze code')
    } finally {
      setLoading(false)
    }
  }

  const handleNodeClick = useCallback(async (node: GraphNode) => {
    setSelectedNode(node)
    setExplanation('')
    setExplanationLoading(true)
    try {
      const text = await explainNode(node.label, node.description)
      setExplanation(text)
    } catch {
      setExplanation('Could not load explanation.')
    } finally {
      setExplanationLoading(false)
    }
  }, [])

  const handleFlowClick = (flow: DataFlow) => {
    highlightFlow(flow, svgRef)
  }

  const handleSidebarClose = () => {
    setSelectedNode(null)
    clearFlow(svgRef)
  }

  const handleReset = () => {
    setGraphData(null)
    setSelectedNode(null)
    setCode('')
    setError('')
    clearFlow(svgRef)
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => setCode((ev.target?.result as string) ?? '')
    reader.readAsText(file)
    e.target.value = ''
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Header */}
      <header style={{
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        padding: '10px 20px',
        borderBottom: '1px solid #e5e7eb',
        background: 'white',
        flexShrink: 0,
      }}>
        <h1 style={{ margin: 0, fontSize: 16, fontWeight: 700 }}>Codebase Cartographer</h1>

        {graphData && (
          <span style={{ fontSize: 13, color: '#6b7280' }}>
            {graphData.nodes.length} nodes · {graphData.edges.length} edges · {graphData.dataFlows.length} flows
          </span>
        )}

        {graphData && (
          <button
            onClick={handleReset}
            style={{ marginLeft: 'auto', fontSize: 13, color: '#6b7280', background: 'none', border: '1px solid #e5e7eb', borderRadius: 6, padding: '4px 12px', cursor: 'pointer' }}
          >
            New Analysis
          </button>
        )}
      </header>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Input panel — shown only before graph renders */}
        {!graphData && (
          <div style={{
            width: 360,
            flexShrink: 0,
            display: 'flex',
            flexDirection: 'column',
            gap: 10,
            padding: 16,
            borderRight: '1px solid #e5e7eb',
          }}>
            <label style={{ fontSize: 12, color: '#6b7280', fontWeight: 500 }}>
              Paste code or upload a file
            </label>

            {/* GitHub URL fetch */}
            <div style={{ display: 'flex', gap: 6 }}>
              <input
                type="text"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleFetchGitHub()}
                placeholder="github.com/user/repo/blob/main/file.ts"
                style={{
                  flex: 1,
                  padding: '7px 10px',
                  fontSize: 12,
                  border: '1px solid #d1d5db',
                  borderRadius: 6,
                  outline: 'none',
                  color: '#111827',
                  fontFamily: 'monospace',
                }}
              />
              <button
                onClick={handleFetchGitHub}
                disabled={!githubUrl.trim() || githubLoading}
                style={{
                  padding: '7px 12px',
                  fontSize: 12,
                  fontWeight: 600,
                  background: githubUrl.trim() && !githubLoading ? '#111827' : '#e5e7eb',
                  color: githubUrl.trim() && !githubLoading ? 'white' : '#9ca3af',
                  border: 'none',
                  borderRadius: 6,
                  cursor: githubUrl.trim() && !githubLoading ? 'pointer' : 'not-allowed',
                  whiteSpace: 'nowrap',
                }}
              >
                {githubLoading ? '...' : 'Fetch'}
              </button>
            </div>

            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="// paste a .js, .ts, .tsx, or .py file here..."
              spellCheck={false}
              style={{
                flex: 1,
                padding: 12,
                fontFamily: 'monospace',
                fontSize: 12,
                border: '1px solid #d1d5db',
                borderRadius: 6,
                resize: 'none',
                outline: 'none',
                color: '#111827',
              }}
            />

            <label style={{
              fontSize: 12,
              color: '#6b7280',
              textAlign: 'center',
              cursor: 'pointer',
              padding: '8px',
              border: '1px dashed #d1d5db',
              borderRadius: 6,
            }}>
              or upload a file (.js .ts .tsx .py)
              <input type="file" accept=".js,.ts,.tsx,.py" style={{ display: 'none' }} onChange={handleFileUpload} />
            </label>

            <button
              onClick={handleMapIt}
              disabled={!code.trim() || loading}
              style={{
                padding: '10px',
                background: code.trim() && !loading ? '#2563eb' : '#e5e7eb',
                color: code.trim() && !loading ? 'white' : '#9ca3af',
                border: 'none',
                borderRadius: 6,
                fontSize: 14,
                fontWeight: 600,
                cursor: code.trim() && !loading ? 'pointer' : 'not-allowed',
              }}
            >
              {loading ? 'Analyzing...' : 'Map It →'}
            </button>

            {error && (
              <p style={{ margin: 0, fontSize: 12, color: '#dc2626', background: '#fef2f2', padding: '8px 12px', borderRadius: 6 }}>
                {error}
              </p>
            )}
          </div>
        )}

        {/* Graph canvas */}
        {graphData && (
          <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
            <GraphView data={graphData} svgRef={svgRef} onNodeClick={handleNodeClick} />

            {/* Data flows panel */}
            {graphData.dataFlows.length > 0 && (
              <div style={{
                position: 'absolute',
                top: 12,
                left: 12,
                background: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: 8,
                padding: '12px',
                minWidth: 200,
                maxWidth: 260,
                boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
              }}>
                <p style={{ margin: '0 0 8px', fontSize: 11, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Data Flows
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  {graphData.dataFlows.map((flow) => (
                    <button
                      key={flow.id}
                      onClick={() => handleFlowClick(flow)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 8,
                        width: '100%',
                        textAlign: 'left',
                        padding: '6px 8px',
                        borderRadius: 4,
                        border: '1px solid #f3f4f6',
                        background: 'white',
                        fontSize: 12,
                        cursor: 'pointer',
                        color: '#374151',
                      }}
                    >
                      <span style={{
                        width: 8, height: 8, borderRadius: '50%', flexShrink: 0,
                        background: FLOW_COLORS[flow.type],
                      }} />
                      {flow.label}
                    </button>
                  ))}
                </div>
                <button
                  onClick={() => clearFlow(svgRef)}
                  style={{ marginTop: 8, fontSize: 11, color: '#9ca3af', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
                >
                  clear highlight
                </button>
              </div>
            )}

            <NodeSidebar
              node={selectedNode}
              explanation={explanation}
              loading={explanationLoading}
              onClose={handleSidebarClose}
            />
          </div>
        )}
      </div>
    </div>
  )
}
