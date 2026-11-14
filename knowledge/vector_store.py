"""
Base vetorial para RAG com isolamento multi-tenant e pesquisa por similaridade.
Implementação simplificada com numpy para demonstração (em produção: FAISS/Qdrant).
"""
import numpy as np
from typing import List, Dict, Tuple

class VectorStore:
    def __init__(self):
        self.documents: Dict[str, Dict] = {}
        self.embeddings: Dict[str, np.ndarray] = {}
    
    def add_document(self, doc_id: str, content: str, embedding: np.ndarray, tenant_id: str = "default"):
        """Adiciona documento com isolamento por tenant."""
        self.documents[doc_id] = {"content": content, "tenant_id": tenant_id}
        self.embeddings[doc_id] = embedding
    
    def search(self, query_embedding: np.ndarray, tenant_id: str = "default", top_k: int = 5) -> List[Tuple[str, float]]:
        """Pesquisa vetorial com isolamento de tenant."""
        scores = []
        for doc_id, emb in self.embeddings.items():
            if self.documents[doc_id]["tenant_id"] == tenant_id:
                similarity = np.dot(query_embedding, emb) / (np.linalg.norm(query_embedding) * np.linalg.norm(emb))
                scores.append((doc_id, float(similarity)))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def get_document(self, doc_id: str) -> Dict:
        return self.documents.get(doc_id)
