import { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import type { GraphData, GraphNode, GraphEdge } from '../types/graph'
import { NODE_COLORS } from '../types/graph'

interface Props {
  data: GraphData
  svgRef: { current: SVGSVGElement | null }
  onNodeClick: (node: GraphNode) => void
}

export default function GraphView({ data, svgRef, onNodeClick }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return

    const { width, height } = containerRef.current.getBoundingClientRect()
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()
    svg.attr('width', width).attr('height', height)

    const g = svg.append('g')

    svg.call(
      d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.2, 4])
        .on('zoom', (event) => g.attr('transform', event.transform)),
    )

    // Deep-copy nodes and edges so D3 can mutate them freely
    const nodes: GraphNode[] = data.nodes.map((n) => ({ ...n }))
    const edges: GraphEdge[] = data.edges.map((e) => ({ ...e }))

    const simulation = d3
      .forceSimulation(nodes as d3.SimulationNodeDatum[])
      .force(
        'link',
        d3
          .forceLink(edges)
          .id((d) => (d as GraphNode).id)
          .distance(120),
      )
      .force('charge', d3.forceManyBody().strength(-350))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide(30))

    // Draw edges first (behind nodes)
    const link = g
      .append('g')
      .selectAll<SVGLineElement, GraphEdge>('line')
      .data(edges)
      .join('line')
      .attr('class', 'edge')
      .attr('stroke', '#d1d5db')
      .attr('stroke-width', 1)

    // Draw node groups
    const nodeGroup = g
      .append('g')
      .selectAll<SVGGElement, GraphNode>('g')
      .data(nodes)
      .join('g')
      .style('cursor', 'pointer')
      .call(
        d3
          .drag<SVGGElement, GraphNode>()
          .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart()
            d.fx = d.x
            d.fy = d.y
          })
          .on('drag', (event, d) => {
            d.fx = event.x
            d.fy = event.y
          })
          .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0)
            d.fx = null
            d.fy = null
          }),
      )
      .on('click', (event, d) => {
        event.stopPropagation()
        onNodeClick(d)
      })

    nodeGroup
      .append('circle')
      .attr('class', 'node')
      .attr('r', 12)
      .attr('fill', (d) => NODE_COLORS[d.type] ?? '#9ca3af')
      .attr('stroke', 'white')
      .attr('stroke-width', 2)

    nodeGroup
      .append('text')
      .text((d) => d.label)
      .attr('x', 16)
      .attr('y', 4)
      .attr('font-size', 11)
      .attr('font-family', 'system-ui, sans-serif')
      .attr('fill', '#374151')

    simulation.on('tick', () => {
      link
        .attr('x1', (d) => (d.source as GraphNode).x ?? 0)
        .attr('y1', (d) => (d.source as GraphNode).y ?? 0)
        .attr('x2', (d) => (d.target as GraphNode).x ?? 0)
        .attr('y2', (d) => (d.target as GraphNode).y ?? 0)

      nodeGroup.attr('transform', (d) => `translate(${d.x ?? 0},${d.y ?? 0})`)
    })

    return () => {
      simulation.stop()
    }
  }, [data, svgRef, onNodeClick])

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%' }}>
      <svg ref={svgRef} style={{ width: '100%', height: '100%' }} />
    </div>
  )
}
