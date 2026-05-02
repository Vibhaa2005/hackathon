"""
Entry-point script for judges.

Usage:
    python inference.py --input hidden_private_dataset.json --output team_results.json

Input JSON format:
    [{"id": "q1", "query": "OPC 43 cement for RCC columns"}, ...]

Output JSON format:
    [{"id": "q1", "retrieved_standards": ["IS 8112:2013", ...], "latency_seconds": 0.123}, ...]
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from src.rag_pipeline import get_pipeline


def run_inference(input_path: str, output_path: str, top_k: int = 5) -> None:
    with open(input_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    pipeline = get_pipeline()
    pipeline.top_k = top_k

    results = []
    for item in items:
        item_id = item.get("id", str(len(results)))
        query = item.get("query", "")

        t0 = time.time()
        output = pipeline.query(query)
        latency = round(time.time() - t0, 4)

        retrieved_standards = [r["standard_number"] for r in output["results"]]

        results.append({
            "id": item_id,
            "retrieved_standards": retrieved_standards,
            "latency_seconds": latency,
        })
        print(f"[{item_id}] {len(retrieved_standards)} standards in {latency:.3f}s")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True) if os.path.dirname(output_path) else None
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nDone. {len(results)} queries processed → {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BIS Standards RAG — inference script")
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    parser.add_argument("--top_k", type=int, default=5, help="Number of standards to retrieve")
    args = parser.parse_args()

    run_inference(args.input, args.output, args.top_k)
