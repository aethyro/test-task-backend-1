import argparse
import asyncio
import time
from statistics import mean
from typing import List

import httpx


async def worker(base_url: str, deadline: float, results: list[float], successes: list[bool]):
    async with httpx.AsyncClient(base_url=base_url, timeout=5.0) as client:
        while time.perf_counter() < deadline:
            started = time.perf_counter()
            try:
                resp = await client.get("/health/healthz")
                successes.append(resp.status_code == 200)
            except Exception:
                successes.append(False)
            else:
                results.append(time.perf_counter() - started)


def percentiles(data: List[float]) -> dict[str, float]:
    if not data:
        return {"p50": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0}
    data_sorted = sorted(data)

    def pct(p: float) -> float:
        k = int((p / 100) * (len(data_sorted) - 1))
        return data_sorted[k]

    return {"p50": pct(50), "p90": pct(90), "p95": pct(95), "p99": pct(99)}


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8080")
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--duration", type=int, default=10, help="seconds")
    args = parser.parse_args()

    results: list[float] = []
    successes: list[bool] = []
    deadline = time.perf_counter() + args.duration

    tasks = [
        asyncio.create_task(worker(args.base_url, deadline, results, successes))
        for _ in range(args.concurrency)
    ]
    await asyncio.gather(*tasks)

    total_requests = len(successes)
    success_count = sum(successes)
    duration = args.duration
    rps = total_requests / duration if duration else 0
    latency = {
        "avg": mean(results) if results else 0,
        "min": min(results) if results else 0,
        "max": max(results) if results else 0,
    }
    latency.update(percentiles(results))

    print("Total requests:", total_requests)
    print("Successes:", success_count)
    print(
        "Success rate:",
        f"{(success_count / total_requests * 100) if total_requests else 0:.2f}%",
    )
    print("Observed RPS:", f"{rps:.2f}")
    print("Latency (s):", latency)


if __name__ == "__main__":
    asyncio.run(main())
