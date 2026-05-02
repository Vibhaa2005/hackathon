"""
Evaluation script for BIS Standards RAG system.

Computes:
  - Hit Rate @3  : fraction of queries where a ground-truth standard is in top-3
  - MRR @5       : Mean Reciprocal Rank of first relevant result in top-5
  - Avg Latency  : average latency_seconds across all queries

Usage:
    python eval_script.py --results team_results.json --ground_truth ground_truth.json

Ground-truth JSON format:
    [{"id": "q1", "relevant_standards": ["IS 8112:2013", "IS 12269:2013"]}, ...]

Results JSON format (output of inference.py):
    [{"id": "q1", "retrieved_standards": ["IS 8112:2013", ...], "latency_seconds": 0.12}, ...]
"""

import argparse
import json
import sys
from typing import List, Dict


def hit_rate_at_k(results: List[Dict], ground_truth: Dict[str, List[str]], k: int = 3) -> float:
    hits = 0
    total = 0
    for r in results:
        item_id = r["id"]
        if item_id not in ground_truth:
            continue
        relevant = set(ground_truth[item_id])
        retrieved = r["retrieved_standards"][:k]
        if any(std in relevant for std in retrieved):
            hits += 1
        total += 1
    return hits / total if total > 0 else 0.0


def mrr_at_k(results: List[Dict], ground_truth: Dict[str, List[str]], k: int = 5) -> float:
    rr_sum = 0.0
    total = 0
    for r in results:
        item_id = r["id"]
        if item_id not in ground_truth:
            continue
        relevant = set(ground_truth[item_id])
        retrieved = r["retrieved_standards"][:k]
        rr = 0.0
        for rank, std in enumerate(retrieved, 1):
            if std in relevant:
                rr = 1.0 / rank
                break
        rr_sum += rr
        total += 1
    return rr_sum / total if total > 0 else 0.0


def avg_latency(results: List[Dict]) -> float:
    latencies = [r.get("latency_seconds", 0.0) for r in results]
    return sum(latencies) / len(latencies) if latencies else 0.0


def evaluate(results_path: str, ground_truth_path: str) -> Dict:
    with open(results_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    with open(ground_truth_path, "r", encoding="utf-8") as f:
        gt_list = json.load(f)

    gt = {item["id"]: item["relevant_standards"] for item in gt_list}

    hr3 = hit_rate_at_k(results, gt, k=3)
    mrr5 = mrr_at_k(results, gt, k=5)
    lat = avg_latency(results)

    metrics = {
        "hit_rate_at_3": round(hr3, 4),
        "mrr_at_5": round(mrr5, 4),
        "avg_latency_seconds": round(lat, 4),
        "num_queries": len(results),
    }
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate BIS Standards RAG results")
    parser.add_argument("--results", required=True, help="Path to inference output JSON")
    parser.add_argument("--ground_truth", required=True, help="Path to ground-truth JSON")
    args = parser.parse_args()

    metrics = evaluate(args.results, args.ground_truth)

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
