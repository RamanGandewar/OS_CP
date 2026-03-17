from datetime import datetime
import sys
from pathlib import Path

from flask import Flask

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from Backend.models import DeadlockEvent, ProcessRecord, ResourceAllocationRecord, db


def _get_app():
    app = Flask(__name__)
    db_path = ROOT_DIR / "Backend" / "database" / "crm.db"
    app.config["SECRET_KEY"] = "phase-6-deadlock-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path.as_posix()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"check_same_thread": False}}
    db.init_app(app)
    return app


class DeadlockRecovery:
    def choose_victim(self, processes):
        app = _get_app()
        with app.app_context():
            records = ProcessRecord.query.filter(ProcessRecord.pid.in_(processes)).all()
            if records:
                victim = sorted(records, key=lambda record: record.priority, reverse=True)[0]
                return str(victim.pid)
        return sorted(processes)[-1]

    def recover(self, processes):
        victim = self.choose_victim(processes)
        app = _get_app()
        with app.app_context():
            allocations = ResourceAllocationRecord.query.filter_by(process_id=str(victim)).all()
            released_resources = []
            for allocation in allocations:
                if allocation.resource:
                    allocation.resource.available_instances += allocation.allocated_count
                    released_resources.append(allocation.resource.resource_name)
                allocation.allocated_count = 0
                allocation.requested_count = 0

            event = DeadlockEvent.query.order_by(DeadlockEvent.id.desc()).first()
            if event and not event.resolution_action:
                event.resolution_action = f"Rolled back victim process {victim}"
                event.resolved_at = datetime.utcnow()
            db.session.commit()

        return {"victim_process": victim, "released_resources": released_resources}
