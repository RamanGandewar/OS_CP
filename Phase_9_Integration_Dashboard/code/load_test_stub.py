from concurrent.futures import ThreadPoolExecutor
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "Backend"
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from app import app


def request_snapshot(_index):
    client = app.test_client()
    response = client.get("/api/dashboard/snapshot")
    return response.status_code


def run_load_test(users=25):
    with ThreadPoolExecutor(max_workers=users) as executor:
        results = list(executor.map(request_snapshot, range(users)))
    print({"users": users, "success_count": sum(1 for item in results if item == 200)})


if __name__ == "__main__":
    run_load_test()
