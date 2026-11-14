"""
Agente de extração: transforma texto livre em Proposal estruturada.
"""
from typing import Dict, Any
from core.models import TraceID, Proposal, Evidence
from agents.llm_client import LLMClient
from agents.tools import ToolRegistry
import hashlib

class ExtractionAgent:
    """Agente que extrai campos de texto e gera Proposal."""
    
    def __init__(self, llm_client: LLMClient, tool_registry: ToolRegistry, max_retries: int = 3):
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.max_retries = max_retries
    
    def extract(self, text: str, trace_id: TraceID) -> Dict[str, Any]:
        """Extrai campos do texto e gera Proposal."""
        prompt = f"Extrair campos do seguinte texto:\n{text}"
        
        for attempt in range(self.max_retries):
            response = self.llm_client.generate(prompt, trace_id)
            
            # Validar schema da resposta
            if not self._validate_response(response):
                continue
            
            # Criar Evidence para cada campo
            evidences = []
            for field_name, field_value in response.get("fields", {}).items():
                content = f"{field_name}: {field_value}"
                evidence = Evidence(
                    source="extraction_agent",
                    content={"field": field_name, "value": field_value, "text": text},
                    content_hash=hashlib.sha256(content.encode()).hexdigest()
                )
                evidences.append(evidence)
            
            # Criar Proposal
            proposal = Proposal(
                trace_id=trace_id,
                agent=self.llm_client.model_name,
                content=response.get("fields", {}),
                confidence=response.get("confidence", 0.5),
                evidence_ids=[e.id for e in evidences]
            )
            
            return {
                "status": "completed",
                "output": {
                    "proposal": proposal,
                    "evidences": evidences
                }
            }
        
        # Falha após max_retries
        return {
            "status": "failed",
            "reason": "max_retries_exceeded"
        }
    
    def _validate_response(self, response: Dict[str, Any]) -> bool:
        """Valida se a resposta do LLM tem o schema esperado."""
        if not isinstance(response, dict):
            return False
        if "fields" not in response or not isinstance(response["fields"], dict):
            return False
        if "confidence" not in response:
            return False
        return True
