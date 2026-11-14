"""
Gerador de explicações fiéis ao trace.
Duas vistas: cidadão (linguagem simples) e auditor (técnica com IDs).
Cada frase tem referência explícita ao trace.
"""
from typing import Dict, Any, List
from core.models import Decision, VerdictStatus
from datetime import datetime

class ExplanationGenerator:
    """Gera explicações a partir do trace da decisão."""
    
    def __init__(self):
        pass
    
    def generate(self, decision: Decision, evidences: List[Dict] = None) -> Dict[str, str]:
        """
        Gera duas vistas da explicação: citizen e auditor.
        Retorna: {"citizen": str, "auditor": str}
        """
        evidences = evidences or []
        
        # Vista do cidadão
        citizen_view = self._generate_citizen_view(decision, evidences)
        
        # Vista do auditor
        auditor_view = self._generate_auditor_view(decision, evidences)
        
        return {
            "citizen": citizen_view,
            "auditor": auditor_view
        }
    
    def _generate_citizen_view(self, decision: Decision, evidences: List[Dict]) -> str:
        """Gera explicação para o cidadão em linguagem simples."""
        
        # Extrair informações do verdict
        verdict = decision.verdict
        reason = verdict.reason or "Decisão processada com sucesso"
        
        # Construir referências
        references = []
        for rule_id in verdict.rules_evaluated:
            references.append(f"Regra {rule_id}")
        for evidence in evidences:
            references.append(f"Evidência {evidence.get('id', 'N/A')}")
        
        references_str = ", ".join(references) if references else "Nenhuma referência disponível"
        
        if verdict.status == VerdictStatus.APPROVED:
            return self._citizen_approved(reason, references_str)
        else:
            return self._citizen_rejected(reason, references_str, verdict)
    
    def _citizen_approved(self, reason: str, references: str) -> str:
        """Template para decisão aprovada."""
        return f"""
A sua candidatura foi **aprovada**.

**Motivo:** {reason}

**Próximos passos:** Aguarde notificação oficial com detalhes de implementação.

**Referências:** {references}

Se tiver dúvidas, contacte-nos através dos canais oficiais.
"""
    
    def _citizen_rejected(self, reason: str, references: str, verdict) -> str:
        """Template para decisão indeferida (Adverse Action Notice)."""
        
        # Fundamentação legal baseada nas regras violadas
        legal_basis = "Legislação aplicável ao procedimento"
        if verdict.rules_violated:
            legal_basis = f"Artigos violados: {', '.join(verdict.rules_violated)}"
        
        return f"""
A sua candidatura foi **indeferida**.

**Motivo da decisão:** {reason}

**Fundamentação legal:** {legal_basis}

**Direito de recurso:** Tem direito a reclamar desta decisão no prazo de 15 dias úteis, nos termos do artigo 123.º do Código do Procedimento Administrativo.

**Referências:** {references}

Para exercer o seu direito de recurso, contacte-nos através dos canais oficiais.
"""
    
    def _generate_auditor_view(self, decision: Decision, evidences: List[Dict]) -> str:
        """Gera explicação técnica para auditor com IDs e versões."""
        
        verdict = decision.verdict
        
        # Construir árvore de prova
        proof_tree_lines = []
        proof_tree_lines.append(f"├─ Proposal ID: {decision.proposal.id}")
        proof_tree_lines.append(f"├─ Agent: {decision.proposal.agent}")
        proof_tree_lines.append(f"├─ Confidence: {decision.proposal.confidence or 'N/A'}")
        proof_tree_lines.append(f"├─ Verdict ID: {verdict.id}")
        proof_tree_lines.append(f"└─ Status: {verdict.status.value}")
        proof_tree = "\n".join(proof_tree_lines)
        
        # Regras avaliadas
        rules_evaluated = "\n".join([f"  - {rule_id}" for rule_id in verdict.rules_evaluated]) or "  Nenhuma"
        
        # Regras violadas
        rules_violated = "\n".join([f"  - {rule_id}" for rule_id in verdict.rules_violated]) or "  Nenhuma"
        
        # Evidências
        evidences_str = "\n".join([f"  - {e.get('id', 'N/A')}: {e.get('source', 'N/A')}" for e in evidences]) or "  Nenhuma"
        
        return f"""
=== VISTA DO AUDITOR ===

**Trace ID:** {decision.trace_id.id}
**Timestamp:** {decision.timestamp.isoformat()}
**Status:** {verdict.status.value}

**Versões do sistema:**
- Modelo: {decision.model_version}
- Prompt: {decision.prompt_version}
- Regras: {decision.rules_version}

**Árvore de prova:**
{proof_tree}

**Regras avaliadas:**
{rules_evaluated}

**Regras violadas:**
{rules_violated}

**Evidências consultadas:**
{evidences_str}
"""
