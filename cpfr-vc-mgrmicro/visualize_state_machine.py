"""
State Machine Visualizer for CPFR VC App
Generates visual diagrams of the state machine from the JSON schema

Requirements:
    pip install graphviz matplotlib networkx
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Try different visualization libraries
try:
    import graphviz
    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False
    print("Warning: graphviz not installed. Install with: pip install graphviz")

try:
    import matplotlib.pyplot as plt
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("Warning: networkx/matplotlib not installed. Install with: pip install networkx matplotlib")

def load_state_schema(filepath: str = "state_machine_schema.json") -> Dict[str, Any]:
    """Load the state machine schema from JSON"""
    with open(filepath, 'r') as f:
        return json.load(f)

def create_graphviz_diagram(schema: Dict[str, Any], output_file: str = "state_machine") -> Optional[str]:
    """Create a state diagram using Graphviz"""

    if not HAS_GRAPHVIZ:
        print("Graphviz not available")
        return None

    dot = graphviz.Digraph(comment='CPFR VC State Machine', engine='dot')
    dot.attr(rankdir='TB', size='12,10')
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')

    # Define colors for corruption risk levels
    risk_colors = {
        'NONE': 'lightgreen',
        'LOW': 'lightblue',
        'MEDIUM': 'yellow',
        'HIGH': 'orange',
        'CRITICAL': 'red'
    }

    # Add nodes (states)
    for state_id, state_data in schema['states'].items():
        label = f"{state_data['name']}\\n[{state_id}]"
        color = risk_colors.get(state_data.get('corruptionRisk', 'LOW'), 'lightgray')

        if state_data.get('terminal'):
            dot.node(state_id, label, fillcolor=color, shape='doubleoctagon')
        elif state_id == 'AppInit':
            dot.node(state_id, label, fillcolor=color, shape='circle')
        elif state_id == 'WarehouseCheck':
            # Special highlighting for the hang point
            dot.node(state_id, label + "\\n⚠️ HANG POINT", fillcolor='red', fontcolor='white', style='filled,bold')
        elif state_id == 'StateValidation':
            # Highlight the corruption point
            dot.node(state_id, label + "\\n❌ REMOVE", fillcolor='darkred', fontcolor='white', style='filled,dashed')
        else:
            dot.node(state_id, label, fillcolor=color)

    # Add edges (transitions)
    for transition in schema.get('transitions', []):
        from_state = transition['from']
        to_state = transition['to']
        label = transition.get('trigger', '')

        # Style based on safety
        if transition.get('safe') is False:
            dot.edge(from_state, to_state, label=label, color='red', style='dashed')
        elif transition.get('recommended'):
            dot.edge(from_state, to_state, label=label, color='green', style='bold')
        elif transition.get('criticalPath'):
            dot.edge(from_state, to_state, label=label, color='blue', style='bold')
        else:
            dot.edge(from_state, to_state, label=label)

    # Add legend
    with dot.subgraph(name='cluster_legend') as legend:
        legend.attr(label='Corruption Risk Legend', style='rounded')
        legend.node('legend_none', 'NONE', fillcolor='lightgreen')
        legend.node('legend_low', 'LOW', fillcolor='lightblue')
        legend.node('legend_med', 'MEDIUM', fillcolor='yellow')
        legend.node('legend_high', 'HIGH', fillcolor='orange')
        legend.node('legend_crit', 'CRITICAL', fillcolor='red')

    # Render
    dot.render(output_file, format='png', cleanup=True)
    dot.render(output_file, format='svg', cleanup=True)
    print(f"✅ Generated {output_file}.png and {output_file}.svg")

    return output_file

def create_networkx_diagram(schema: Dict[str, Any], output_file: str = "state_machine_nx.png") -> Optional[str]:
    """Create a state diagram using NetworkX and Matplotlib"""

    if not HAS_NETWORKX:
        print("NetworkX not available")
        return None

    # Create directed graph
    G = nx.DiGraph()

    # Add nodes
    for state_id in schema['states'].keys():
        G.add_node(state_id)

    # Add edges from transitions
    for transition in schema.get('transitions', []):
        G.add_edge(transition['from'], transition['to'],
                  trigger=transition.get('trigger', ''))

    # Create layout
    pos = nx.spring_layout(G, k=2, iterations=50)

    # Set up the plot
    plt.figure(figsize=(16, 12))
    plt.title("CPFR VC App State Machine", fontsize=16, fontweight='bold')

    # Color mapping based on corruption risk
    risk_colors = {
        'NONE': '#90EE90',  # lightgreen
        'LOW': '#ADD8E6',   # lightblue
        'MEDIUM': '#FFFF00', # yellow
        'HIGH': '#FFA500',   # orange
        'CRITICAL': '#FF0000' # red
    }

    # Get node colors
    node_colors = []
    for node in G.nodes():
        risk = schema['states'].get(node, {}).get('corruptionRisk', 'LOW')
        node_colors.append(risk_colors.get(risk, '#D3D3D3'))

    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                          node_size=3000, alpha=0.8)
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
    nx.draw_networkx_edges(G, pos, edge_color='gray',
                          arrows=True, arrowsize=20, width=2)

    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, 'trigger')
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6)

    # Add legend
    legend_elements = []
    for risk, color in risk_colors.items():
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                         markerfacecolor=color, markersize=10,
                                         label=f'Risk: {risk}'))
    plt.legend(handles=legend_elements, loc='upper right')

    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ Generated {output_file}")
    plt.show()

    return output_file

def generate_mermaid_code(schema: Dict[str, Any]) -> str:
    """Generate Mermaid diagram code from schema"""

    mermaid = ["```mermaid", "stateDiagram-v2", "    [*] --> AppInit: Page Load", ""]

    # Add transitions
    for transition in schema.get('transitions', []):
        from_state = transition['from']
        to_state = transition['to']
        trigger = transition.get('trigger', 'auto')

        if transition.get('safe') is False:
            mermaid.append(f"    {from_state} --> {to_state}: ❌ {trigger}")
        elif transition.get('recommended'):
            mermaid.append(f"    {from_state} --> {to_state}: ✅ {trigger}")
        else:
            mermaid.append(f"    {from_state} --> {to_state}: {trigger}")

    # Add notes for critical states
    mermaid.extend([
        "",
        "    note right of WarehouseCheck",
        "        HANG POINT: App gets stuck here",
        "        when corruption exists",
        "    end note",
        "",
        "    note right of StateValidation",
        "        CORRUPTION POINT: validate_session_state()",
        "        was modifying state here",
        "    end note",
        "```"
    ])

    return "\n".join(mermaid)

def main():
    """Main function to generate all visualizations"""

    print("=" * 60)
    print("CPFR VC App State Machine Visualizer")
    print("=" * 60)

    # Load schema
    try:
        schema = load_state_schema()
        print(f"✅ Loaded state machine schema")
        print(f"   States: {len(schema['states'])}")
        print(f"   Transitions: {len(schema['transitions'])}")
    except FileNotFoundError:
        print("❌ Error: state_machine_schema.json not found")
        print("   Please ensure the file exists in the current directory")
        sys.exit(1)

    # Generate visualizations
    print("\nGenerating visualizations...")

    # Graphviz
    if HAS_GRAPHVIZ:
        create_graphviz_diagram(schema)
    else:
        print("⚠️  Skipping Graphviz diagram (library not installed)")

    # NetworkX
    if HAS_NETWORKX:
        create_networkx_diagram(schema)
    else:
        print("⚠️  Skipping NetworkX diagram (library not installed)")

    # Mermaid
    mermaid_code = generate_mermaid_code(schema)
    with open("state_machine_mermaid.md", 'w') as f:
        f.write("# State Machine Diagram (Mermaid)\n\n")
        f.write("Copy this code to any Markdown viewer that supports Mermaid:\n\n")
        f.write(mermaid_code)
    print("✅ Generated state_machine_mermaid.md")

    # Summary report
    print("\n" + "=" * 60)
    print("Summary Report")
    print("=" * 60)

    # Count risk levels
    risk_counts = {}
    for state in schema['states'].values():
        risk = state.get('corruptionRisk', 'UNKNOWN')
        risk_counts[risk] = risk_counts.get(risk, 0) + 1

    print("\nCorruption Risk Distribution:")
    for risk, count in sorted(risk_counts.items()):
        print(f"  {risk:10s}: {count:2d} states")

    # Identify critical states
    critical_states = [
        state_id for state_id, state_data in schema['states'].items()
        if state_data.get('corruptionRisk') == 'CRITICAL'
    ]

    if critical_states:
        print(f"\n⚠️  Critical Risk States: {', '.join(critical_states)}")

    # Unsafe transitions
    unsafe_transitions = [
        f"{t['from']} -> {t['to']}"
        for t in schema.get('transitions', [])
        if t.get('safe') is False
    ]

    if unsafe_transitions:
        print(f"\n❌ Unsafe Transitions: {', '.join(unsafe_transitions)}")

    print("\n✅ Visualization complete!")
    print("\nGenerated files:")
    print("  - state_machine.png/svg (if graphviz installed)")
    print("  - state_machine_nx.png (if networkx installed)")
    print("  - state_machine_mermaid.md (always generated)")

if __name__ == "__main__":
    main()