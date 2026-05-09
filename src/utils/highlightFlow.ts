import * as d3 from 'd3'
import type { DataFlow, GraphEdge, GraphNode } from '../types/graph'
import { FLOW_COLORS } from '../types/graph'

const DEFAULT_EDGE_STROKE = '#d1d5db'
const DEFAULT_EDGE_WIDTH = 1
const DEFAULT_NODE_RADIUS = 12

function getNodeId(d: string | GraphNode): string {
  return typeof d === 'object' ? d.id : d
}

/**
 * Highlights edges connecting consecutive nodes in flow.path and pulses the origin node.
 * Call clearFlow() first if you want to reset any previous highlight.
 *
 * How the UI team should call this:
 *   highlightFlow(selectedFlow, svgRef)
 *
 * svgRef is a React.RefObject<SVGSVGElement> passed into GraphView.
 */
export function highlightFlow(flow: DataFlow, svgRef: { current: SVGSVGElement | null }): void {
  if (!svgRef.current) return

  clearFlow(svgRef)

  const svg = d3.select(svgRef.current)
  const color = FLOW_COLORS[flow.type]

  // Build set of directed and undirected edge pairs from the flow path
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

  // Pulse the origin node: grow then settle slightly larger to keep it visible
  svg
    .selectAll<SVGCircleElement, GraphNode>('.node')
    .filter((d) => d.id === flow.origin)
    .transition().duration(200)
    .attr('r', 20)
    .transition().duration(200)
    .attr('r', 16)
    .transition().duration(150)
    .attr('r', 18)
}

/**
 * Resets all edges and nodes to their default D3 styles.
 *
 * How the UI team should call this:
 *   clearFlow(svgRef)
 */
export function clearFlow(svgRef: { current: SVGSVGElement | null }): void {
  if (!svgRef.current) return

  const svg = d3.select(svgRef.current)

  svg
    .selectAll('.edge')
    .attr('stroke', DEFAULT_EDGE_STROKE)
    .attr('stroke-width', DEFAULT_EDGE_WIDTH)
    .attr('stroke-dasharray', null)

  svg
    .selectAll<SVGCircleElement, GraphNode>('.node')
    .transition().duration(150)
    .attr('r', DEFAULT_NODE_RADIUS)
}
