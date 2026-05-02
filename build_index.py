"""
Run this once to pre-build the FAISS index (optional — the app builds it automatically on first run).

Usage:
    python build_index.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.data_loader import load_standards, get_embedding_texts
from src.embeddings import encode
from src.retriever import INDEX_DIR, INDEX_PATH, META_PATH
import json
import faiss

if __name__ == "__main__":
    print("Loading BIS standards…")
    standards = load_standards()
    print(f"  {len(standards)} standards loaded.")

    print("Generating embeddings…")
    texts = get_embedding_texts(standards)
    embeddings = encode(texts)
    print(f"  Embedding shape: {embeddings.shape}")

    os.makedirs(INDEX_DIR, exist_ok=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(standards, f, ensure_ascii=False, indent=2)

    print(f"Index saved to {INDEX_PATH}")
    print(f"Metadata saved to {META_PATH}")
    print("Done.")
