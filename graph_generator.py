#!/usr/bin/env python3
"""
Graph Generator Utility
Converts JSON visualization data to multiple graph formats.
Flexible enough to work with any graph structure.
"""

import json
from pathlib import Path
import csv
from typing import Dict, List, Any, Optional
import sys


class GraphGenerator:
    """Generate various graph visualizations from JSON data."""

    def __init__(self, json_data: Dict[str, Any]):
        """Initialize with visualization JSON data."""
        self.data = json_data
        self.nodes = {node['id']: node for node in json_data.get('nodes', [])}
        self.links = json_data.get('links', [])
        self.summary = json_data.get('summary', {})

    def to_csv(self, output_path: Path) -> Path:
        """Export graph as CSV with node and edge information."""
        output_path = Path(output_path)

        # Write nodes CSV
        nodes_csv = output_path.parent / f"{output_path.stem}_nodes.csv"
        with open(nodes_csv, 'w', newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['id', 'label', 'type', 'status', 'in_degree', 'out_degree']
            )
            writer.writeheader()

            for node_id, node in self.nodes.items():
                in_degree = sum(1 for link in self.links if link['target'] == node_id)
                out_degree = sum(1 for link in self.links if link['source'] == node_id)

                writer.writerow({
                    'id': node_id,
                    'label': node.get('label', ''),
                    'type': node.get('type', ''),
                    'status': node.get('status', ''),
                    'in_degree': in_degree,
                    'out_degree': out_degree
                })

        # Write edges CSV
        edges_csv = output_path.parent / f"{output_path.stem}_edges.csv"
        with open(edges_csv, 'w', newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['source', 'target', 'source_type', 'target_type']
            )
            writer.writeheader()

            for link in self.links:
                source_node = self.nodes.get(link['source'], {})
                target_node = self.nodes.get(link['target'], {})

                writer.writerow({
                    'source': link['source'],
                    'target': link['target'],
                    'source_type': source_node.get('type', ''),
                    'target_type': target_node.get('type', '')
                })

        return nodes_csv, edges_csv

    def to_graphml(self, output_path: Path) -> Path:
        """Export as GraphML format (compatible with Gephi, yEd, etc.)."""
        output_path = Path(output_path)

        graphml = '''<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
                           http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <key id="label" for="node" attr.name="label" attr.type="string"/>
  <key id="type" for="node" attr.name="type" attr.type="string"/>
  <key id="status" for="node" attr.name="status" attr.type="string"/>

  <graph id="G" edgedefault="directed">
'''

        # Add nodes
        for node_id, node in self.nodes.items():
            graphml += f'''    <node id="{node_id}">
      <data key="label">{node.get('label', '')}</data>
      <data key="type">{node.get('type', '')}</data>
      <data key="status">{node.get('status', '')}</data>
    </node>
'''

        # Add edges
        for i, link in enumerate(self.links):
            graphml += f'''    <edge id="e{i}" source="{link['source']}" target="{link['target']}"/>
'''

        graphml += '''  </graph>
</graphml>'''

        with open(output_path, 'w') as f:
            f.write(graphml)

        return output_path

    def to_json_adjacency(self, output_path: Path) -> Path:
        """Export as adjacency list JSON format."""
        output_path = Path(output_path)

        adjacency = {}
        for node_id in self.nodes:
            adjacency[node_id] = {
                'node': self.nodes[node_id],
                'outgoing': [],
                'incoming': []
            }

        for link in self.links:
            adjacency[link['source']]['outgoing'].append(link['target'])
            adjacency[link['target']]['incoming'].append(link['source'])

        with open(output_path, 'w') as f:
            json.dump(adjacency, f, indent=2)

        return output_path

    def to_summary_text(self, output_path: Path) -> Path:
        """Generate a text summary of the graph."""
        output_path = Path(output_path)

        summary_text = "GRAPH SUMMARY\n"
        summary_text += "=" * 60 + "\n\n"

        summary_text += f"Total Nodes: {len(self.nodes)}\n"
        summary_text += f"Total Edges: {len(self.links)}\n\n"

        # Node types
        type_counts = {}
        for node in self.nodes.values():
            node_type = node.get('type', 'unknown')
            type_counts[node_type] = type_counts.get(node_type, 0) + 1

        summary_text += "Node Types:\n"
        for node_type, count in sorted(type_counts.items()):
            summary_text += f"  - {node_type}: {count}\n"

        # Node statuses
        status_counts = {}
        for node in self.nodes.values():
            status = node.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        summary_text += "\nNode Statuses:\n"
        for status, count in sorted(status_counts.items()):
            summary_text += f"  - {status}: {count}\n"

        # Top nodes by degree
        degrees = {}
        for node_id in self.nodes:
            in_degree = sum(1 for link in self.links if link['target'] == node_id)
            out_degree = sum(1 for link in self.links if link['source'] == node_id)
            degrees[node_id] = in_degree + out_degree

        summary_text += "\nTop 10 Connected Nodes:\n"
        for node_id, degree in sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]:
            node = self.nodes[node_id]
            summary_text += f"  - {node.get('label', node_id)}: {degree} connections\n"

        with open(output_path, 'w') as f:
            f.write(summary_text)

        return output_path

    def generate_all(self, output_dir: Optional[Path] = None, base_name: str = 'graph') -> Dict[str, Path]:
        """Generate all available formats."""
        if output_dir is None:
            output_dir = Path.cwd()

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        try:
            nodes_csv, edges_csv = self.to_csv(output_dir / base_name)
            results['nodes_csv'] = nodes_csv
            results['edges_csv'] = edges_csv
            print(f"✓ CSV export: {nodes_csv.name}, {edges_csv.name}")
        except Exception as e:
            print(f"✗ CSV export failed: {e}")

        try:
            graphml_path = self.to_graphml(output_dir / f"{base_name}.graphml")
            results['graphml'] = graphml_path
            print(f"✓ GraphML export: {graphml_path.name}")
        except Exception as e:
            print(f"✗ GraphML export failed: {e}")

        try:
            adj_path = self.to_json_adjacency(output_dir / f"{base_name}_adjacency.json")
            results['adjacency_json'] = adj_path
            print(f"✓ Adjacency JSON: {adj_path.name}")
        except Exception as e:
            print(f"✗ Adjacency JSON failed: {e}")

        try:
            summary_path = self.to_summary_text(output_dir / f"{base_name}_summary.txt")
            results['summary'] = summary_path
            print(f"✓ Summary text: {summary_path.name}")
        except Exception as e:
            print(f"✗ Summary text failed: {e}")

        return results


