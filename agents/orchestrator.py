"""
Orquestrador de agentes com limite de passos e deteção de loops.
"""
from typing import Dict, Any, Optional
from core.models import TraceID

class AgentOrchestrator:
    """Orquestrador com limite de passos e deteção de loops."""
    
    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps
    
    def run(self, agent_func, initial_input: Dict[str, Any], trace_id: TraceID) -> Dict[str, Any]:
        """
        Executa o agente com limite de passos.
        Se atingir o limite, devolve "escalated".
        """
        current_input = initial_input
        history = []
        
        for step in range(1, self.max_steps + 1):
            # Detetar loop: se o input se repete
            input_hash = str(current_input)
            if input_hash in history:
                return {
                    "status": "loop_detected",
                    "step": step,
                    "trace_id": trace_id,
                    "history": history
                }
            history.append(input_hash)
            
            # Executar passo do agente
            result = agent_func(current_input, trace_id)
            
            # Verificar condição de terminação
            if result.get("status") == "completed":
                return {
                    "status": "completed",
                    "step": step,
                    "trace_id": trace_id,
                    "output": result.get("output")
                }
            
            # Preparar próximo passo
            current_input = result.get("next_input", {})
        
        # Limite atingido
        return {
            "status": "max_steps_reached",
            "step": self.max_steps,
            "trace_id": trace_id,
            "escalated": True
        }
