import numpy as np
from typing import List

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def encode(texts: List[str]) -> np.ndarray:
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.astype(np.float32)


def encode_single(text: str) -> np.ndarray:
    return encode([text])[0]
