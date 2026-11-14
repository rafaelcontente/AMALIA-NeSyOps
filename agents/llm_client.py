"""
Interface LLM independente do modelo (AMALIA por defeito, outros por routing).
Para o MVP, usa um Mock determinístico para testes.
"""
from typing import Dict, Any, List, Optional
from core.models import TraceID

class LLMClient:
    """Cliente LLM com routing e mock para testes."""
    
    def __init__(self, model_name: str = "amalia-7b-v1", responses: List[Dict[str, Any]] = None):
        self.model_name = model_name
        self.responses = responses or []
        self.call_count = 0
    
    def generate(self, prompt: str, trace_id: TraceID) -> Dict[str, Any]:
        """Gera resposta do LLM. Em produção, chama o endpoint real."""
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return response
        
        # Fallback: resposta inválida para testar validação
        self.call_count += 1
        return {"raw_output": "invalid_response", "confidence": 0.1}