def main(json_path: Optional[str] = None, output_dir: Optional[str] = None):
    """Main entry point."""
    if json_path is None:
        # Find JSON in common locations
        possible_paths = [
            Path('/Users/deantaylor_2026/Library/Application Support/Claude/local-agent-mode-sessions/116cc161-e181-40b7-a0d8-a8da90d2de66/258dc3c3-00fe-4e37-9889-5b19769e5304/local_33324a89-19e1-4726-b007-44d5a77dbb54/uploads/mike_visualization.json'),
            Path('./mike_visualization.json'),
        ]

        json_path = None
        for path in possible_paths:
            if path.exists():
                json_path = path
                break

        if json_path is None:
            print("Usage: python graph_generator.py <path_to_json> [output_dir]")
            sys.exit(1)

    json_path = Path(json_path)
    if not json_path.exists():
        print(f"Error: File not found: {json_path}")
        sys.exit(1)

    print(f"Loading: {json_path}")
    with open(json_path, 'r') as f:
        data = json.load(f)

    generator = GraphGenerator(data)

    # Use provided output_dir or fall back to current directory
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)

    base_name = json_path.stem

    print(f"\nGenerating graph files in: {output_dir}\n")
    results = generator.generate_all(output_dir, base_name)

    print(f"\n✓ Complete! Generated {len(results)} files")


if __name__ == '__main__':
    json_path = sys.argv[1] if len(sys.argv) > 1 else None
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    main(json_path, output_dir)
