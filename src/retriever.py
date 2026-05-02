import os
import json
import numpy as np
import faiss
from typing import List, Dict, Tuple

from src.data_loader import load_standards, get_embedding_texts
from src.embeddings import encode, encode_single

INDEX_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "faiss_index")
INDEX_PATH = os.path.join(INDEX_DIR, "index.faiss")
META_PATH = os.path.join(INDEX_DIR, "metadata.json")


class FAISSRetriever:
    def __init__(self):
        self.standards: List[Dict] = []
        self.index: faiss.Index = None
        self._load_or_build()

    def _load_or_build(self):
        if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
            self._load_index()
        else:
            self._build_index()

    def _load_index(self):
        self.index = faiss.read_index(INDEX_PATH)
        with open(META_PATH, "r", encoding="utf-8") as f:
            self.standards = json.load(f)

    def _build_index(self):
        os.makedirs(INDEX_DIR, exist_ok=True)
        self.standards = load_standards()
        texts = get_embedding_texts(self.standards)
        embeddings = encode(texts)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)
        faiss.write_index(self.index, INDEX_PATH)
        with open(META_PATH, "w", encoding="utf-8") as f:
            json.dump(self.standards, f, ensure_ascii=False, indent=2)

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[Dict, float]]:
        q_emb = encode_single(query).reshape(1, -1)
        scores, indices = self.index.search(q_emb, min(k, len(self.standards)))
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:
                results.append((self.standards[idx], float(score)))
        return results


_retriever_instance = None


def get_retriever() -> FAISSRetriever:
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = FAISSRetriever()
    return _retriever_instance
