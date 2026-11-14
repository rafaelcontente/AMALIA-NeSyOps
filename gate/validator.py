"""
Validador de 5 camadas: estrutura, consistência, regras, plausibilidade, afirmações.
Toda a validação é determinística. LLM nunca é a fonte de verdade.
"""
from typing import Dict, Any, List, Optional
from core.models import Proposal, Verdict, VerdictStatus, TraceID
from policy.registry import RuleRegistry
from policy.engine import RuleEvaluator
from datetime import datetime, timezone

class ValidationResult:
    def __init__(self, layer: str, passed: bool, reason: str = "", details: Dict = None):
        self.layer = layer
        self.passed = passed
        self.reason = reason
        self.details = details or {}

class GateValidator:
    """Portão de validação com 5 camadas."""
    
    def __init__(self, rule_registry: RuleRegistry = None):
        self.rule_registry = rule_registry
    
    def validate(self, proposal: Proposal, context: Dict[str, Any] = None) -> List[ValidationResult]:
        """Executa as 5 camadas de validação em sequência."""
        results = []
        context = context or {}
        
        # Camada 1: Estrutura (schema)
        results.append(self._validate_structure(proposal))
        if not results[-1].passed:
            return results
        
        # Camada 2: Consistência
        results.append(self._validate_consistency(proposal))
        if not results[-1].passed:
            return results
        
        # Camada 3: Regras de domínio (via policy/)
        results.append(self._validate_domain_rules(proposal, context))
        if not results[-1].passed:
            return results
        
        # Camada 4: Plausibilidade (incerteza, drift)
        results.append(self._validate_plausibility(proposal))
        if not results[-1].passed:
            return results
        
        # Camada 5: Verificação de afirmações (cada número tem fonte)
        results.append(self._validate_claims(proposal, context))
        
        return results
    
    def _validate_structure(self, proposal: Proposal) -> ValidationResult:
        """Camada 1: Validação de schema (já feita pelo Pydantic, mas reconfirmamos)."""
        try:
            if not proposal.content:
                return ValidationResult("structure", False, "Proposal sem conteúdo")
            if proposal.trace_id is None:
                return ValidationResult("structure", False, "Proposal sem trace_id")
            return ValidationResult("structure", True)
        except Exception as e:
            return ValidationResult("structure", False, f"Erro de estrutura: {str(e)}")
    
    def _validate_consistency(self, proposal: Proposal) -> ValidationResult:
        """Camada 2: Consistência interna dos campos."""
        content = proposal.content
        if not isinstance(content, dict):
            return ValidationResult("consistency", True)  # Não-dict não tem contradições internas
        
        # Exemplo: se tem data_fim e data_inicio, fim >= inicio
        if "data_inicio" in content and "data_fim" in content:
            try:
                if content["data_fim"] < content["data_inicio"]:
                    return ValidationResult("consistency", False, 
                        f"data_fim ({content['data_fim']}) < data_inicio ({content['data_inicio']})")
            except (TypeError, ValueError):
                pass
        
        # Exemplo: valor_total = soma de parcelas
        if "valor_total" in content and "parcelas" in content:
            try:
                soma = sum(content["parcelas"])
                if abs(soma - content["valor_total"]) > 0.01:
                    return ValidationResult("consistency", False,
                        f"valor_total ({content['valor_total']}) != soma parcelas ({soma})")
            except (TypeError, ValueError):
                pass
        
        return ValidationResult("consistency", True)
    
    def _validate_domain_rules(self, proposal: Proposal, context: Dict) -> ValidationResult:
        """Camada 3: Regras de domínio via policy/ (AST seguro)."""
        if not self.rule_registry or not self.rule_registry.rule_sets:
            return ValidationResult("domain_rules", True, "Sem regras configuradas")
        
        try:
            # Usar a última versão do conjunto de regras
            latest_version = list(self.rule_registry.rule_sets.keys())[-1]
            rule_set = self.rule_registry.get_rule_set(latest_version)
            evaluator = RuleEvaluator(rule_set)
            
            # Preparar contexto de avaliação
            eval_context = {}
            if isinstance(proposal.content, dict):
                eval_context.update(proposal.content)
            
            results = evaluator.evaluate(eval_context)
            violations = [r for r in results if r['severity'] == 'hard' and not r['passed']]
            
            if violations:
                return ValidationResult("domain_rules", False,
                    f"Violação de regras duras: {[v['rule_id'] for v in violations]}",
                    {"violations": violations})
            
            return ValidationResult("domain_rules", True)
        except Exception as e:
            return ValidationResult("domain_rules", False, f"Erro na avaliação de regras: {str(e)}")
    
    def _validate_plausibility(self, proposal: Proposal) -> ValidationResult:
        """Camada 4: Plausibilidade (incerteza muito baixa = sinal de alerta)."""
        if proposal.confidence is not None and proposal.confidence < 0.3:
            return ValidationResult("plausibility", False,
                f"Confiança muito baixa: {proposal.confidence} < 0.3")
        return ValidationResult("plausibility", True)
    
    def _validate_claims(self, proposal: Proposal, context: Dict) -> ValidationResult:
        """Camada 5: Verificação de afirmações — cada número/citação deve ter fonte."""
        claims = context.get("claims_to_verify", [])
        evidences = context.get("available_evidences", [])
        evidence_ids = {e.id for e in evidences}
        
        unverified = []
        for claim in claims:
            # Se a claim exige evidência e não tem source válida
            if claim.get("requires_evidence", True):
                source = claim.get("source_id")
                if not source or source not in evidence_ids:
                    unverified.append(claim)
        
        if unverified:
            return ValidationResult("claims", False,
                f"Afirmações sem fonte rastreável: {len(unverified)}",
                {"unverified_claims": unverified})
        
        return ValidationResult("claims", True)
