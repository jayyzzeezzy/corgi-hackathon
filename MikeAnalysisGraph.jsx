import React, { useState, useEffect, useRef } from 'react';

const MikeAnalysisGraph = () => {
  const canvasRef = useRef(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [simulationRunning, setSimulationRunning] = useState(true);
  const [zoom, setZoom] = useState(1);

  // Sample data - in production, this would be loaded from JSON
  const data = {
    nodes: [
      { id: "repo", label: "willchen96/mike", type: "repo", status: "neutral" },
      { id: "1_Understanding", label: "1: Understanding", type: "phase", status: "neutral" },
      { id: "finding_0", label: "File inventory complete", type: "finding", status: "green" },
      { id: "finding_1", label: "No formal dependency file found", type: "finding", status: "yellow" },
      { id: "finding_2", label: "Core functionality mapped", type: "finding", status: "green" },
      { id: "2_Structural", label: "2: Structural", type: "phase", status: "neutral" },
      { id: "finding_3", label: "Source/test organization could be clearer", type: "finding", status: "yellow" },
      { id: "3_Quality", label: "3: Quality", type: "phase", status: "neutral" },
      { id: "finding_4", label: "Documentation present (README)", type: "finding", status: "green" },
      { id: "finding_5", label: "No code style configuration found", type: "finding", status: "yellow" },
      { id: "finding_6", label: "No testing configuration found", type: "finding", status: "red" },
      { id: "finding_7", label: "Large source files detected (1 files > 10KB)", type: "finding", status: "yellow" },
      { id: "4_Security", label: "4: Security", type: "phase", status: "neutral" },
      { id: "finding_8", label: "No environment configuration pattern detected", type: "finding", status: "yellow" },
      { id: "finding_9", label: ".gitignore configured", type: "finding", status: "green" },
      { id: "finding_10", label: "No automated security scanning detected", type: "finding", status: "yellow" }
    ],
    links: [
      { source: "repo", target: "1_Understanding" },
      { source: "1_Understanding", target: "finding_0" },
      { source: "1_Understanding", target: "finding_1" },
      { source: "1_Understanding", target: "finding_2" },
      { source: "repo", target: "2_Structural" },
      { source: "2_Structural", target: "finding_3" },
      { source: "repo", target: "3_Quality" },
      { source: "3_Quality", target: "finding_4" },
      { source: "3_Quality", target: "finding_5" },
      { source: "3_Quality", target: "finding_6" },
      { source: "3_Quality", target: "finding_7" },
      { source: "repo", target: "4_Security" },
      { source: "4_Security", target: "finding_8" },
      { source: "4_Security", target: "finding_9" },
      { source: "4_Security", target: "finding_10" }
    ]
  };

  const statusColors = {
    green: '#90EE90',
    yellow: '#FFD700',
    red: '#FF6B6B',
    neutral: '#E0E0E0'
  };

  const nodeRadius = {
    repo: 25,
    phase: 20,
    finding: 12
  };

  // Force-directed graph simulation
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Initialize node positions
    const nodes = data.nodes.map((node, i) => ({
      ...node,
      x: width / 2 + (Math.random() - 0.5) * 200,
      y: height / 2 + (Math.random() - 0.5) * 200,
      vx: 0,
      vy: 0
    }));

    // Physics simulation
    const simulate = () => {
      if (!simulationRunning) return;

      // Apply forces
      for (let i = 0; i < nodes.length; i++) {
        let fx = 0, fy = 0;

        // Repulsive forces between all nodes
        for (let j = 0; j < nodes.length; j++) {
          if (i !== j) {
            const dx = nodes[j].x - nodes[i].x;
            const dy = nodes[j].y - nodes[i].y;
            const dist = Math.sqrt(dx * dx + dy * dy) + 1;
            const repulsion = 5000 / (dist * dist);
            fx -= (dx / dist) * repulsion;
            fy -= (dy / dist) * repulsion;
          }
        }

        // Attractive forces along edges
        data.links.forEach(link => {
          const source = nodes.find(n => n.id === link.source);
          const target = nodes.find(n => n.id === link.target);

          if ((source.id === nodes[i].id || target.id === nodes[i].id)) {
            const other = source.id === nodes[i].id ? target : source;
            const dx = other.x - nodes[i].x;
            const dy = other.y - nodes[i].y;
            const dist = Math.sqrt(dx * dx + dy * dy) + 1;
            const attraction = dist * 0.1;
            fx += (dx / dist) * attraction;
            fy += (dy / dist) * attraction;
          }
        });

        // Apply damping and update velocity
        nodes[i].vx = (nodes[i].vx + fx * 0.01) * 0.95;
        nodes[i].vy = (nodes[i].vy + fy * 0.01) * 0.95;

        // Update position
        nodes[i].x += nodes[i].vx;
        nodes[i].y += nodes[i].vy;

        // Boundary constraints
        nodes[i].x = Math.max(40, Math.min(width - 40, nodes[i].x));
        nodes[i].y = Math.max(40, Math.min(height - 40, nodes[i].y));
      }

      // Clear canvas
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, width, height);

      // Draw edges
      ctx.strokeStyle = '#99999988';
      ctx.lineWidth = 2;
      data.links.forEach(link => {
        const source = nodes.find(n => n.id === link.source);
        const target = nodes.find(n => n.id === link.target);

        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.stroke();

        // Draw arrowhead
        const angle = Math.atan2(target.y - source.y, target.x - source.x);
        const arrowSize = 8;
        ctx.fillStyle = '#999999';
        ctx.beginPath();
        ctx.moveTo(target.x, target.y);
        ctx.lineTo(target.x - arrowSize * Math.cos(angle - Math.PI / 6), target.y - arrowSize * Math.sin(angle - Math.PI / 6));
        ctx.lineTo(target.x - arrowSize * Math.cos(angle + Math.PI / 6), target.y - arrowSize * Math.sin(angle + Math.PI / 6));
        ctx.fill();
      });

      // Draw nodes
      nodes.forEach(node => {
        const radius = nodeRadius[node.type] || 12;
        const isHovered = hoveredNode === node.id;
        const isSelected = selectedNode === node.id;

        // Node circle
        ctx.fillStyle = statusColors[node.status] || '#E0E0E0';
        ctx.beginPath();
        ctx.arc(node.x, node.y, radius + (isHovered ? 4 : 0) + (isSelected ? 6 : 0), 0, Math.PI * 2);
        ctx.fill();

        // Node border
        ctx.strokeStyle = isSelected ? '#0066cc' : '#333333';
        ctx.lineWidth = isSelected ? 3 : 2;
        ctx.stroke();
      });

      // Draw labels for visible nodes
      ctx.fillStyle = '#000000';
      ctx.font = '11px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      nodes.forEach(node => {
        const label = node.label.substring(0, 20);
        ctx.fillText(label, node.x, node.y);
      });

      requestAnimationFrame(simulate);
    };

    simulate();
  }, [hoveredNode, selectedNode, simulationRunning]);

  const handleCanvasClick = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    for (const node of data.nodes) {
      const dx = node.x - x;
      const dy = node.y - y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const radius = nodeRadius[node.type] || 12;

      if (dist < radius + 5) {
        setSelectedNode(selectedNode === node.id ? null : node.id);
        return;
      }
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      <div style={{ marginBottom: '15px' }}>
        <h2>📊 Mike Repository Analysis Graph</h2>
        <p style={{ color: '#666', marginBottom: '10px' }}>
          Interactive force-directed graph showing repository analysis findings organized by phase.
        </p>

        <div style={{ display: 'flex', gap: '10px', marginBottom: '10px', flexWrap: 'wrap' }}>
          <button
            onClick={() => setSimulationRunning(!simulationRunning)}
            style={{
              padding: '8px 12px',
              backgroundColor: simulationRunning ? '#4CAF50' : '#999',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            {simulationRunning ? '⏸ Pause' : '▶ Play'}
          </button>

          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span style={{ fontSize: '12px' }}>Legend:</span>
            <span style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
              <span style={{ width: '12px', height: '12px', backgroundColor: '#90EE90', borderRadius: '2px' }} />
              <span style={{ fontSize: '12px' }}>Good</span>
            </span>
            <span style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
              <span style={{ width: '12px', height: '12px', backgroundColor: '#FFD700', borderRadius: '2px' }} />
              <span style={{ fontSize: '12px' }}>Attention</span>
            </span>
            <span style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
              <span style={{ width: '12px', height: '12px', backgroundColor: '#FF6B6B', borderRadius: '2px' }} />
              <span style={{ fontSize: '12px' }}>Critical</span>
            </span>
          </div>
        </div>
      </div>

      <canvas
        ref={canvasRef}
        width={800}
        height={600}
        onClick={handleCanvasClick}
        onMouseMove={(e) => {
          const canvas = canvasRef.current;
          const rect = canvas.getBoundingClientRect();
          const x = e.clientX - rect.left;
          const y = e.clientY - rect.top;

          let hoveredId = null;
          for (const node of data.nodes) {
            const dx = node.x - x;
            const dy = node.y - y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            const radius = nodeRadius[node.type] || 12;

            if (dist < radius + 5) {
              hoveredId = node.id;
              break;
            }
          }

          setHoveredNode(hoveredId);
          canvas.style.cursor = hoveredId ? 'pointer' : 'default';
        }}
        onMouseLeave={() => setHoveredNode(null)}
        style={{
          border: '1px solid #ddd',
          borderRadius: '4px',
          backgroundColor: '#ffffff',
          cursor: 'default'
        }}
      />

      {selectedNode && (
        <div style={{
          marginTop: '15px',
          padding: '12px',
          backgroundColor: '#f5f5f5',
          borderRadius: '4px',
          borderLeft: '4px solid #0066cc'
        }}>
          {(() => {
            const node = data.nodes.find(n => n.id === selectedNode);
            return (
              <>
                <h3 style={{ margin: '0 0 8px 0' }}>{node.label}</h3>
                <p style={{ margin: '0 0 4px 0', color: '#666', fontSize: '12px' }}>
                  <strong>Type:</strong> {node.type}
                </p>
                <p style={{ margin: '0 0 4px 0', color: '#666', fontSize: '12px' }}>
                  <strong>Status:</strong> <span style={{
                    display: 'inline-block',
                    width: '12px',
                    height: '12px',
                    backgroundColor: statusColors[node.status],
                    borderRadius: '2px',
                    marginRight: '4px'
                  }} /> {node.status}
                </p>
                <p style={{ margin: '0', color: '#666', fontSize: '12px' }}>
                  Click another node or elsewhere to deselect.
                </p>
              </>
            );
          })()}
        </div>
      )}

      <div style={{ marginTop: '15px', fontSize: '12px', color: '#999' }}>
        <p>
          <strong>How to use:</strong> Hover over nodes to highlight them. Click to select and see details.
          The graph uses forces to organize nodes: repulsion keeps them apart, while edge forces keep connected
          nodes together.
        </p>
      </div>
    </div>
  );
};

export default MikeAnalysisGraph;
