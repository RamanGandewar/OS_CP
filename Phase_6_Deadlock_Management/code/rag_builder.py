from pathlib import Path

try:
    import networkx as nx
except ImportError:  # pragma: no cover
    nx = None

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class ResourceAllocationGraphBuilder:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_graph(self, allocations):
        if nx is None:
            nodes = set()
            edges = []
            for item in allocations:
                process_node = f"P:{item['process_id']}"
                resource_node = f"R:{item['resource_name']}"
                nodes.add(process_node)
                nodes.add(resource_node)
                if item["allocated_count"] > 0:
                    edges.append((resource_node, process_node, f"alloc:{item['allocated_count']}"))
                if item["requested_count"] > 0:
                    edges.append((process_node, resource_node, f"req:{item['requested_count']}"))
            return {"nodes": sorted(nodes), "edges": edges}
        graph = nx.DiGraph()
        for item in allocations:
            process_node = f"P:{item['process_id']}"
            resource_node = f"R:{item['resource_name']}"
            graph.add_node(process_node, kind="process")
            graph.add_node(resource_node, kind="resource")
            if item["allocated_count"] > 0:
                graph.add_edge(resource_node, process_node, label=f"alloc:{item['allocated_count']}")
            if item["requested_count"] > 0:
                graph.add_edge(process_node, resource_node, label=f"req:{item['requested_count']}")
        return graph

    def save_graph_image(self, graph, filename="resource_allocation_graph.png"):
        if graph is None:
            return None
        if nx is None:
            figure, axis = plt.subplots(figsize=(8, 6))
            axis.axis("off")
            axis.set_title("Resource Allocation Graph")
            edge_lines = [f"{source} -> {target} ({label})" for source, target, label in graph["edges"]]
            content = "\n".join(edge_lines) if edge_lines else "No active allocations or requests."
            axis.text(0.02, 0.98, content, va="top", ha="left", wrap=True, family="monospace")
            output_path = self.output_dir / filename
            figure.savefig(output_path, bbox_inches="tight")
            plt.close(figure)
            return output_path
        figure, axis = plt.subplots(figsize=(8, 6))
        pos = nx.spring_layout(graph, seed=7)
        labels = nx.get_edge_attributes(graph, "label")
        nx.draw(graph, pos, with_labels=True, node_color="#dbeafe", edge_color="#1f2937", ax=axis)
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels, ax=axis)
        axis.set_title("Resource Allocation Graph")
        output_path = self.output_dir / filename
        figure.savefig(output_path, bbox_inches="tight")
        plt.close(figure)
        return output_path
