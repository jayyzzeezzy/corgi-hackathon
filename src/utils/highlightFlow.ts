import * as d3 from 'd3'
import type { DataFlow, GraphEdge, GraphNode } from '../types/graph'
import { FLOW_COLORS } from '../types/graph'

const DEFAULT_EDGE_STROKE = '#dde1e8'
const DEFAULT_EDGE_WIDTH = 1
const DEFAULT_EDGE_OPACITY = 0.8

function getNodeId(d: string | GraphNode): string {
  return typeof d === 'object' ? d.id : d
}

function baseR(el: SVGCircleElement): number {
  return +(el.getAttribute('data-base-r') ?? 12)
}

export function highlightFlow(flow: DataFlow, svgRef: { current: SVGSVGElement | null }): void {
  if (!svgRef.current) return

  clearFlow(svgRef)

  const svg = d3.select(svgRef.current)
  const color = FLOW_COLORS[flow.type]

  const pairs = new Set(
    flow.path.slice(0, -1).map((_, i) => `${flow.path[i]}::${flow.path[i + 1]}`)
  )

  svg.selectAll<SVGLineElement, GraphEdge>('.edge').each(function (d) {
    const src = getNodeId(d.source)
    const tgt = getNodeId(d.target)
    if (pairs.has(`${src}::${tgt}`) || pairs.has(`${tgt}::${src}`)) {
      d3.select(this)
        .attr('stroke', color)
        .attr('stroke-width', 2.5)
        .attr('stroke-dasharray', '6 3')
    }
  })

  svg.selectAll<SVGCircleElement, GraphNode>('.node')
    .filter((d) => d.id === flow.origin)
    .each(function () {
      const r = baseR(this)
      d3.select(this)
        .transition().duration(200).attr('r', r + 8)
        .transition().duration(200).attr('r', r + 3)
        .transition().duration(150).attr('r', r + 5)
    })
}

export function highlightStep(
  nodeId: string,
  prevNodeId: string | null,
  visited: Set<string>,
  svgRef: { current: SVGSVGElement | null },
): void {
  if (!svgRef.current) return
  const svg = d3.select(svgRef.current)

  svg.selectAll<SVGCircleElement, GraphNode>('.node')
    .attr('fill', (d) => {
      if (d.id === nodeId) return '#111827'
      if (visited.has(d.id)) return '#94a3b8'
      return '#e4e4e7'
    })
    .attr('opacity', (d) => {
      if (d.id === nodeId) return 1
      if (visited.has(d.id)) return 0.8
      return 0.28
    })
    .each(function (d) {
      const r = baseR(this)
      d3.select(this).attr('r', d.id === nodeId ? r + 4 : r)
    })
    .attr('stroke', (d) => (d.id === nodeId ? '#374151' : 'white'))
    .attr('stroke-width', (d) => (d.id === nodeId ? 2.5 : 2))

  svg.selectAll<SVGLineElement, GraphEdge>('.edge').each(function (d) {
    const src = getNodeId(d.source)
    const tgt = getNodeId(d.target)
    const isActive = src === prevNodeId && tgt === nodeId
    const isVisited = visited.has(src) && visited.has(tgt)

    d3.select(this)
      .attr('stroke', isActive ? '#334155' : isVisited ? '#94a3b8' : '#e4e4e7')
      .attr('stroke-width', isActive ? 2 : 1)
      .attr('opacity', isActive ? 1 : isVisited ? 0.55 : 0.1)
  })
}

export function clearFlow(svgRef: { current: SVGSVGElement | null }): void {
  if (!svgRef.current) return
  const svg = d3.select(svgRef.current)

  svg.selectAll('.edge')
    .attr('stroke', DEFAULT_EDGE_STROKE)
    .attr('stroke-width', DEFAULT_EDGE_WIDTH)
    .attr('stroke-dasharray', null)
    .attr('opacity', DEFAULT_EDGE_OPACITY)

  svg.selectAll<SVGCircleElement, GraphNode>('.node')
    .transition().duration(150)
    .attr('r', function () { return baseR(this) })
    .attr('opacity', 1)
}
