"""
Registo de regras com controlo de ciclo de vida e maker-checker.
"""
from typing import Optional
from datetime import datetime, timezone
from policy.models import Rule, RuleSet, RuleStatus, RuleTestCase


class RuleRegistry:
    """Gestão de regras com validação de ciclo de vida."""
    
    def __init__(self):
        self.rules: dict[str, Rule] = {}
        self.rule_sets: dict[str, RuleSet] = {}
    
    def create_rule(self, rule: Rule) -> Rule:
        """Cria nova regra em estado DRAFT."""
        if rule.id in self.rules:
            raise ValueError(f"Regra {rule.id} já existe")
        
        if rule.status != RuleStatus.DRAFT:
            raise ValueError("Nova regra deve estar em estado DRAFT")
        
        self.rules[rule.id] = rule
        return rule
    
    def review_rule(self, rule_id: str, reviewer: str) -> Rule:
        """Transição: DRAFT → REVIEWED."""
        rule = self._get_rule(rule_id)
        
        if rule.status != RuleStatus.DRAFT:
            raise ValueError(f"Regra {rule_id} não está em DRAFT")
        
        if reviewer == rule.author:
            raise ValueError("Revisor não pode ser o autor")
        
        # Criar nova versão da regra (imutável)
        updated_rule = rule.model_copy(
            update={
                'status': RuleStatus.REVIEWED,
                'reviewer': reviewer
            }
        )
        self.rules[rule_id] = updated_rule
        return updated_rule
    
    def approve_rule(self, rule_id: str, approver: str) -> Rule:
        """Transição: REVIEWED → APPROVED."""
        rule = self._get_rule(rule_id)
        
        if rule.status != RuleStatus.REVIEWED:
            raise ValueError(f"Regra {rule_id} não está em REVIEWED")
        
        if approver != rule.reviewer:
            raise ValueError("Apenas o revisor pode aprovar")
        
        updated_rule = rule.model_copy(
            update={
                'status': RuleStatus.APPROVED,
                'approved_at': datetime.now(timezone.utc)
            }
        )
        self.rules[rule_id] = updated_rule
        return updated_rule
    
    def activate_rule(self, rule_id: str) -> Rule:
        """Transição: APPROVED → ACTIVE."""
        rule = self._get_rule(rule_id)
        
        if rule.status != RuleStatus.APPROVED:
            raise ValueError(f"Regra {rule_id} não está em APPROVED")
        
        # Validar que tem pelo menos 1 teste positivo e 1 negativo
        self._validate_test_coverage(rule)
        
        updated_rule = rule.model_copy(
            update={'status': RuleStatus.ACTIVE}
        )
        self.rules[rule_id] = updated_rule
        return updated_rule
    
    def revoke_rule(self, rule_id: str) -> Rule:
        """Transição: ACTIVE → REVOKED."""
        rule = self._get_rule(rule_id)
        
        if rule.status != RuleStatus.ACTIVE:
            raise ValueError(f"Regra {rule_id} não está em ACTIVE")
        
        updated_rule = rule.model_copy(
            update={'status': RuleStatus.REVOKED}
        )
        self.rules[rule_id] = updated_rule
        return updated_rule
    
    def _validate_test_coverage(self, rule: Rule):
        """Valida que a regra tem pelo menos 1 teste positivo e 1 negativo."""
        if not rule.test_cases:
            raise ValueError(f"Regra {rule.id} não tem casos de teste")
        
        has_positive = any(tc.expected_result for tc in rule.test_cases)
        has_negative = any(not tc.expected_result for tc in rule.test_cases)
        
        if not has_positive:
            raise ValueError(f"Regra {rule.id} precisa de pelo menos 1 teste positivo")
        
        if not has_negative:
            raise ValueError(f"Regra {rule.id} precisa de pelo menos 1 teste negativo")
    
    def _get_rule(self, rule_id: str) -> Rule:
        if rule_id not in self.rules:
            raise KeyError(f"Regra {rule_id} não encontrada")
        return self.rules[rule_id]
    
    def create_rule_set(self, name: str, version: str, rule_ids: list[str]) -> RuleSet:
        """Cria conjunto de regras versionado."""
        rules = [self.rules[rid] for rid in rule_ids if rid in self.rules]
        
        rule_set = RuleSet(
            name=name,
            version=version,
            rules=rules
        )
        
        self.rule_sets[version] = rule_set
        return rule_set
    
    def get_rule_set(self, version: str) -> RuleSet:
        if version not in self.rule_sets:
            raise KeyError(f"Conjunto de regras {version} não encontrado")
        return self.rule_sets[version]
