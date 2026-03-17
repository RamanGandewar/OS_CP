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

    print("Requesting unified dashboard snapshot...")
    snapshot = client.get("/api/dashboard/snapshot")
    print(snapshot.status_code)
    data = snapshot.json
    print(data["overview"])

    print("Generating analytics files...")
    analytics = client.post("/api/dashboard/analytics/generate")
    print(analytics.status_code, analytics.json)

    print("Testing CSV export...")
    csv_response = client.get("/api/dashboard/export/csv")
    print(csv_response.status_code, csv_response.headers.get("Content-Type"))

    print("Testing performance report export...")
    report_response = client.get("/api/dashboard/report")
    print(report_response.status_code, report_response.headers.get("Content-Type"))

    print("Testing stream endpoint...")
    stream_response = client.get("/api/dashboard/stream")
    print(stream_response.status_code, stream_response.headers.get("Content-Type"))


if __name__ == "__main__":
    run_validation()
