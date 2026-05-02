import json
import os
from typing import List, Dict


DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "bis_standards.json")


def load_standards() -> List[Dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        standards = json.load(f)
    seen_ids = set()
    unique = []
    for s in standards:
        if s["id"] not in seen_ids:
            seen_ids.add(s["id"])
            unique.append(s)
    return unique


def get_embedding_texts(standards: List[Dict]) -> List[str]:
    texts = []
    for s in standards:
        parts = [
            s.get("standard_number", ""),
            s.get("title", ""),
            s.get("category", ""),
            s.get("description", ""),
            s.get("scope", ""),
            " ".join(s.get("keywords", [])),
            " ".join(s.get("applicable_products", [])),
        ]
        texts.append(" | ".join(filter(None, parts)))
    return texts
