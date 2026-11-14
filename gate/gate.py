"""
Orquestração do portão: validação + plano de ação + aprovação humana quando necessário.
"""
from typing import Dict, Any, Optional, Callable
from core.models import Proposal, Verdict, VerdictStatus, TraceID
from gate.validator import GateValidator
from gate.planner import FailurePlanner, FailPlan
from datetime import datetime, timezone

class Gate:
    """Portão único de saída do sistema."""
    
    def __init__(self, validator: GateValidator, planner: FailurePlanner = None,
                 timeout_seconds: float = 5.0):
        self.validator = validator
        self.planner = planner or FailurePlanner()
        self.timeout_seconds = timeout_seconds
    
    def evaluate(self, proposal: Proposal, context: Dict[str, Any] = None,
                 repair_attempt: int = 0) -> Dict[str, Any]:
        """
        Avalia uma proposta e devolve um plano de ação.
        Se falhar com timeout ou exceção, recusa sempre (segurança).
        """
        context = context or {}
        
        try:
            # Validação com timeout implícito (simulado para MVP)
            results = self.validator.validate(proposal, context)
            
            # Todas as camadas passaram
            if all(r.passed for r in results):
                verdict = Verdict(
                    trace_id=proposal.trace_id,
                    proposal_id=proposal.id,
                    status=VerdictStatus.APPROVED,
                    reason="Todas as 5 camadas de validação passaram",
                    rules_evaluated=[r.layer for r in results],
                    rules_violated=[]
                )
                return {
                    "verdict": verdict,
                    "validation_results": results,
                    "needs_human_approval": False
                }
            
            # Algo falhou: decidir plano
            plan = self.planner.decide_plan(results, repair_attempt)
            
            status_map = {
                FailPlan.REPAIR: VerdictStatus.REPAIRED,
                FailPlan.DEGRADE: VerdictStatus.APPROVED,  # Com flags de degradação
                FailPlan.ESCALATE: VerdictStatus.ESCALATED,
                FailPlan.REFUSE: VerdictStatus.REJECTED
            }
            
            verdict = Verdict(
                trace_id=proposal.trace_id,
                proposal_id=proposal.id,
                status=status_map[plan["action"]],
                reason=plan["reason"],
                rules_evaluated=[r.layer for r in results],
                rules_violated=[r.layer for r in results if not r.passed]
            )
            
            return {
                "verdict": verdict,
                "plan": plan,
                "validation_results": results,
                "needs_human_approval": plan.get("needs_approval", False)
            }
        
        except Exception as e:
            # FALHA DO VALIDADOR: recusa sempre (nunca deixa passar)
            verdict = Verdict(
                trace_id=proposal.trace_id,
                proposal_id=proposal.id,
                status=VerdictStatus.REJECTED,
                reason=f"Erro no validador — recusado por segurança: {str(e)}",
                rules_evaluated=[],
                rules_violated=[]
            )
            return {
                "verdict": verdict,
                "plan": {"action": FailPlan.REFUSE, "reason": str(e)},
                "validation_results": [],
                "needs_human_approval": False,
                "validator_error": True
            }
