"""Observabilidade: tracing, métricas e correlation IDs."""
import uuid
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

class CorrelationIDGenerator:
    """Gera correlation IDs únicos."""
    
    def generate(self) -> str:
        return str(uuid.uuid4())


@dataclass
class Span:
    """Um span de tracing."""
    span_id: str
    operation: str
    correlation_id: str
    parent_id: Optional[str] = None
    entity_id: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    def set_attribute(self, key: str, value: Any):
        self.attributes[key] = value
    
    def end(self):
        self.end_time = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "span_id": self.span_id,
            "operation": self.operation,
            "correlation_id": self.correlation_id,
            "parent_id": self.parent_id,
            "entity_id": self.entity_id,
            "attributes": self.attributes,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": (self.end_time - self.start_time) * 1000 if self.end_time else None,
        }


class TracingManager:
    """Gere spans de tracing."""
    
    def __init__(self):
        self.spans: List[Span] = []
    
    def start_span(
        self,
        operation: str,
        correlation_id: str = None,
        entity_id: str = None,
        parent_span: Optional[Span] = None,
    ) -> Span:
        span = Span(
            span_id=str(uuid.uuid4()),
            operation=operation,
            correlation_id=correlation_id or str(uuid.uuid4()),
            parent_id=parent_span.span_id if parent_span else None,
            entity_id=entity_id,
        )
        self.spans.append(span)
        return span
    
    def get_spans(self, correlation_id: str = None) -> List[Dict[str, Any]]:
        spans = self.spans
        if correlation_id:
            spans = [s for s in spans if s.correlation_id == correlation_id]
        return [s.to_dict() for s in spans]


class MetricsCollector:
    """Coleta contadores e histogramas."""
    
    def __init__(self):
        self.counters: Dict[str, Dict[str, int]] = {}
        self.histograms: Dict[str, Dict[str, List[float]]] = {}
    
    def _tag_key(self, tags: Dict[str, str]) -> str:
        return ":".join(f"{k}={v}" for k, v in sorted(tags.items())) if tags else "_default"
    
    def increment_counter(self, name: str, tags: Dict[str, str] = None):
        tags = tags or {}
        key = self._tag_key(tags)
        self.counters.setdefault(name, {})[key] = self.counters.get(name, {}).get(key, 0) + 1
    
    def observe_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        tags = tags or {}
        key = tags.get("endpoint", self._tag_key(tags))
        self.histograms.setdefault(name, {}).setdefault(key, []).append(value)
    
    def get_metrics(self) -> Dict[str, Any]:
        result = {}
        for name, values in self.counters.items():
            result[name] = values
        
        for name, buckets in self.histograms.items():
            result[name] = {}
            for key, values in buckets.items():
                result[name][key] = {
                    "count": len(values),
                    "sum": sum(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                }
        
        return result
