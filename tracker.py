import os
import time
import requests

DUNE_API_KEY = os.getenv("DUNE_API_KEY")
DUNE_QUERY_ID = os.getenv("DUNE_QUERY_ID")

POLL_SECONDS = 30

if not DUNE_API_KEY:
    raise RuntimeError("DUNE_API_KEY is missing")

if not DUNE_QUERY_ID:
    raise RuntimeError("DUNE_QUERY_ID is missing")


headers = {
    "X-Dune-API-Key": DUNE_API_KEY,
    "Content-Type": "application/json",
}


def execute_query():
    url = f"https://api.dune.com/api/v1/query/{DUNE_QUERY_ID}/execute"

    response = requests.post(
        url,
        headers=headers,
        json={}
    )

    response.raise_for_status()
    return response.json()["execution_id"]


def get_results(execution_id):
    url = f"https://api.dune.com/api/v1/execution/{execution_id}/results"

    while True:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()

        if data.get("state") == "QUERY_STATE_COMPLETED":
            return data.get("result", {}).get("rows", [])

        if data.get("state") in (
            "QUERY_STATE_FAILED",
            "QUERY_STATE_CANCELLED"
        ):
            raise RuntimeError(f"Query failed: {data}")

        time.sleep(5)


def print_top_wallets(rows):
    print("\n===== QUID LIVE TRACKER =====")

    for row in rows[:20]:
        wallet = row.get("wallet", "")
        volume = row.get("total_volume_usd", 0)

        print(f"{wallet}  |  ${volume:,.2f}")


def main():
    print("QUID tracker started...")

    while True:
        try:
            execution_id = execute_query()
            rows = get_results(execution_id)

            print_top_wallets(rows)

        except Exception as e:
            print("ERROR:", e)

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
