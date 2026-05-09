import type { GraphData, GraphNode, GraphEdge, NodeType } from '../types/graph'

export interface RepoGraphResult {
  graph: GraphData
  paths: string[]
  repoName: string
}

const CODE_EXTENSIONS = new Set(['.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.py'])

function getExtension(path: string): string {
  const dot = path.lastIndexOf('.')
  return dot === -1 ? '' : path.slice(dot)
}

function inferNodeType(path: string): NodeType {
  const filename = path.split('/').pop() ?? ''
  const ext = getExtension(filename)
  if (/^use[A-Z]/.test(filename)) return 'hook'
  if (ext === '.tsx' || ext === '.jsx') return 'component'
  if (/\/(utils?|helpers?|lib)\//i.test(path)) return 'util'
  if (/\/(services?|api|store|hooks)\//i.test(path)) return 'util'
  if (/\.(py)$/.test(ext)) return 'class'
  return 'function'
}

function resolveImport(fromDir: string, importPath: string, allPaths: string[]): string | null {
  const parts = (fromDir + '/' + importPath).split('/')
  const resolved: string[] = []
  for (const part of parts) {
    if (part === '..') resolved.pop()
    else if (part !== '.') resolved.push(part)
  }
  const base = resolved.join('/')

  const candidates = [
    base,
    `${base}.ts`, `${base}.tsx`, `${base}.js`, `${base}.jsx`, `${base}.py`,
    `${base}/index.ts`, `${base}/index.tsx`, `${base}/index.js`,
  ]
  return candidates.find((c) => allPaths.includes(c)) ?? null
}

function parseImports(content: string, filePath: string, allPaths: string[]): string[] {
  const dir = filePath.split('/').slice(0, -1).join('/')
  const deps = new Set<string>()

  // JS/TS: import X from './path' | import './path' | export { X } from './path'
  const jsPattern = /(?:from|import)\s+['"]([^'"]+)['"]/g
  let match
  while ((match = jsPattern.exec(content)) !== null) {
    const imp = match[1]
    if (!imp.startsWith('.')) continue
    const resolved = resolveImport(dir, imp, allPaths)
    if (resolved && resolved !== filePath) deps.add(resolved)
  }

  // Python: from .module import X
  const pyPattern = /^from\s+(\.+\S*)\s+import/gm
  while ((match = pyPattern.exec(content)) !== null) {
    const imp = match[1].replace(/^\./, './')
    const resolved = resolveImport(dir, imp, allPaths)
    if (resolved && resolved !== filePath) deps.add(resolved)
  }

  return [...deps]
}

export async function fetchRepoGraph(repoUrl: string): Promise<RepoGraphResult> {
  const match = repoUrl.match(/github\.com\/([^/]+)\/([^/?\s]+?)(?:\.git|\/|$)/)
  if (!match) throw new Error('Invalid GitHub repo URL — expected github.com/user/repo')
  const [, owner, repo] = match

  // Get default branch
  const repoRes = await fetch(`https://api.github.com/repos/${owner}/${repo}`)
  if (repoRes.status === 404) throw new Error('Repo not found — make sure it\'s public')
  if (!repoRes.ok) throw new Error(`GitHub API error (${repoRes.status})`)
  const repoData = await repoRes.json()
  const branch: string = repoData.default_branch

  // Get full file tree
  const treeRes = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/git/trees/${branch}?recursive=1`,
  )
  if (!treeRes.ok) throw new Error(`Failed to fetch file tree (${treeRes.status})`)
  const treeData = await treeRes.json()

  if (treeData.truncated) console.warn('[github] Tree was truncated — very large repo')

  // Filter to code files, exclude noise
  const codeFiles: { path: string }[] = (treeData.tree as { path: string; type: string }[])
    .filter(
      (item) =>
        item.type === 'blob' &&
        CODE_EXTENSIONS.has(getExtension(item.path)) &&
        !item.path.includes('node_modules') &&
        !item.path.endsWith('.d.ts') &&
        !item.path.includes('__tests__') &&
        !item.path.includes('.test.') &&
        !item.path.includes('.spec.') &&
        !item.path.includes('.config.'),
    )
    // Prefer shallower paths (closer to root = more central files)
    .sort((a, b) => a.path.split('/').length - b.path.split('/').length)
    .slice(0, 60)

  const allPaths = codeFiles.map((f) => f.path)

  // Fetch all file contents in parallel
  const contents = await Promise.all(
    codeFiles.map(async (file) => {
      const res = await fetch(
        `https://raw.githubusercontent.com/${owner}/${repo}/${branch}/${file.path}`,
      )
      return res.ok ? res.text() : Promise.resolve(null)
    }),
  )

  // Build graph
  const nodes: GraphNode[] = []
  const edgeSet = new Set<string>()
  const edges: GraphEdge[] = []

  codeFiles.forEach((file, i) => {
    const content = contents[i]
    if (!content) return

    const filename = file.path.split('/').pop() ?? file.path
    nodes.push({
      id: file.path,
      label: filename,
      type: inferNodeType(file.path),
      description: file.path,
    })

    const deps = parseImports(content, file.path, allPaths)
    for (const dep of deps) {
      const key = `${file.path}→${dep}`
      if (!edgeSet.has(key)) {
        edgeSet.add(key)
        edges.push({ source: file.path, target: dep, relationship: 'imports' })
      }
    }
  })

  // Drop nodes with no connections to reduce clutter
  const connected = new Set(edges.flatMap((e) => [e.source as string, e.target as string]))
  const filteredNodes = nodes.filter((n) => connected.has(n.id))

  return {
    graph: { nodes: filteredNodes, edges, dataFlows: [] },
    paths: allPaths,
    repoName: repo,
  }
}
