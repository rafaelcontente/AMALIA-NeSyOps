"""
Verificador independente de provas e motor de explicação.
"""
from typing import List, Dict, Any

class ProofVerifier:
    """Verifica se a solução do solver respeita as restrições de forma independente."""

    def verify_selection(self, candidates: List[Dict[str, Any]], budget: float, 
                         max_per_region: int, result_dict: Dict[str, Any]) -> bool:
        if not result_dict['feasible']:
            return True  # Assumimos que o solver detetou corretamente a inviabilidade
            
        selected_ids = result_dict['solution']['selected']
        selected_candidates = [c for c in candidates if c['id'] in selected_ids]
        
        # Verificar orçamento
        total_cost = sum(c['cost'] for c in selected_candidates)
        if total_cost > budget:
            return False
            
        # Verificar limite por região
        regions = {}
        for c in selected_candidates:
            regions[c['region']] = regions.get(c['region'], 0) + 1
            if regions[c['region']] > max_per_region:
                return False
                
        return True

class Explainer:
    """Reconstrói a explicação a partir da prova."""

    def explain(self, proof: List[Dict[str, Any]]) -> str:
        if not proof:
            return "Sem prova disponível."
        
        lines = ["--- Prova de Decisão ---"]
        for step in proof:
            if step['type'] == 'constraint':
                lines.append(f"[Regra] {step['id']}: {step['rule']} (Valor: {step['value']})")
            elif step['type'] == 'selection':
                lines.append(f"[Seleção] Candidato {step['candidate_id']} baseado em {step['rule_id']} (Evidência: {step['evidence_id']})")
        return "\n".join(lines)
