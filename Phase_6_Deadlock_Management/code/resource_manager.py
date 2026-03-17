import sys
from pathlib import Path

from flask import Flask

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from Backend.models import ResourceAllocationRecord, ResourceRecord, db


def _get_app():
    app = Flask(__name__)
    db_path = ROOT_DIR / "Backend" / "database" / "crm.db"
    app.config["SECRET_KEY"] = "phase-6-deadlock-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path.as_posix()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"check_same_thread": False}}
    db.init_app(app)
    return app


class ResourceManager:
    def initialize_defaults(self):
        defaults = [
            ("R1_DB", "DB_CONNECTION", 10),
            ("R2_REPORT", "REPORT_GENERATOR", 3),
            ("R3_EMAIL", "EMAIL_SENDER", 5),
            ("R4_PDF", "PDF_CREATOR", 2),
        ]
        app = _get_app()
        with app.app_context():
            for name, rtype, total in defaults:
                resource = ResourceRecord.query.filter_by(resource_name=name).first()
                if not resource:
                    resource = ResourceRecord(resource_name=name, resource_type=rtype, total_instances=total, available_instances=total)
                    db.session.add(resource)
            db.session.commit()
        return self.get_state()

    def request_resource(self, process_id, resource_name, requested_count=1, grant=False):
        app = _get_app()
        with app.app_context():
            resource = ResourceRecord.query.filter_by(resource_name=resource_name).first()
            if not resource:
                return {"success": False, "message": "Resource not found"}

            allocation = ResourceAllocationRecord.query.filter_by(process_id=str(process_id), resource_id=resource.id).first()
            if not allocation:
                allocation = ResourceAllocationRecord(process_id=str(process_id), resource_id=resource.id, allocated_count=0, requested_count=0)
                db.session.add(allocation)

            if grant and resource.available_instances >= requested_count:
                resource.available_instances -= requested_count
                allocation.allocated_count += requested_count
                allocation.requested_count = max(0, allocation.requested_count - requested_count)
            else:
                allocation.requested_count += requested_count

            db.session.commit()
            return {"success": True, "resource": resource.to_dict(), "allocation": allocation.to_dict()}

    def release_all_for_process(self, process_id):
        app = _get_app()
        with app.app_context():
            allocations = ResourceAllocationRecord.query.filter_by(process_id=str(process_id)).all()
            for allocation in allocations:
                if allocation.resource:
                    allocation.resource.available_instances += allocation.allocated_count
                allocation.allocated_count = 0
                allocation.requested_count = 0
            db.session.commit()

    def reset_state(self):
        app = _get_app()
        with app.app_context():
            allocations = ResourceAllocationRecord.query.all()
            for allocation in allocations:
                db.session.delete(allocation)

            resources = ResourceRecord.query.all()
            for resource in resources:
                resource.available_instances = resource.total_instances

            db.session.commit()
        return self.get_state()

    def get_state(self):
        app = _get_app()
        with app.app_context():
            resources = [resource.to_dict() for resource in ResourceRecord.query.order_by(ResourceRecord.id.asc()).all()]
            allocations = [allocation.to_dict() for allocation in ResourceAllocationRecord.query.order_by(ResourceAllocationRecord.id.asc()).all()]
            return {"resources": resources, "allocations": allocations}
