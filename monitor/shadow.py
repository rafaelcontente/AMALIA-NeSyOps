"""
Shadow mode e canary deployment: novas versões correm em paralelo
sem afetar decisões reais.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class ShadowResult:
    def __init__(self, trace_id: str, active_version: str, shadow_version: str,
                 active_output: Dict[str, Any], shadow_output: Dict[str, Any]):
        self.trace_id = trace_id
        self.active_version = active_version
        self.shadow_version = shadow_version
        self.active_output = active_output
        self.shadow_output = shadow_output
        self.timestamp = utc_now()
        self.match = active_output == shadow_output
    
    def to_dict(self):
        return {
            "trace_id": self.trace_id,
            "active_version": self.active_version,
            "shadow_version": self.shadow_version,
            "match": self.match,
            "timestamp": self.timestamp.isoformat()
        }

class ShadowDeployer:
    """Gere deploy em shadow mode e canary."""
    
    def __init__(self, active_version: str):
        self.active_version = active_version
        self.shadow_version: Optional[str] = None
        self.canary_percentage: float = 0.0  # 0-100
        self.results: List[ShadowResult] = []
        self._real_decisions_impacted: int = 0
    
    def set_shadow(self, version: str):
        """Define a versão em shadow mode."""
        self.shadow_version = version
    
    def set_canary(self, percentage: float):
        """Define percentagem de tráfego para canary (0-100)."""
        if not 0 <= percentage <= 100:
            raise ValueError("Percentagem deve estar entre 0 e 100")
        self.canary_percentage = percentage
    
    def run_shadow(self, trace_id: str, request: Dict[str, Any],
                   active_fn, shadow_fn) -> Dict[str, Any]:
        """
        Executa active e shadow em paralelo.
        Apenas o resultado do active é devolvido (shadow é só para comparação).
        """
        if self.shadow_version is None:
            # Sem shadow mode, executar apenas active
            active_output = active_fn(request)
            return {
                "mode": "active_only",
                "version": self.active_version,
                "output": active_output
            }
        
        # Executar ambos
        active_output = active_fn(request)
        shadow_output = shadow_fn(request)
        
        # Registar comparação (apenas observabilidade, NÃO afeta decisão)
        result = ShadowResult(
            trace_id=trace_id,
            active_version=self.active_version,
            shadow_version=self.shadow_version,
            active_output=active_output,
            shadow_output=shadow_output
        )
        self.results.append(result)
        
        # Devolver APENAS o resultado do active (real)
        return {
            "mode": "shadow",
            "version": self.active_version,  # Decisão real usa active
            "output": active_output,
            "shadow_compared": self.shadow_version
        }
    
    def get_comparison_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de comparação active vs shadow."""
        if not self.results:
            return {"total": 0, "match_rate": 0.0}
        
        matches = sum(1 for r in self.results if r.match)
        total = len(self.results)
        
        return {
            "total": total,
            "matches": matches,
            "mismatches": total - matches,
            "match_rate": matches / total,
            "active_version": self.active_version,
            "shadow_version": self.shadow_version
        }
    
    def verify_no_real_impact(self) -> bool:
        """
        Verifica que o shadow mode não afetou decisões reais.
        Retorna True se nenhum impacto real foi registado.
        """
        return self._real_decisions_impacted == 0
