import type { GraphData } from '../types/graph'

export function computeTraversal(data: GraphData): string[] {
  const incomingCount = new Map<string, number>()
  data.nodes.forEach((n) => incomingCount.set(n.id, 0))

  // Build adjacency list and count incoming edges
  const adj = new Map<string, string[]>()
  for (const edge of data.edges) {
    const src = typeof edge.source === 'string' ? edge.source : edge.source.id
    const tgt = typeof edge.target === 'string' ? edge.target : edge.target.id
    if (!adj.has(src)) adj.set(src, [])
    adj.get(src)!.push(tgt)
    incomingCount.set(tgt, (incomingCount.get(tgt) ?? 0) + 1)
  }

  // Root nodes: no incoming edges — prefer files named index/main/app
  const isEntryName = (id: string) => /(?:^|\/)(?:index|main|app)\.[^/]+$/i.test(id)
  const roots = data.nodes
    .filter((n) => (incomingCount.get(n.id) ?? 0) === 0)
    .sort((a, b) => (isEntryName(b.id) ? 1 : 0) - (isEntryName(a.id) ? 1 : 0))

  const startIds = roots.length > 0 ? roots.map((n) => n.id) : [data.nodes[0]?.id].filter(Boolean)

  // BFS
  const visited = new Set<string>()
  const queue = [...startIds]
  const order: string[] = []

  while (queue.length > 0) {
    const id = queue.shift()!
    if (visited.has(id)) continue
    visited.add(id)
    order.push(id)
    for (const neighbor of adj.get(id) ?? []) {
      if (!visited.has(neighbor)) queue.push(neighbor)
    }
  }

  // Append any isolated nodes at the end
  for (const node of data.nodes) {
    if (!visited.has(node.id)) order.push(node.id)
  }

  return order
}
