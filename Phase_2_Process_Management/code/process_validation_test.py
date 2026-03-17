import threading
import time

import requests

BASE_URL = "http://127.0.0.1:5000/api"
RESULTS = []


def login_user(index):
    session = requests.Session()
    response = session.post(
        f"{BASE_URL}/auth/login",
        json={"username": f"user{index}", "password": "password123"},
        timeout=10,
    )
    data = response.json()
    RESULTS.append({"user": f"user{index}", "pid": data.get("process_pid"), "status": response.status_code, "session": session})


def main():
    threads = [threading.Thread(target=login_user, args=(index,)) for index in range(1, 6)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    pids = [item["pid"] for item in RESULTS if item["status"] == 200]
    print("Unique PIDs:", len(set(pids)) == len(pids), pids)

    time.sleep(4)
    monitor = requests.get(f"{BASE_URL}/processes/monitor", timeout=10).json()
    print("Tracked processes:", monitor["total_count"])
    print("State counts:", monitor["state_counts"])

    for item in RESULTS:
        item["session"].post(f"{BASE_URL}/auth/logout", timeout=10)

    time.sleep(3)
    post_logout = requests.get(f"{BASE_URL}/processes/monitor", timeout=10).json()
    print("After logout active count:", post_logout["active_count"])


if __name__ == "__main__":
    main()
