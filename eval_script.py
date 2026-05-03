"""
Official evaluation script — BIS Standards RAG Hackathon.

Computes:
  - Hit Rate @3 : fraction of queries where a ground-truth standard appears in top-3
  - MRR @5      : Mean Reciprocal Rank of first relevant result in top-5
  - Avg Latency : average latency_seconds across all queries

Usage:
    python eval_script.py --results team_results.json

Results JSON format (output of inference.py):
    [
      {
        "id": "PUB-01",
        "query": "...",
        "expected_standards": ["IS 269:1989"],
        "retrieved_standards": ["IS 269:2015", "IS 8112:2013", ...],
        "latency_seconds": 1.23
      },
      ...
    ]
"""

import argparse
import json
import sys
from typing import List, Dict


def normalize_std(std_string: str) -> str:
    return str(std_string).replace(" ", "").lower()


def hit_rate_at_k(results: List[Dict], k: int = 3) -> float:
    hits = 0
    total = 0
    for r in results:
        expected = [normalize_std(s) for s in r.get("expected_standards", [])]
        if not expected:
            continue
        retrieved = [normalize_std(s) for s in r.get("retrieved_standards", [])[:k]]
        if any(s in expected for s in retrieved):
            hits += 1
        total += 1
    return hits / total if total > 0 else 0.0


def mrr_at_k(results: List[Dict], k: int = 5) -> float:
    rr_sum = 0.0
    total = 0
    for r in results:
        expected = [normalize_std(s) for s in r.get("expected_standards", [])]
        if not expected:
            continue
        retrieved = [normalize_std(s) for s in r.get("retrieved_standards", [])[:k]]
        rr = 0.0
        for rank, std in enumerate(retrieved, 1):
            if std in expected:
                rr = 1.0 / rank
                break
        rr_sum += rr
        total += 1
    return rr_sum / total if total > 0 else 0.0


def avg_latency(results: List[Dict]) -> float:
    latencies = [r.get("latency_seconds", 0.0) for r in results]
    return sum(latencies) / len(latencies) if latencies else 0.0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate BIS Standards RAG results")
    parser.add_argument("--results", required=True, help="Path to inference output JSON")
    args = parser.parse_args()

    with open(args.results, "r", encoding="utf-8") as f:
        results = json.load(f)

    hr3  = hit_rate_at_k(results, k=3)
    mrr5 = mrr_at_k(results, k=5)
    lat  = avg_latency(results)

    metrics = {
        "hit_rate_at_3":       round(hr3, 4),
        "mrr_at_5":            round(mrr5, 4),
        "avg_latency_seconds": round(lat, 4),
        "num_queries":         len(results),
    }

    print("\n" + "=" * 45)
    print("  BIS Standards RAG — Evaluation Results")
    print("=" * 45)
    print(f"  Hit Rate @3         : {metrics['hit_rate_at_3']:.4f}")
    print(f"  MRR @5              : {metrics['mrr_at_5']:.4f}")
    print(f"  Avg Latency (s)     : {metrics['avg_latency_seconds']:.4f}")
    print(f"  Queries evaluated   : {metrics['num_queries']}")
    print("=" * 45)
    print("\nJSON output:")
    print(json.dumps(metrics, indent=2))
