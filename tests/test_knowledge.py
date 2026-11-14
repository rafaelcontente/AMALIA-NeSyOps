import pytest
from datetime import datetime
from knowledge.rag import StructuredRAG

@pytest.fixture
def rag_system():
    """Inicializa o sistema RAG com dados de teste."""
    rag = StructuredRAG()
    
    # Norma antiga (vigente até 2025)
    rag.ingest_norm(
        norm_id="norm-001",
        title="Lei Antiga",
        valid_from="2020-01-01",
        valid_to="2025-12-31",
        articles=[
            {"id": "art-001-1", "content": "Artigo 1 da Lei Antiga: regra X."},
            {"id": "art-001-2", "content": "Artigo 2 da Lei Antiga: regra Y."}
        ]
    )
    
    # Norma nova (vigente a partir de 2026)
    rag.ingest_norm(
        norm_id="norm-002",
        title="Lei Nova",
        valid_from="2026-01-01",
        articles=[
            {"id": "art-002-1", "content": "Artigo 1 da Lei Nova: regra Z."}
        ]
    )
    
    return rag

# ─── Teste 1: Temporalidade (data passada devolve norma antiga) ─────────────
def test_temporal_query_returns_active_norm(rag_system):
    """Teste 1: uma pergunta com data passada devolve a versão da norma vigente nessa data."""
    # Data no passado (2024)
    result_2024 = rag_system.query("Qual a regra aplicável?", date="2024-06-15")
    
    assert "Lei Antiga" in result_2024["active_norms"], "Deve retornar a Lei Antiga em 2024"
    assert "Lei Nova" not in result_2024["active_norms"], "Não deve retornar a Lei Nova em 2024"
    
    # Data no futuro (2026)
    result_2026 = rag_system.query("Qual a regra aplicável?", date="2026-06-15")
    
    assert "Lei Nova" in result_2026["active_norms"], "Deve retornar a Lei Nova em 2026"
    assert "Lei Antiga" not in result_2026["active_norms"], "Não deve retornar a Lei Antiga em 2026"

# ─── Teste 2: Sem evidência (pergunta sem fonte devolve "sem evidência") ────
def test_no_evidence_when_no_source(rag_system):
    """Teste 2: uma pergunta sem fonte no corpus devolve 'sem evidência'."""
    # Simular tenant sem documentos
    result = rag_system.query("Pergunta sobre tema inexistente", date="2024-06-15", tenant_id="empty_tenant")
    
    assert result["answer"] == "sem evidência", "Deve devolver 'sem evidência' quando não há fontes"
    assert len(result["sources"]) == 0, "Não deve haver fontes citadas"

# ─── Teste 3: RAG Evals (recall e citações válidas) ─────────────────────────
def test_rag_evals_recall_and_citations(rag_system):
    """Teste 3: nos RAG Evals, recall@5 >= 0.90 e todas as citações apontam para excerto existente."""
    # Golden set de perguntas e fontes esperadas
    golden_set = [
        {"question": "Sobre regra X", "expected_doc": "art-001-1", "date": "2024-01-01"},
        {"question": "Sobre regra Z", "expected_doc": "art-002-1", "date": "2026-01-01"}
    ]
    
    correct_retrievals = 0
    total_queries = len(golden_set)
    
    for item in golden_set:
        result = rag_system.query(item["question"], date=item["date"])
        
        # Verificar se a fonte esperada está nos top 5 resultados
        retrieved_docs = [s["doc_id"] for s in result["sources"]]
        if item["expected_doc"] in retrieved_docs:
            correct_retrievals += 1
        
        # Verificar que todas as citações apontam para excertos existentes
        for source in result["sources"]:
            doc = rag_system.vector_store.get_document(source["doc_id"])
            assert doc is not None, f"Citação {source['doc_id']} não existe na base vetorial"
            assert "content" in doc and len(doc["content"]) > 0, "Excerto deve ter conteúdo"
    
    recall_at_5 = correct_retrievals / total_queries
    assert recall_at_5 >= 0.90, f"Recall@5 deve ser >= 0.90, mas foi {recall_at_5}"
