import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "Backend"
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from app import app, db


def run_validation():
    with app.app_context():
        db.create_all()

    client = app.test_client()

    print("Reading initial I/O monitor...")
    initial = client.get("/api/io/monitor").json
    print(initial["best_algorithm"], initial["reference_sequence"])

    print("Adding disk request...")
    print(client.post("/api/io/requests", json={"request_type": "Generate Report", "track_number": 78}).json)

    print("Comparing algorithms...")
    comparison = client.post(
        "/api/io/compare",
        json={"requests": [45, 12, 78, 23, 67, 89, 34, 56], "current_head": 50},
    ).json
    print({name: data["total_seek"] for name, data in comparison.items()})

    print("Allocating buffer...")
    print(client.post("/api/io/buffer/allocate", json={"request_type": "upload", "size": 120}).json)

    print("Queueing print job...")
    print(client.post("/api/io/spool/enqueue", json={"job_type": "invoice", "filename": "invoice-001.pdf", "pages": 4, "user_id": 1}).json)

    print("Processing print job...")
    print(client.post("/api/io/spool/process").json)

    print("Reading final I/O monitor...")
    final_state = client.get("/api/io/monitor").json
    print(final_state["best_algorithm"], len(final_state["print_queue"]))


if __name__ == "__main__":
    run_validation()
