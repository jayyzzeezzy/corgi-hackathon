import { useState, useRef, useCallback, useEffect } from 'react'
import type { GraphData, GraphNode, DataFlow } from './types/graph'
import { FLOW_COLORS } from './types/graph'
import GraphView from './components/GraphView'
import NodeSidebar from './components/NodeSidebar'
import { parseCode, explainNode } from './services/pipeshift'
import { fetchRepoGraph } from './services/github'
import FileTree from './components/FileTree'
import { highlightFlow, clearFlow, highlightStep } from './utils/highlightFlow'
import { computeTraversal } from './utils/traversal'
import PlayControls from './components/PlayControls'
import TraversalList from './components/TraversalList'

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
  const [repoPaths, setRepoPaths] = useState<string[] | null>(null)
  const [repoName, setRepoName] = useState('')
  const svgRef = useRef<SVGSVGElement>(null)

  // Playback state
  const [traversal, setTraversal] = useState<string[]>([])
  const [playStep, setPlayStep] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [playSpeed, setPlaySpeed] = useState(1000)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const visitedRef = useRef<Set<string>>(new Set())

  const handleFetchGitHub = async () => {
    const url = githubUrl.trim()
    if (!url) return
    setGithubLoading(true)
    setError('')

    const isFileUrl = url.includes('/blob/')

    try {
      if (isFileUrl) {
        // Single file → load into textarea
        const rawUrl = toRawGitHubUrl(url)
        const res = await fetch(rawUrl)
        if (!res.ok) throw new Error(`GitHub fetch failed (${res.status}) — make sure the file is public`)
        setCode(await res.text())
        setGithubUrl('')
      } else {
        // Whole repo → build file dependency graph directly
        setGraphData(null)
        setSelectedNode(null)
        setRepoPaths(null)
        const result = await fetchRepoGraph(url)
        setGraphData(result.graph)
        setRepoPaths(result.paths)
        setRepoName(result.repoName)
        setGithubUrl('')
      }
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
    setRepoPaths(null)
    setRepoName('')
    clearFlow(svgRef)
    stopPlayback()
  }

  // Compute traversal order whenever graphData changes
  useEffect(() => {
    if (!graphData) return
    const order = computeTraversal(graphData)
    setTraversal(order)
    setPlayStep(0)
    setIsPlaying(false)
    visitedRef.current = new Set()
  }, [graphData])

  // Animate each step
  useEffect(() => {
    if (!graphData || traversal.length === 0) return
    const nodeId = traversal[playStep]
    const prevNodeId = playStep > 0 ? traversal[playStep - 1] : null
    visitedRef.current.add(nodeId)
    highlightStep(nodeId, prevNodeId, new Set(visitedRef.current), svgRef)
  }, [playStep, traversal, graphData])

  function stopPlayback() {
    if (intervalRef.current) clearInterval(intervalRef.current)
    intervalRef.current = null
    setIsPlaying(false)
  }

  const handlePlay = () => {
    if (playStep >= traversal.length - 1) return
    setIsPlaying(true)
    intervalRef.current = setInterval(() => {
      setPlayStep((prev) => {
        if (prev >= traversal.length - 1) {
          stopPlayback()
          return prev
        }
        return prev + 1
      })
    }, playSpeed)
  }

  const handlePause = () => stopPlayback()

  const handleNext = () => {
    if (playStep < traversal.length - 1) setPlayStep((p) => p + 1)
  }

  const handlePlayReset = () => {
    stopPlayback()
    visitedRef.current = new Set()
    setPlayStep(0)
    clearFlow(svgRef)
  }

  const handleSpeedChange = (ms: number) => {
    setPlaySpeed(ms)
    if (isPlaying) {
      stopPlayback()
      // Restart with new speed
      setIsPlaying(true)
      intervalRef.current = setInterval(() => {
        setPlayStep((prev) => {
          if (prev >= traversal.length - 1) { stopPlayback(); return prev }
          return prev + 1
        })
      }, ms)
    }
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
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', fontFamily: 'Inter, system-ui, sans-serif' }}>
      {/* Header */}
      <header style={{
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        padding: '0 20px',
        height: 48,
        borderBottom: '1px solid #f0f0f0',
        background: 'white',
        flexShrink: 0,
      }}>
        <h1 style={{ margin: 0, fontSize: 14, fontWeight: 600, color: '#111827', letterSpacing: '-0.01em' }}>
          Codebase Cartographer
        </h1>

        {graphData && (
          <span style={{ fontSize: 12, color: '#9ca3af', fontVariantNumeric: 'tabular-nums' }}>
            {graphData.nodes.length} nodes · {graphData.edges.length} edges
          </span>
        )}

        {graphData && (
          <button
            onClick={handleReset}
            style={{
              marginLeft: 'auto',
              fontSize: 12,
              color: '#6b7280',
              background: 'none',
              border: '1px solid #e5e7eb',
              borderRadius: 6,
              padding: '5px 12px',
              cursor: 'pointer',
            }}
          >
            New Analysis
          </button>
        )}
      </header>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Input panel — shown only before graph renders */}
        {!graphData && (
          <div style={{
            width: 340,
            flexShrink: 0,
            display: 'flex',
            flexDirection: 'column',
            gap: 8,
            padding: '20px 16px',
            borderRight: '1px solid #f0f0f0',
          }}>
            <p style={{ margin: '0 0 4px', fontSize: 11, fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.07em' }}>
              Source
            </p>

            {/* GitHub URL */}
            <div style={{ display: 'flex', gap: 6 }}>
              <input
                type="text"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleFetchGitHub()}
                placeholder="github.com/user/repo or …/blob/main/file.ts"
                style={{
                  flex: 1,
                  padding: '7px 10px',
                  fontSize: 12,
                  border: '1px solid #e5e7eb',
                  borderRadius: 6,
                  outline: 'none',
                  color: '#111827',
                  fontFamily: 'ui-monospace, monospace',
                  background: '#fafafa',
                }}
              />
              <button
                onClick={handleFetchGitHub}
                disabled={!githubUrl.trim() || githubLoading}
                style={{
                  padding: '7px 12px',
                  fontSize: 12,
                  fontWeight: 500,
                  background: githubUrl.trim() && !githubLoading ? '#111827' : '#f3f4f6',
                  color: githubUrl.trim() && !githubLoading ? 'white' : '#9ca3af',
                  border: 'none',
                  borderRadius: 6,
                  cursor: githubUrl.trim() && !githubLoading ? 'pointer' : 'not-allowed',
                  whiteSpace: 'nowrap',
                }}
              >
                {githubLoading ? '…' : 'Fetch'}
              </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 8, margin: '4px 0' }}>
              <div style={{ flex: 1, height: 1, background: '#f0f0f0' }} />
              <span style={{ fontSize: 11, color: '#c4c4c4' }}>or paste code</span>
              <div style={{ flex: 1, height: 1, background: '#f0f0f0' }} />
            </div>

            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="// .js  .ts  .tsx  .py"
              spellCheck={false}
              style={{
                flex: 1,
                padding: '10px 12px',
                fontFamily: 'ui-monospace, monospace',
                fontSize: 12,
                border: '1px solid #e5e7eb',
                borderRadius: 6,
                resize: 'none',
                outline: 'none',
                color: '#111827',
                background: '#fafafa',
                lineHeight: 1.6,
                minHeight: 220,
              }}
            />

            <label style={{
              fontSize: 12,
              color: '#9ca3af',
              textAlign: 'center',
              cursor: 'pointer',
              padding: '8px',
              border: '1px dashed #e5e7eb',
              borderRadius: 6,
              transition: 'border-color 0.1s',
            }}>
              Upload a file (.js .ts .tsx .py)
              <input type="file" accept=".js,.ts,.tsx,.py" style={{ display: 'none' }} onChange={handleFileUpload} />
            </label>

            <button
              onClick={handleMapIt}
              disabled={!code.trim() || loading}
              style={{
                padding: '9px',
                background: code.trim() && !loading ? '#111827' : '#f3f4f6',
                color: code.trim() && !loading ? 'white' : '#9ca3af',
                border: 'none',
                borderRadius: 6,
                fontSize: 13,
                fontWeight: 500,
                cursor: code.trim() && !loading ? 'pointer' : 'not-allowed',
                letterSpacing: '0.01em',
              }}
            >
              {loading ? 'Analyzing…' : 'Map It →'}
            </button>

            {error && (
              <p style={{ margin: 0, fontSize: 12, color: '#dc2626', padding: '8px 12px', borderRadius: 6, border: '1px solid #fee2e2', background: '#fef9f9' }}>
                {error}
              </p>
            )}
          </div>
        )}

        {/* File tree sidebar — shown when graph comes from a repo fetch */}
        {graphData && repoPaths && (
          <FileTree paths={repoPaths} repoName={repoName} />
        )}

        {/* Graph canvas */}
        {graphData && (
          <div style={{ flex: 1, position: 'relative', overflow: 'hidden', background: '#fafaf9' }}>
            <GraphView data={graphData} svgRef={svgRef} onNodeClick={handleNodeClick} />

            {/* Data flows panel */}
            {graphData.dataFlows.length > 0 && (
              <div style={{
                position: 'absolute',
                top: 16,
                left: 16,
                background: '#ffffff',
                border: '1px solid #e5e7eb',
                borderRadius: 8,
                padding: '12px',
                minWidth: 180,
                maxWidth: 240,
                boxShadow: '0 4px 16px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04)',
                fontFamily: 'Inter, system-ui, sans-serif',
              }}>
                <p style={{ margin: '0 0 8px', fontSize: 10, fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                  Data Flows
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
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
                        padding: '5px 8px',
                        borderRadius: 5,
                        border: 'none',
                        background: 'transparent',
                        fontSize: 12,
                        cursor: 'pointer',
                        color: '#374151',
                      }}
                    >
                      <span style={{
                        width: 6, height: 6, borderRadius: '50%', flexShrink: 0,
                        background: FLOW_COLORS[flow.type],
                      }} />
                      {flow.label}
                    </button>
                  ))}
                </div>
                <button
                  onClick={() => clearFlow(svgRef)}
                  style={{ marginTop: 8, fontSize: 11, color: '#c4c4c4', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
                >
                  clear
                </button>
              </div>
            )}

            <NodeSidebar
              node={selectedNode}
              explanation={explanation}
              loading={explanationLoading}
              onClose={handleSidebarClose}
            />

            {traversal.length > 0 && (() => {
              const traversalNodes = traversal
                .map((id) => graphData?.nodes.find((n) => n.id === id))
                .filter((n): n is NonNullable<typeof n> => !!n)
              return (
                <TraversalList
                  nodes={traversalNodes}
                  currentIndex={playStep}
                  onJumpTo={(i) => {
                    stopPlayback()
                    visitedRef.current = new Set(traversal.slice(0, i + 1))
                    setPlayStep(i)
                  }}
                />
              )
            })()}

            {traversal.length > 0 && (
              <PlayControls
                isPlaying={isPlaying}
                step={playStep}
                total={traversal.length}
                currentLabel={
                  (graphData?.nodes.find((n) => n.id === traversal[playStep])?.label) ?? ''
                }
                speed={playSpeed}
                onPlay={handlePlay}
                onPause={handlePause}
                onNext={handleNext}
                onReset={handlePlayReset}
                onSpeedChange={handleSpeedChange}
              />
            )}
          </div>
        )}
      </div>
    </div>
  )
}
