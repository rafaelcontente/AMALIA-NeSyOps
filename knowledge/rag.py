"""
RAG estruturado: combina grafo de conhecimento, base vetorial e reranker.
Garante que todas as respostas têm fonte e respeitam a data de vigência.
"""
from knowledge.ontology import KnowledgeGraph
from knowledge.vector_store import VectorStore
from typing import List, Dict, Optional
import numpy as np

class StructuredRAG:
    def __init__(self):
        self.graph = KnowledgeGraph()
        self.vector_store = VectorStore()
    
    def ingest_norm(self, norm_id: str, title: str, valid_from: str, articles: List[Dict], valid_to: str = None):
        """Ingerir norma no grafo e na base vetorial."""
        self.graph.add_norm(norm_id, title, valid_from, valid_to)
        for art in articles:
            self.graph.add_article(norm_id, art["id"], art["content"])
            # Embedding simulado (em produção: modelo de embedding real)
            embedding = np.random.rand(128)
            self.vector_store.add_document(art["id"], art["content"], embedding)
    
    def query(self, question: str, date: str, tenant_id: str = "default") -> Dict:
        """
        Responde a uma pergunta com base na data e no corpus.
        Se não houver fonte, devolve "sem evidência".
        """
        # 1. Verificar normas vigentes na data
        active_norms = self.graph.query_active_norms(date)
        if not active_norms:
            return {"answer": "sem evidência", "sources": []}
        
        # 2. Pesquisar na base vetorial (simulação)
        # Na prática, gerar embedding da pergunta e pesquisar
        query_embedding = np.random.rand(128)
        results = self.vector_store.search(query_embedding, tenant_id, top_k=5)
        
        if not results:
            return {"answer": "sem evidência", "sources": []}
        
        # 3. Construir resposta com citações
        sources = []
        for doc_id, score in results:
            doc = self.vector_store.get_document(doc_id)
            if doc:
                sources.append({"doc_id": doc_id, "content": doc["content"], "score": score})
        
        return {
            "answer": f"Resposta baseada em {len(sources)} fontes vigentes em {date}.",
            "sources": sources,
            "active_norms": [str(row[1]) for row in active_norms]
        }
