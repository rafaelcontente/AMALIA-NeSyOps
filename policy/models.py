"""
Modelos de dados para regras formais.
Cada regra é imutável após criação e tem ciclo de vida controlado.
"""
from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict, field_validator, ValidationInfo

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RuleSeverity(str, Enum):
    """Severidade da regra."""
    HARD = "hard"
    SOFT = "soft"


class RuleStatus(str, Enum):
    """Ciclo de vida da regra."""
    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    ACTIVE = "active"
    REVOKED = "revoked"


class RuleTestCase(BaseModel):
    """Caso de teste para uma regra."""
    model_config = ConfigDict(frozen=True)
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    input_data: dict[str, Any]
    expected_result: bool
    description: str = ""


class Rule(BaseModel):
    """Regra formal com ciclo de vida completo."""
    model_config = ConfigDict(frozen=True)
    
    id: str = Field(default_factory=lambda: f"R-{str(uuid4())[:8]}")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    name: str
    description: str
    severity: RuleSeverity
    status: RuleStatus = RuleStatus.DRAFT
    
    author: str
    reviewer: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    valid_from: datetime = Field(default_factory=utc_now)
    valid_until: Optional[datetime] = None
    
    source_norm: str = ""
    source_text: str = ""
    
    expression: str
    priority: int = 100
    exceptions: list[str] = Field(default_factory=list)
    test_cases: list[RuleTestCase] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    
    @field_validator("reviewer")
    @classmethod
    def reviewer_must_differ_from_author(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        """Maker-checker: revisor não pode ser o autor."""
        if v and info.data.get('author') and v == info.data.get('author'):
            raise ValueError('Revisor não pode ser o autor da regra')
        return v


class RuleSet(BaseModel):
    """Conjunto de regras versionado."""
    model_config = ConfigDict(frozen=True)
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    name: str
    rules: list[Rule] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
