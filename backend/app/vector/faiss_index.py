import json
from pathlib import Path

import numpy as np

from app.core.config import settings

try:
    import faiss
except ImportError:  # pragma: no cover - exercised only when faiss is unavailable.
    faiss = None


class FaissIndex:
    """Small FAISS adapter that owns vectors, not application persistence."""

    def __init__(self, index_path: str | None = None) -> None:
        self.index_path = Path(index_path or settings.faiss_index_path)
        self.mapping_path = self.index_path.with_suffix(".json")
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self._index = None
        self._vector_ids: list[int] = self._load_mapping()

    def add(self, *, vector_id: int, vector: list[float]) -> None:
        normalized = self._normalize(vector)
        index = self._load_or_create_index(normalized.shape[1])
        index.add(normalized)
        self._vector_ids.append(vector_id)
        self._save_index()
        self._save_mapping()

    def search(self, *, vector: list[float], limit: int = 10) -> list[tuple[int, float]]:
        if not self._vector_ids and not self.index_path.exists():
            return []
        normalized = self._normalize(vector)
        index = self._load_or_create_index(normalized.shape[1])
        if index.ntotal == 0:
            return []

        scores, positions = index.search(normalized, min(limit, index.ntotal))
        matches: list[tuple[int, float]] = []
        for position, score in zip(positions[0], scores[0], strict=False):
            if 0 <= position < len(self._vector_ids):
                matches.append((self._vector_ids[position], float(score)))
        return matches

    def _load_or_create_index(self, dimensions: int):
        if self._index is not None:
            return self._index
        if faiss is not None and self.index_path.exists():
            self._index = faiss.read_index(str(self.index_path))
            return self._index
        if faiss is None:
            self._index = _NumpyIndex.load(self.index_path, dimensions) if self.index_path.exists() else _NumpyIndex(dimensions)
        else:
            self._index = faiss.IndexFlatIP(dimensions)
        return self._index

    def _save_index(self) -> None:
        if faiss is not None:
            faiss.write_index(self._index, str(self.index_path))
        elif isinstance(self._index, _NumpyIndex):
            self._index.save(self.index_path)

    def _load_mapping(self) -> list[int]:
        if not self.mapping_path.exists():
            return []
        return [int(item) for item in json.loads(self.mapping_path.read_text())]

    def _save_mapping(self) -> None:
        self.mapping_path.write_text(json.dumps(self._vector_ids))

    @staticmethod
    def _normalize(vector: list[float]) -> np.ndarray:
        arr = np.array([vector], dtype="float32")
        norm = np.linalg.norm(arr, axis=1, keepdims=True)
        norm[norm == 0] = 1.0
        return arr / norm


class _NumpyIndex:
    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions
        self.vectors = np.empty((0, dimensions), dtype="float32")

    @property
    def ntotal(self) -> int:
        return int(self.vectors.shape[0])

    def add(self, vectors: np.ndarray) -> None:
        self.vectors = np.vstack([self.vectors, vectors])

    def search(self, query: np.ndarray, limit: int) -> tuple[np.ndarray, np.ndarray]:
        if self.ntotal == 0:
            return np.array([[]], dtype="float32"), np.array([[]], dtype="int64")
        scores = self.vectors @ query[0]
        order = np.argsort(scores)[::-1][:limit]
        return np.array([scores[order]], dtype="float32"), np.array([order], dtype="int64")

    def save(self, path: Path) -> None:
        with path.open("wb") as handle:
            np.save(handle, self.vectors)

    @classmethod
    def load(cls, path: Path, dimensions: int) -> "_NumpyIndex":
        index = cls(dimensions)
        with path.open("rb") as handle:
            index.vectors = np.load(handle)
        return index

