"""
Pipeline de ingestão: orquestra parsers, normalização, segurança e deduplicação.
"""
from typing import List, Dict, Any
from core.models import Evidence
from ingest.parsers import parse_document, compute_hash
from ingest.normalizer import normalize_text
from ingest.security import check_prompt_injection

# Registo simples de deduplicação (em produção: base de dados ou vector store)
_ingested_hashes = set()

def ingest_document(file_path: str) -> List[Evidence]:
    """
    Ingerir um documento, validar, normalizar e devolver Evidence imutável.
    """
    fragments = parse_document(file_path)
    evidences = []
    
    for frag in fragments:
        # 1. Deduplicação
        if frag["hash"] in _ingested_hashes:
            continue  # Já ingerido
        
        # 2. Segurança (Prompt Injection)
        injection_detected, reason = check_prompt_injection(frag["content"])
        
        # 3. Normalização
        clean_content = normalize_text(frag["content"])
        
        # 4. Criar Evidence
        evidence = Evidence(
            source=frag["source"],
            content={
                "text": clean_content,
                "page": frag["page"],
                "injection_detected": injection_detected,
                "injection_reason": reason
            },
            content_hash=frag["hash"],
            metadata={
                "doc_id": frag["doc_id"],
                "is_untrusted": True  # Regra de ouro: tudo é não confiável
            }
        )
        evidences.append(evidence)
        _ingested_hashes.add(frag["hash"])
        
    return evidences

def reset_ingest_registry():
    """Apenas para testes."""
    _ingested_hashes.clear()
