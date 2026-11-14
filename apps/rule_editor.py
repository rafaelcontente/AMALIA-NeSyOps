"""Editor de regras para juristas: texto ↔ regra ↔ testes."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class RuleDraft(BaseModel):
    """Rascunho de regra."""
    id: Optional[str] = None
    version: str = "draft"
    name: str
    description: str
    source_text: str
    expression: str
    severity: str = "hard"
    test_cases: List[Dict[str, Any]] = []

class RuleEditor:
    """Editor de regras para juristas: texto ↔ regra ↔ testes."""
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.drafts: Dict[str, RuleDraft] = {}
    
    def create_draft(self, jurist_id: str, name: str, description: str,
                    source_text: str, expression: str,
                    severity: str = "hard") -> RuleDraft:
        """Cria rascunho de nova regra."""
        draft = RuleDraft(
            name=name,
            description=description,
            source_text=source_text,
            expression=expression,
            severity=severity
        )
        
        draft_id = f"draft-{len(self.drafts) + 1}"
        self.drafts[draft_id] = draft
        
        return draft
    
    def add_test_case(self, draft_id: str, input_data: Dict[str, Any],
                     expected_result: bool, description: str = "") -> Dict[str, Any]:
        """Adiciona caso de teste a um rascunho."""
        if draft_id not in self.drafts:
            raise ValueError(f"Rascunho {draft_id} não encontrado")
        
        draft = self.drafts[draft_id]
        test_case = {
            "input_data": input_data,
            "expected_result": expected_result,
            "description": description
        }
        
        draft.test_cases.append(test_case)
        return test_case
    
    def validate_expression(self, draft_id: str) -> Dict[str, Any]:
        """Valida expressão da regra via API."""
        if draft_id not in self.drafts:
            raise ValueError(f"Rascunho {draft_id} não encontrado")
        
        draft = self.drafts[draft_id]
        result = self.api_client.validate_rule_expression(draft.expression)
        
        return {
            "valid": result.get("valid", False),
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", [])
        }
    
    def run_tests(self, draft_id: str) -> Dict[str, Any]:
        """Executa casos de teste via API."""
        if draft_id not in self.drafts:
            raise ValueError(f"Rascunho {draft_id} não encontrado")
        
        draft = self.drafts[draft_id]
        results = self.api_client.run_rule_tests(
            expression=draft.expression,
            test_cases=draft.test_cases
        )
        
        return results
    
    def submit_for_review(self, draft_id: str, jurist_id: str) -> Dict[str, Any]:
        """Submete rascunho para revisão via API."""
        if draft_id not in self.drafts:
            raise ValueError(f"Rascunho {draft_id} não encontrado")
        
        draft = self.drafts[draft_id]
        result = self.api_client.submit_rule_for_review(
            draft=draft.model_dump(),
            jurist_id=jurist_id
        )
        
        return result
    
    def get_draft(self, draft_id: str) -> Optional[RuleDraft]:
        """Retorna rascunho por ID."""
        return self.drafts.get(draft_id)
    
    def list_drafts(self) -> List[RuleDraft]:
        """Lista todos os rascunhos."""
        return list(self.drafts.values())
