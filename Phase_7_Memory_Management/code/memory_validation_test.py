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

    print("Reading initial monitor...")
    print(client.get("/api/memory/monitor").json["page_table"])

    print("Loading report page 0...")
    print(client.post("/api/memory/report/page", json={"page_number": 0}).json)

    print("Loading report page 1...")
    print(client.post("/api/memory/report/page", json={"page_number": 1}).json)

    print("Accessing customer cache...")
    print(client.post("/api/memory/cache/customer", json={"customer_id": 1}).json)

    print("Accessing quotation cache...")
    print(client.post("/api/memory/cache/quotation", json={"quotation_id": 1}).json)

    print("Comparing replacement algorithms...")
    print(
        client.post(
            "/api/memory/replacement/compare",
            json={"reference_string": [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5], "frame_count": 4},
        ).json
    )

    print("Allocating memory...")
    print(client.post("/api/memory/allocator/allocate", json={"strategy": "best_fit", "size": 70}).json)

    print("Reading final monitor...")
    print(client.get("/api/memory/monitor").json["allocator"])


if __name__ == "__main__":
    run_validation()
