#!/usr/bin/env python3
"""
Visualization generator for Mike repository analysis.
Creates network graph visualization from JSON structure.
"""

import json
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
import sys


def load_visualization_data(json_path):
    """Load the visualization JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)


def create_graph(data):
    """Create a NetworkX directed graph from visualization data."""
    G = nx.DiGraph()

    # Add nodes with attributes
    for node in data['nodes']:
        G.add_node(
            node['id'],
            label=node['label'],
            type=node['type'],
            status=node.get('status', 'neutral'),
            full_title=node.get('full_title', node['label'])
        )

    # Add edges
    for link in data['links']:
        G.add_edge(link['source'], link['target'])

    return G


def get_node_colors(G):
    """Get color mapping for nodes based on status."""
    color_map = []
    status_colors = {
        'green': '#90EE90',
        'yellow': '#FFD700',
        'red': '#FF6B6B',
        'neutral': '#E0E0E0'
    }

    for node in G.nodes():
        status = G.nodes[node].get('status', 'neutral')
        color_map.append(status_colors.get(status, '#E0E0E0'))

    return color_map


def get_node_sizes(G):
    """Size nodes based on their type and degree."""
    size_map = []
    for node in G.nodes():
        node_type = G.nodes[node].get('type', 'finding')
        if node_type == 'repo':
            size = 3000
        elif node_type == 'phase':
            size = 2000
        else:  # finding
            size = 800 + (G.degree(node) * 300)
        size_map.append(size)

    return size_map


def visualize_hierarchical(G, output_path='mike_analysis_hierarchical.png'):
    """Create a hierarchical layout visualization."""
    plt.figure(figsize=(16, 12))

    # Use a spring layout with specific parameters for hierarchical appearance
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # Draw the network
    colors = get_node_colors(G)
    sizes = get_node_sizes(G)

    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='#666666', arrows=True,
                          arrowsize=15, arrowstyle='->', width=1.5,
                          connectionstyle='arc3,rad=0.1', alpha=0.6)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=sizes,
                          alpha=0.9, edgecolors='#333333', linewidths=2)

    # Draw labels
    labels = {node: G.nodes[node]['label'] for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')

    plt.title('Mike Repository Analysis - Hierarchical View\n(Green: Good, Yellow: Attention Needed, Red: Critical)',
              fontsize=14, fontweight='bold', pad=20)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Hierarchical visualization saved: {output_path}")

    return output_path


def visualize_tree(G, output_path='mike_analysis_tree.png'):
    """Create a tree layout visualization (more hierarchical)."""
    plt.figure(figsize=(18, 10))

    # Use a hierarchical tree layout
    pos = nx.nx_agraph.graphviz_layout(G, prog='dot') if nx.is_directed_acyclic_graph(G) else nx.spring_layout(G, k=3, iterations=50, seed=42)

    colors = get_node_colors(G)
    sizes = get_node_sizes(G)

    # Draw edges with better styling
    nx.draw_networkx_edges(G, pos, edge_color='#999999', arrows=True,
                          arrowsize=20, arrowstyle='->', width=2,
                          connectionstyle='arc3,rad=0.1', alpha=0.7)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=sizes,
                          alpha=0.95, edgecolors='#222222', linewidths=2.5)

    # Draw labels with better positioning
    labels = {node: G.nodes[node]['label'] for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=9, font_weight='bold', font_color='#000000')

    plt.title('Mike Repository Analysis - Tree Structure\n(Green: Good, Yellow: Attention Needed, Red: Critical)',
              fontsize=14, fontweight='bold', pad=20)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Tree visualization saved: {output_path}")

    return output_path


def print_graph_stats(G, data):
    """Print statistics about the graph."""
    print("\n" + "="*60)
    print("GRAPH STATISTICS")
    print("="*60)
    print(f"Total Nodes: {G.number_of_nodes()}")
    print(f"Total Edges: {G.number_of_edges()}")
    print(f"\nNode Types:")

    type_counts = {}
    for node in G.nodes():
        node_type = G.nodes[node].get('type', 'unknown')
        type_counts[node_type] = type_counts.get(node_type, 0) + 1

    for node_type, count in sorted(type_counts.items()):
        print(f"  - {node_type}: {count}")

    print(f"\nStatus Breakdown:")
    summary = data.get('summary', {})
    for status, count in summary.get('status_breakdown', {}).items():
        print(f"  - {status}: {count}")

    print(f"\nPhases:")
    for node in sorted(G.nodes()):
        if G.nodes[node].get('type') == 'phase':
            findings = list(G.successors(node))
            print(f"  - {G.nodes[node]['label']}: {len(findings)} findings")


def main(json_path=None, output_dir=None):
    """Main execution function."""
    if json_path is None:
        # Try to find the JSON file in common locations
        possible_paths = [
            Path('/Users/deantaylor_2026/Library/Application Support/Claude/local-agent-mode-sessions/116cc161-e181-40b7-a0d8-a8da90d2de66/258dc3c3-00fe-4e37-9889-5b19769e5304/local_33324a89-19e1-4726-b007-44d5a77dbb54/uploads/mike_visualization.json'),
            Path('./mike_visualization.json'),
            Path('./uploads/mike_visualization.json'),
        ]

        json_path = None
        for path in possible_paths:
            if path.exists():
                json_path = path
                break

        if json_path is None:
            print("Error: Could not find mike_visualization.json")
            print("Please provide path as argument: python visualize_mike_analysis.py <path_to_json>")
            sys.exit(1)

    json_path = Path(json_path)

    if not json_path.exists():
        print(f"Error: File not found: {json_path}")
        sys.exit(1)

    print(f"Loading visualization data from: {json_path}")
    data = load_visualization_data(json_path)

    print("Creating graph structure...")
    G = create_graph(data)

    # Print statistics
    print_graph_stats(G, data)

    # Create visualizations
    if output_dir is None:
        output_dir = json_path.parent
    else:
        output_dir = Path(output_dir)

    print(f"\nGenerating visualizations in: {output_dir}")

    try:
        visualize_hierarchical(G, output_dir / 'mike_analysis_hierarchical.png')
    except Exception as e:
        print(f"⚠ Hierarchical visualization skipped: {e}")

    try:
        # Try tree layout if pygraphviz is available, otherwise use spring layout
        if nx.is_directed_acyclic_graph(G):
            visualize_tree(G, output_dir / 'mike_analysis_tree.png')
        else:
            print("⚠ Tree layout skipped: Graph is not a DAG")
    except ImportError:
        print("⚠ Tree layout skipped: pygraphviz not installed")
    except Exception as e:
        print(f"⚠ Tree layout failed: {e}")

    print("\n✓ Visualization complete!")


if __name__ == '__main__':
    json_path = sys.argv[1] if len(sys.argv) > 1 else None
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    main(json_path, output_dir)
