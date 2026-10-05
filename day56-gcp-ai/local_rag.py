"""Tiny deterministic local vectorizer plus FAISS. No embedding API calls."""
import hashlib
import json
import re
from pathlib import Path
import numpy as np
import faiss


class PolicyIndex:
    def __init__(self, documents, dimension=512):
        self.documents = documents
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(self.vectorize([d["text"] for d in documents]))

    def vectorize(self, texts):
        vectors = np.zeros((len(texts), self.dimension), dtype=np.float32)
        for row, text in enumerate(texts):
            for word in re.findall(r"[a-z0-9]+", text.lower()):
                digest = hashlib.blake2b(word.encode(), digest_size=8).digest()
                vectors[row, int.from_bytes(digest, "little") % self.dimension] += 1
        faiss.normalize_L2(vectors)
        return vectors

    def search(self, query, k=2):
        scores, ids = self.index.search(self.vectorize([query]), min(k, len(self.documents)))
        return [{**self.documents[int(idx)], "score": round(float(score), 4)}
                for score, idx in zip(scores[0], ids[0]) if idx >= 0 and score > 0]

    def save(self, prefix):
        prefix = Path(prefix)
        faiss.write_index(self.index, str(prefix.with_suffix(".faiss")))
        prefix.with_suffix(".json").write_text(json.dumps({"dimension": self.dimension, "documents": self.documents}))

    @classmethod
    def load(cls, prefix):
        prefix = Path(prefix)
        data = json.loads(prefix.with_suffix(".json").read_text())
        obj = cls(data["documents"], data["dimension"])
        obj.index = faiss.read_index(str(prefix.with_suffix(".faiss")))
        return obj
