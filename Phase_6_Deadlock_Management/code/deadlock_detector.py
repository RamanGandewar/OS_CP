from datetime import datetime
import sys
from pathlib import Path

try:
    import networkx as nx
except ImportError:  # pragma: no cover
    nx = None

from flask import Flask

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from Backend.models import DeadlockEvent, ResourceAllocationRecord, db
from .rag_builder import ResourceAllocationGraphBuilder


def _get_app():
    app = Flask(__name__)
    db_path = ROOT_DIR / "Backend" / "database" / "crm.db"
    app.config["SECRET_KEY"] = "phase-6-deadlock-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path.as_posix()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"check_same_thread": False}}
    db.init_app(app)
    return app


class DeadlockDetector:
    def __init__(self, output_dir):
        self.graph_builder = ResourceAllocationGraphBuilder(output_dir)

    def detect_deadlock(self, record_event=True):
        app = _get_app()
        with app.app_context():
            allocations = [item.to_dict() for item in ResourceAllocationRecord.query.all()]

        graph = self.graph_builder.build_graph(allocations)
        image_path = self.graph_builder.save_graph_image(graph)
        if graph is None:
            return {"deadlock": False, "processes": [], "resources": [], "graph_path": str(image_path) if image_path else None}

        cycles = self._find_cycles(graph)
        if not cycles:
            return {"deadlock": False, "processes": [], "resources": [], "graph_path": str(image_path) if image_path else None}

        involved_processes = sorted({node.replace("P:", "") for cycle in cycles for node in cycle if node.startswith("P:")})
        involved_resources = sorted({node.replace("R:", "") for cycle in cycles for node in cycle if node.startswith("R:")})
        if record_event:
            self._record_event(involved_processes, involved_resources, None)
        return {
            "deadlock": True,
            "processes": involved_processes,
            "resources": involved_resources,
            "cycles": cycles,
            "graph_path": str(image_path) if image_path else None,
        }

    def _find_cycles(self, graph):
        if nx is not None and hasattr(graph, "nodes"):
            return list(nx.simple_cycles(graph))

        adjacency = {node: [] for node in graph["nodes"]}
        for source, target, _label in graph["edges"]:
            adjacency.setdefault(source, []).append(target)
            adjacency.setdefault(target, [])

        cycles = set()

        def dfs(start, node, path, seen):
            for neighbor in adjacency.get(node, []):
                if neighbor == start and len(path) > 1:
                    cycle_nodes = path + [start]
                    normalized = self._normalize_cycle(cycle_nodes[:-1])
                    cycles.add(normalized)
                elif neighbor not in seen:
                    dfs(start, neighbor, path + [neighbor], seen | {neighbor})

        for node in adjacency:
            dfs(node, node, [node], {node})

        return [list(cycle) for cycle in cycles]

    def _normalize_cycle(self, cycle):
        rotations = [tuple(cycle[index:] + cycle[:index]) for index in range(len(cycle))]
        return min(rotations)

    def _record_event(self, processes, resources, resolution_action):
        app = _get_app()
        with app.app_context():
            event = DeadlockEvent(
                processes_involved=",".join(processes),
                resources_involved=",".join(resources),
                resolution_action=resolution_action,
                resolved_at=datetime.utcnow() if resolution_action else None,
            )
            db.session.add(event)
            db.session.commit()
