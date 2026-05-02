import json
import time
from typing import List, Dict, Tuple

from src.retriever import get_retriever
from src.llm_client import generate_rationale


class RAGPipeline:
    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        self.retriever = get_retriever()

    def query(self, product_description: str) -> Dict:
        start = time.time()

        retrieved = self.retriever.retrieve(product_description, k=self.top_k)
        standards = [s for s, _ in retrieved]
        scores = [sc for _, sc in retrieved]

        rationale_json = generate_rationale(product_description, standards)

        try:
            rationales = json.loads(rationale_json)
            if not isinstance(rationales, list):
                rationales = []
        except Exception:
            rationales = []

        results = []
        for i, (std, score) in enumerate(zip(standards, scores)):
            rat_entry = {}
            for r in rationales:
                if r.get("standard_number", "") in std.get("standard_number", ""):
                    rat_entry = r
                    break
            if not rat_entry and i < len(rationales):
                rat_entry = rationales[i]

            results.append({
                "rank": i + 1,
                "standard_number": std["standard_number"],
                "title": std["title"],
                "category": std["category"],
                "description": std["description"],
                "scope": std["scope"],
                "key_requirements": std.get("key_requirements", []),
                "applicable_products": std.get("applicable_products", []),
                "year": std.get("year"),
                "relevance_score": round(score, 4),
                "rationale": rat_entry.get("rationale", std.get("scope", "")),
                "key_requirement": rat_entry.get(
                    "key_requirement",
                    std.get("key_requirements", ["See standard."])[0],
                ),
                "id": std["id"],
            })

        latency = round(time.time() - start, 3)
        return {"query": product_description, "results": results, "latency_seconds": latency}


_pipeline_instance = None


def get_pipeline() -> RAGPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = RAGPipeline()
    return _pipeline_instance
