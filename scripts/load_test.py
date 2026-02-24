#!/usr/bin/env python3
"""Load test script for benchmarking Fourbyfour event throughput."""

import asyncio
import time
import uuid
import argparse
import statistics
from datetime import datetime, timedelta
from typing import NamedTuple

import httpx

# Default configuration
DEFAULT_BASE_URL = "http://localhost:8001"
DEFAULT_EVENTS_COUNT = 1000
DEFAULT_CONCURRENCY = 50


class BenchmarkResult(NamedTuple):
    total_events: int
    successful: int
    failed: int
    duration_seconds: float
    events_per_second: float
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float


async def fire_event(
    client: httpx.AsyncClient,
    base_url: str,
    event_type: str,
) -> tuple[bool, float]:
    """Fire a single event and return success status and latency."""
    user_id = f"u_{uuid.uuid4().hex[:8]}"
    course_id = f"course_{uuid.uuid4().hex[:8]}"

    endpoints = {
        "course.abandoned": {
            "url": f"{base_url}/api/events/course-abandoned",
            "params": {
                "user_id": user_id,
                "course_id": course_id,
                "course_name": "Python Basics",
                "progress": 35,
            },
        },
        "streak.broken": {
            "url": f"{base_url}/api/events/streak-broken",
            "params": {
                "user_id": user_id,
                "streak_days": 7,
            },
        },
        "certificate.earned": {
            "url": f"{base_url}/api/events/certificate-earned",
            "params": {
                "user_id": user_id,
                "course_id": course_id,
                "course_name": "Python Mastery",
            },
        },
    }

    config = endpoints.get(event_type, endpoints["course.abandoned"])

    start = time.perf_counter()
    try:
        response = await client.post(config["url"], params=config["params"])
        latency = (time.perf_counter() - start) * 1000  # ms
        return response.status_code == 200, latency
    except Exception as e:
        latency = (time.perf_counter() - start) * 1000
        print(f"Error: {e}")
        return False, latency


async def run_load_test(
    base_url: str,
    total_events: int,
    concurrency: int,
    event_type: str,
) -> BenchmarkResult:
    """Run load test with specified parameters."""
    print(f"\n{'=' * 60}")
    print(f"Load Test Configuration")
    print(f"{'=' * 60}")
    print(f"Base URL:     {base_url}")
    print(f"Event Type:   {event_type}")
    print(f"Total Events: {total_events:,}")
    print(f"Concurrency:  {concurrency}")
    print(f"{'=' * 60}\n")

    latencies: list[float] = []
    successful = 0
    failed = 0

    semaphore = asyncio.Semaphore(concurrency)

    async def bounded_fire():
        nonlocal successful, failed
        async with semaphore:
            async with httpx.AsyncClient(timeout=30.0) as client:
                success, latency = await fire_event(client, base_url, event_type)
                latencies.append(latency)
                if success:
                    successful += 1
                else:
                    failed += 1

    print("Starting load test...")
    start_time = time.perf_counter()

    # Create all tasks
    tasks = [bounded_fire() for _ in range(total_events)]

    # Progress tracking
    completed = 0
    for coro in asyncio.as_completed(tasks):
        await coro
        completed += 1
        if completed % 100 == 0 or completed == total_events:
            elapsed = time.perf_counter() - start_time
            rate = completed / elapsed
            print(f"Progress: {completed:,}/{total_events:,} ({rate:.1f} events/sec)")

    duration = time.perf_counter() - start_time

    # Calculate statistics
    sorted_latencies = sorted(latencies)
    p50_idx = int(len(sorted_latencies) * 0.50)
    p95_idx = int(len(sorted_latencies) * 0.95)
    p99_idx = int(len(sorted_latencies) * 0.99)

    result = BenchmarkResult(
        total_events=total_events,
        successful=successful,
        failed=failed,
        duration_seconds=duration,
        events_per_second=total_events / duration,
        avg_latency_ms=statistics.mean(latencies),
        p50_latency_ms=sorted_latencies[p50_idx],
        p95_latency_ms=sorted_latencies[p95_idx],
        p99_latency_ms=sorted_latencies[p99_idx],
    )

    return result


def print_results(result: BenchmarkResult):
    """Print benchmark results."""
    print(f"\n{'=' * 60}")
    print(f"Benchmark Results")
    print(f"{'=' * 60}")
    print(f"Total Events:     {result.total_events:,}")
    print(f"Successful:       {result.successful:,} ({result.successful/result.total_events*100:.1f}%)")
    print(f"Failed:           {result.failed:,} ({result.failed/result.total_events*100:.1f}%)")
    print(f"Duration:         {result.duration_seconds:.2f} seconds")
    print(f"{'=' * 60}")
    print(f"Throughput:       {result.events_per_second:.1f} events/second")
    print(f"{'=' * 60}")
    print(f"Latency (avg):    {result.avg_latency_ms:.1f} ms")
    print(f"Latency (p50):    {result.p50_latency_ms:.1f} ms")
    print(f"Latency (p95):    {result.p95_latency_ms:.1f} ms")
    print(f"Latency (p99):    {result.p99_latency_ms:.1f} ms")
    print(f"{'=' * 60}\n")


def main():
    parser = argparse.ArgumentParser(description="Load test for demo-edtech")
    parser.add_argument(
        "--url",
        default=DEFAULT_BASE_URL,
        help=f"Base URL of the demo app (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--events",
        type=int,
        default=DEFAULT_EVENTS_COUNT,
        help=f"Total number of events to fire (default: {DEFAULT_EVENTS_COUNT})",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=f"Number of concurrent requests (default: {DEFAULT_CONCURRENCY})",
    )
    parser.add_argument(
        "--event-type",
        choices=["course.abandoned", "streak.broken", "certificate.earned"],
        default="course.abandoned",
        help="Type of event to fire (default: course.abandoned)",
    )

    args = parser.parse_args()

    result = asyncio.run(
        run_load_test(
            base_url=args.url,
            total_events=args.events,
            concurrency=args.concurrency,
            event_type=args.event_type,
        )
    )

    print_results(result)


if __name__ == "__main__":
    main()
