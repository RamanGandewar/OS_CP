import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
BACKEND_DIR = ROOT_DIR / "Backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from app import app, db


def run_validation():
    with app.app_context():
        db.create_all()

    client = app.test_client()

    print("Initializing resources...")
    print(client.post("/api/deadlock/init-resources").json)

    print("Resetting state...")
    print(client.post("/api/deadlock/reset").json)

    print("Creating deadlock scenario...")
    scenario = client.post("/api/deadlock/scenario/create").json
    print(scenario)

    print("Detecting deadlock...")
    detection = client.get("/api/deadlock/detect").json
    print(detection)

    print("Running Banker's algorithm...")
    banker = client.post(
        "/api/deadlock/banker-check",
        json={"process_id": "P3", "request": {"R1_DB": 1, "R4_PDF": 1}},
    ).json
    print(banker)

    print("Recovering deadlock...")
    recovery = client.post("/api/deadlock/recover", json={"processes": detection.get("processes", [])}).json
    print(recovery)

    print("Reading final state...")
    final_state = client.get("/api/deadlock/state").json
    print(final_state)


if __name__ == "__main__":
    run_validation()
