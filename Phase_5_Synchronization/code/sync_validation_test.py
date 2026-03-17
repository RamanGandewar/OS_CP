import concurrent.futures
import requests

BASE_URL = "http://127.0.0.1:5000/api/sync"


def quotation_attempt(user_id):
    return requests.post(
        f"{BASE_URL}/quotation-edit",
        json={"quotation_id": 123, "user_id": user_id, "data": {"attempt": user_id}},
        timeout=10,
    ).json()


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        quotation_results = list(executor.map(quotation_attempt, range(1, 21)))

    race_demo = requests.get(f"{BASE_URL}/race-demo", timeout=10).json()
    inventory_results = [
        requests.post(f"{BASE_URL}/inventory/reserve", json={"product_id": "PRODUCT_X", "user_id": user_id, "units": 1}, timeout=10).json()
        for user_id in range(1, 8)
    ]

    print("Quotation mutex results:", quotation_results)
    print("Inventory semaphore results:", inventory_results)
    print("Race condition demo:", race_demo)


if __name__ == "__main__":
    main()
