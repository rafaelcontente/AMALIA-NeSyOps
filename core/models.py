from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class TraceID(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str = Field(default_factory=lambda: str(uuid4()))
    def __str__(self) -> str: return self.id
    def __hash__(self) -> int: return hash(self.id)

class Evidence(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str = Field(default_factory=lambda: str(uuid4()))
    source: str
    content: Any
    content_hash: str  # CORRIGIDO: era content_type
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utc_now)
    def __hash__(self) -> int: return hash(self.model_dump_json())

class RuleFormat(str, Enum):
    SHACL = "shacl"; DATALOG = "datalog"; OPA = "opa"; PYTHON = "python"; SMT = "smt"

class RuleSeverity(str, Enum):
    HARD = "hard"; SOFT = "soft"

class Rule(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    format: RuleFormat
    body: str
    severity: RuleSeverity = RuleSeverity.HARD
    timestamp: datetime = Field(default_factory=utc_now)
    def __hash__(self) -> int: return hash(self.model_dump_json())

class Proposal(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str = Field(default_factory=lambda: str(uuid4()))
    trace_id: TraceID
    agent: str
    content: Any
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=utc_now)
    def __hash__(self) -> int: return hash(self.model_dump_json())

class VerdictStatus(str, Enum):
    APPROVED = "approved"; REJECTED = "rejected"; ESCALATED = "escalated"; REPAIRED = "repaired"

class Verdict(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str = Field(default_factory=lambda: str(uuid4()))
    trace_id: TraceID
    proposal_id: str
    status: VerdictStatus
    reason: str
    rules_evaluated: list[str] = Field(default_factory=list)
    rules_violated: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=utc_now)
    def __hash__(self) -> int: return hash(self.model_dump_json())

class Escalation(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str = Field(default_factory=lambda: str(uuid4()))
    trace_id: TraceID
    verdict_id: str
    reason: str
    assigned_to: str
    timestamp: datetime = Field(default_factory=utc_now)
    def __hash__(self) -> int: return hash(self.model_dump_json())

class Decision(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str = Field(default_factory=lambda: str(uuid4()))
    trace_id: TraceID
    proposal: Proposal
    verdict: Verdict
    explanation: str
    model_version: str
    prompt_version: str
    rules_version: str
    timestamp: datetime = Field(default_factory=utc_now)
    def __hash__(self) -> int: return hash(self.model_dump_json())
