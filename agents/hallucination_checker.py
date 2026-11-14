"""Validação anti-alucinação: verifica entidades contra o grafo RDF."""
from typing import Dict, Any, List, Set
from rdflib import Graph


class HallucinationChecker:
    """
    Valida entidades extraídas pelo LLM contra o grafo de conhecimento.
    
    Se o LLM "inventar" uma entidade que não existe no grafo, a proposta é rejeitada.
    """
    
    def __init__(self, knowledge_graph: Graph):
        self.graph = knowledge_graph
    
    def check_entities(
        self,
        extracted_entities: Dict[str, Any],
        entity_type: str = "all",
    ) -> Dict[str, Any]:
        """
        Verifica se as entidades extraídas existem no grafo.
        
        Args:
            extracted_entities: {"person": "João", "organization": "Câmara de Lisboa", ...}
            entity_type: tipo de entidade a validar (ou "all" para todos)
        
        Returns:
            {"valid": True, "hallucinated": []}
            ou {"valid": False, "hallucinated": ["organization:Câmara de Lisboa"]}
        """
        hallucinated = []
        
        for etype, value in extracted_entities.items():
            if entity_type != "all" and etype != entity_type:
                continue
            
            if not self._entity_exists(etype, value):
                hallucinated.append(f"{etype}:{value}")
        
        return {
            "valid": len(hallucinated) == 0,
            "hallucinated": hallucinated,
            "checked_count": len(extracted_entities),
        }
    
    def _entity_exists(self, entity_type: str, value: str) -> bool:
        """Verifica se uma entidade existe no grafo RDF."""
        # Procurar por triplets onde o valor aparece como objeto
        query = f"""
        SELECT ?s WHERE {{
            ?s ?p "{value}" .
        }}
        LIMIT 1
        """
        results = list(self.graph.query(query))
        return len(results) > 0
