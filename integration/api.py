"""API REST para integração com sistemas externos."""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import json

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class DecisionRequest(BaseModel):
    """Request para criar uma decisão."""
    request_id: str
    entity_id: str
    user_id: str
    document_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: Optional[str] = None

class DecisionResponse(BaseModel):
    """Response com trace_id para polling."""
    trace_id: str
    status: str  # "processing", "completed", "failed"
    created_at: datetime = Field(default_factory=utc_now)

class DecisionResult(BaseModel):
    """Resultado completo de uma decisão."""
    trace_id: str
    status: str  # "approved", "rejected", "escalated"
    decision: Dict[str, Any]
    explanation: str
    created_at: datetime
    completed_at: datetime

class APIGateway:
    """Gateway de API que integra com o sistema de decisão."""
    
    def __init__(self, gate, idempotency_manager, tenant_manager):
        self.gate = gate
        self.idempotency_manager = idempotency_manager
        self.tenant_manager = tenant_manager
        self.requests: Dict[str, Dict[str, Any]] = {}
        self.results: Dict[str, DecisionResult] = {}
    
    def submit_decision(self, request: DecisionRequest) -> DecisionResponse:
        """
        Submete um pedido de decisão.
        
        Args:
            request: Pedido de decisão
        
        Returns:
            Response com trace_id para polling
        """
        # Verificar autorização do utilizador
        if not self.tenant_manager.verify_access(request.user_id, request.entity_id):
            raise PermissionError(
                f"Utilizador {request.user_id} não tem acesso a {request.entity_id}"
            )
        
        # Gerar trace_id
        trace_id = f"T-{request.request_id}"
        
        # Armazenar request
        self.requests[trace_id] = {
            "request": request,
            "status": "processing",
            "created_at": utc_now()
        }
        
        # Processar decisão (assíncrono - aqui simulado como síncrono)
        self._process_decision(trace_id, request)
        
        return DecisionResponse(
            trace_id=trace_id,
            status="processing"
        )
    
    def get_decision(self, trace_id: str, requesting_user_id: str) -> Optional[DecisionResult]:
        """
        Obtém resultado de uma decisão.
        
        Args:
            trace_id: ID do trace
            requesting_user_id: ID do utilizador que pede o resultado
        
        Returns:
            Resultado da decisão se completo e autorizado
        """
        if trace_id not in self.requests:
            return None
        
        request_data = self.requests[trace_id]
        request = request_data["request"]
        
        # Verificar autorização
        if not self.tenant_manager.verify_access(requesting_user_id, request.entity_id):
            raise PermissionError(
                f"Utilizador {requesting_user_id} não tem acesso a {trace_id}"
            )
        
        if trace_id not in self.results:
            return None
        
        return self.results[trace_id]
    
    def _process_decision(self, trace_id: str, request: DecisionRequest):
        """Processa uma decisão (chama o gate)."""
        # Verificar idempotência
        def process_fn(req_data, entity_id):
            # Criar proposal a partir do request
            from core.models import Proposal, TraceID
            
            proposal = Proposal(
                trace_id=TraceID(id=trace_id),
                agent="api_gateway",
                content={
                    "document_text": req_data["document_text"],
                    "metadata": req_data["metadata"]
                },
                confidence=1.0
            )
            
            # Chamar gate (todas as decisões passam pelo gate)
            gate_result = self.gate.evaluate(proposal, context={"entity_id": entity_id})
            
            return {
                "decision": gate_result["verdict"].model_dump(),
                "explanation": "Decisão processada via gate"
            }
        
        # Usar idempotência
        request_data = {
            "document_text": request.document_text,
            "metadata": request.metadata
        }
        
        idem_result = self.idempotency_manager.check_and_process(
            request_data,
            request.entity_id,
            process_fn
        )
        
        # Armazenar resultado
        result = DecisionResult(
            trace_id=trace_id,
            status=idem_result["result"]["decision"]["status"],
            decision=idem_result["result"]["decision"],
            explanation=idem_result["result"]["explanation"],
            created_at=self.requests[trace_id]["created_at"],
            completed_at=utc_now()
        )
        
        self.results[trace_id] = result
        self.requests[trace_id]["status"] = "completed"
