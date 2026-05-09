import { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import type { GraphData, GraphNode, GraphEdge } from '../types/graph'
import { NODE_COLORS } from '../types/graph'

interface Props {
  data: GraphData
  svgRef: { current: SVGSVGElement | null }
  onNodeClick: (node: GraphNode) => void
}

const BASE_R = 9
const MAX_R = 18

function getDegree(data: GraphData): Map<string, number> {
  const deg = new Map<string, number>()
  for (const n of data.nodes) deg.set(n.id, 0)
  for (const e of data.edges) {
    const src = typeof e.source === 'string' ? e.source : (e.source as GraphNode).id
    const tgt = typeof e.target === 'string' ? e.target : (e.target as GraphNode).id
    deg.set(src, (deg.get(src) ?? 0) + 1)
    deg.set(tgt, (deg.get(tgt) ?? 0) + 1)
  }
  return deg
}

export default function GraphView({ data, svgRef, onNodeClick }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return

    const { width, height } = containerRef.current.getBoundingClientRect()
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()
    svg.attr('width', width).attr('height', height)

    const degree = getDegree(data)
    const maxDeg = Math.max(...degree.values(), 1)
    const nodeR = (d: GraphNode) => BASE_R + ((degree.get(d.id) ?? 0) / maxDeg) * (MAX_R - BASE_R)

    // Arrowhead
    svg.append('defs').append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 0 10 10')
      .attr('refX', 10).attr('refY', 5)
      .attr('markerWidth', 5).attr('markerHeight', 5)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M 0 0 L 10 5 L 0 10 z')
      .attr('fill', '#c8cdd6')

    const zoomBehavior = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.08, 4])
      .on('zoom', (event) => g.attr('transform', event.transform))

    svg.call(zoomBehavior)

    const g = svg.append('g')

    // Spread nodes in a circle initially — prevents the center-cluster problem
    const nodes: GraphNode[] = data.nodes.map((n, i) => {
      const angle = (2 * Math.PI * i) / data.nodes.length
      const r = Math.min(width, height) * 0.32
      return { ...n, x: width / 2 + r * Math.cos(angle), y: height / 2 + r * Math.sin(angle) }
    })
    const edges: GraphEdge[] = data.edges.map((e) => ({ ...e }))

    const PAD = 56
    const simulation = d3
      .forceSimulation(nodes as d3.SimulationNodeDatum[])
      .force(
        'link',
        d3.forceLink(edges).id((d) => (d as GraphNode).id).distance(160).strength(0.45),
      )
      .force('charge', d3.forceManyBody().strength(-600))
      .force('center', d3.forceCenter(width / 2, height / 2).strength(0.06))
      .force('collision', d3.forceCollide((d) => nodeR(d as GraphNode) + 28))
      .force('bounds', () => {
        for (const n of nodes) {
          const r = nodeR(n)
          n.x = Math.max(PAD + r, Math.min(width - PAD - r, n.x ?? width / 2))
          n.y = Math.max(PAD + r, Math.min(height - PAD - r, n.y ?? height / 2))
        }
      })
      .alphaDecay(0.025)

    // Edges
    const link = g.append('g')
      .selectAll<SVGLineElement, GraphEdge>('line')
      .data(edges)
      .join('line')
      .attr('class', 'edge')
      .attr('stroke', '#dde1e8')
      .attr('stroke-width', 1)
      .attr('opacity', 0.8)
      .attr('marker-end', 'url(#arrow)')

    // Node groups
    const nodeGroup = g.append('g')
      .selectAll<SVGGElement, GraphNode>('g')
      .data(nodes)
      .join('g')
      .style('cursor', 'pointer')
      .call(
        d3.drag<SVGGElement, GraphNode>()
          .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart()
            d.fx = d.x; d.fy = d.y
          })
          .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y })
          .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0)
            d.fx = null; d.fy = null
          }),
      )
      .on('click', (event, d) => {
        event.stopPropagation()
        onNodeClick(d)
      })

    nodeGroup.append('circle')
      .attr('class', 'node')
      .attr('r', (d) => nodeR(d))
      .attr('data-base-r', (d) => nodeR(d))
      .attr('fill', (d) => NODE_COLORS[d.type] ?? '#94a3b8')
      .attr('stroke', 'white')
      .attr('stroke-width', 2)

    nodeGroup.append('text')
      .text((d) => d.label.length > 22 ? d.label.slice(0, 20) + '…' : d.label)
      .attr('x', (d) => nodeR(d) + 5)
      .attr('y', 4)
      .attr('font-size', 11)
      .attr('font-family', 'Inter, system-ui, sans-serif')
      .attr('fill', '#1a1a1a')
      .attr('pointer-events', 'none')

    simulation.on('tick', () => {
      link
        .attr('x1', (d) => (d.source as GraphNode).x ?? 0)
        .attr('y1', (d) => (d.source as GraphNode).y ?? 0)
        .attr('x2', (d) => {
          const s = d.source as GraphNode, t = d.target as GraphNode
          const dx = (t.x ?? 0) - (s.x ?? 0), dy = (t.y ?? 0) - (s.y ?? 0)
          const dist = Math.sqrt(dx * dx + dy * dy)
          const offset = nodeR(t) + 2
          return dist ? (t.x ?? 0) - (dx / dist) * offset : (t.x ?? 0)
        })
        .attr('y2', (d) => {
          const s = d.source as GraphNode, t = d.target as GraphNode
          const dx = (t.x ?? 0) - (s.x ?? 0), dy = (t.y ?? 0) - (s.y ?? 0)
          const dist = Math.sqrt(dx * dx + dy * dy)
          const offset = nodeR(t) + 2
          return dist ? (t.y ?? 0) - (dy / dist) * offset : (t.y ?? 0)
        })

      nodeGroup.attr('transform', (d) => `translate(${d.x ?? 0},${d.y ?? 0})`)
    })

    // Auto-fit when the simulation settles
    simulation.on('end', () => {
      const xs = nodes.map((n) => n.x ?? 0)
      const ys = nodes.map((n) => n.y ?? 0)
      const x0 = Math.min(...xs) - 72, x1 = Math.max(...xs) + 140
      const y0 = Math.min(...ys) - 56, y1 = Math.max(...ys) + 56
      const scale = Math.min(width / (x1 - x0), height / (y1 - y0), 1.4)
      const tx = (width - scale * (x0 + x1)) / 2
      const ty = (height - scale * (y0 + y1)) / 2
      svg.transition().duration(700).ease(d3.easeCubicOut).call(
        zoomBehavior.transform,
        d3.zoomIdentity.translate(tx, ty).scale(scale),
      )
    })

    return () => { simulation.stop() }
  }, [data, svgRef, onNodeClick])

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%' }}>
      <svg ref={svgRef} style={{ width: '100%', height: '100%' }} />
    </div>
  )
}
