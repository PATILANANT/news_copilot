import os
import pickle
import faiss
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from config import config


class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.index_path = os.path.join(config.VECTOR_STORE_PATH, "index.faiss")
        self.meta_path = os.path.join(config.VECTOR_STORE_PATH, "metadata.pkl")

        self.index = faiss.IndexFlatL2(self.dim)
        self.documents = []
        self.metadata = []

        self._load()

    def _load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "rb") as f:
                data = pickle.load(f)
                self.documents = data["documents"]
                self.metadata = data["metadata"]

    def _save(self):
        os.makedirs(config.VECTOR_STORE_PATH, exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(
                {"documents": self.documents, "metadata": self.metadata}, f
            )

    def clear(self):
        self.index = faiss.IndexFlatL2(self.dim)
        self.documents = []
        self.metadata = []
        self._save()

    def add_documents(self, docs: List[Dict[str, Any]]):
        texts = []
        metas = []

        for d in docs:
            text = f"{d['title']}\n{d['content']}"
            if len(text) < 50:
                continue

            texts.append(text)
            metas.append({
                "title": d["title"],
                "url": d["url"],
                "source": d["source"],
                "timestamp": d["timestamp"]
            })

        if not texts:
            return

        embeddings = self.model.encode(texts, convert_to_numpy=True)
        self.index.add(embeddings.astype("float32"))

        self.documents.extend(texts)
        self.metadata.extend(metas)
        self._save()

    def search(self, query: str, k: int = 5):
        if self.index.ntotal == 0:
            return []

        q_emb = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(q_emb.astype("float32"), k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                score = 1 / (1 + distances[0][i])
                results.append({
                    "content": self.documents[idx],
                    "metadata": self.metadata[idx],
                    "score": float(score)
                })
        return results
