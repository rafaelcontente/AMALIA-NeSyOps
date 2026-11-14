"""
Validador de explicações: garante que todas as afirmações mapeiam para o trace.
Zero afirmações órfãs.
"""
from typing import Dict, Any, List, Set
import re

class ExplanationValidator:
    """Valida que a explicação é fiel ao trace."""
    
    def validate(self, explanation: str, trace: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida a explicação contra o trace.
        Retorna: {"valid": bool, "orphan_claims": list, "coverage": float}
        """
        
        # Extrair todas as referências da explicação
        # Padrão: "Regra R-XXX", "Evidência EV-XXX", "Trace ID XXX"
        references = self._extract_references(explanation)
        
        # Verificar que todas as referências existem no trace
        trace_ids = self._extract_trace_ids(trace)
        
        orphan_claims = []
        for ref in references:
            if ref not in trace_ids:
                orphan_claims.append(ref)
        
        # Calcular cobertura (quantas referências do trace estão na explicação)
        coverage = len([r for r in references if r in trace_ids]) / max(len(references), 1)
        
        return {
            "valid": len(orphan_claims) == 0,
            "orphan_claims": orphan_claims,
            "coverage": coverage,
            "total_references": len(references),
            "trace_ids_found": len(trace_ids)
        }
    
    def _extract_references(self, text: str) -> Set[str]:
        """Extrai referências do texto da explicação."""
        references = set()
        
        # Padrão para regras: R-XXX, R-XXX-YYY
        rule_pattern = r'R-\d+(?:-\w+)?'
        references.update(re.findall(rule_pattern, text))
        
        # Padrão para evidências: EV-XXX
        evidence_pattern = r'EV-\w+'
        references.update(re.findall(evidence_pattern, text))
        
        # Padrão para trace IDs: T-XXX (UUIDs curtos)
        trace_pattern = r'T-[a-f0-9-]+'
        references.update(re.findall(trace_pattern, text))
        
        return references
    
    def _extract_trace_ids(self, trace: Dict[str, Any]) -> Set[str]:
        """Extrai todos os IDs do trace."""
        ids = set()
        
        # IDs diretos
        if "trace_id" in trace:
            ids.add(trace["trace_id"])
        if "proposal_id" in trace:
            ids.add(trace["proposal_id"])
        if "verdict_id" in trace:
            ids.add(trace["verdict_id"])
        
        # IDs de regras
        if "rules_evaluated" in trace:
            ids.update(trace["rules_evaluated"])
        if "rules_violated" in trace:
            ids.update(trace["rules_violated"])
        
        # IDs de evidências
        if "evidences" in trace:
            for ev in trace["evidences"]:
                if "id" in ev:
                    ids.add(ev["id"])
        
        return ids
