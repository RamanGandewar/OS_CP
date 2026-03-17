import time

import requests

BASE_URL = "http://127.0.0.1:5000/api/threads"


def main():
    created = []
    for index in range(50):
        response = requests.post(
            f"{BASE_URL}/validation-job",
            json={"source": f"validation-{index + 1}"},
            timeout=10,
        )
        created.append(response.json())

    time.sleep(5)
    monitor = requests.get(f"{BASE_URL}/monitor", timeout=10).json()
    print("Threads created:", len(created))
    print("Active threads:", monitor.get("active_count"))
    print("Pool utilization:", monitor.get("thread_pool_utilization"))


if __name__ == "__main__":
    main()
