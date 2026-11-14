"""Red teaming e testes adversariais."""
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class AttackResult(BaseModel):
    attack_type: str
    attack_description: str
    input_data: Dict[str, Any]
    original_decision: Dict[str, Any] = None
    attacked_decision: Dict[str, Any] = None
    success: bool
    timestamp: datetime = Field(default_factory=utc_now)

class RedTeamAttacker:
    def __init__(self):
        self.attacks_executed: List[AttackResult] = []
    
    def prompt_injection_attack(self, decision_fn, base_input: Dict[str, Any],
                               injection_texts: List[str]) -> List[AttackResult]:
        results = []
        
        try:
            original_decision = decision_fn(base_input)
        except Exception as e:
            original_decision = {"error": str(e)}
        
        for injection_text in injection_texts:
            attacked_input = base_input.copy()
            
            if "document_text" in attacked_input:
                attacked_input["document_text"] = attacked_input["document_text"] + "\n\n" + injection_text
            else:
                attacked_input["injected_text"] = injection_text
            
            try:
                attacked_decision = decision_fn(attacked_input)
                success = self._decisions_differ(original_decision, attacked_decision)
                
                result = AttackResult(
                    attack_type="prompt_injection",
                    attack_description=f"Injeção: {injection_text[:50]}...",
                    input_data=attacked_input,
                    original_decision=original_decision,
                    attacked_decision=attacked_decision,
                    success=success
                )
            except Exception as e:
                result = AttackResult(
                    attack_type="prompt_injection",
                    attack_description=f"Injeção causou erro",
                    input_data=attacked_input,
                    original_decision=original_decision,
                    attacked_decision=None,
                    success=False
                )
            
            results.append(result)
            self.attacks_executed.append(result)
        
        return results
    
    def _decisions_differ(self, decision1: Dict[str, Any], decision2: Dict[str, Any]) -> bool:
        key_fields = ["decision", "status", "approved", "rejected", "score"]
        for field in key_fields:
            if field in decision1 and field in decision2:
                if decision1[field] != decision2[field]:
                    return True
        return False
    
    def get_attack_summary(self) -> Dict[str, Any]:
        if not self.attacks_executed:
            return {"total_attacks": 0, "successful_attacks": 0}
        
        successful = sum(1 for attack in self.attacks_executed if attack.success)
        return {
            "total_attacks": len(self.attacks_executed),
            "successful_attacks": successful,
            "success_rate": successful / len(self.attacks_executed)
        }
