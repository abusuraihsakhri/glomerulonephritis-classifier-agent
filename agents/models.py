"""
Pydantic v2 schemas and data definitions for Glomerulonephritis Classifier Agent.
Domain: Nephrology & Dialysis Systems
Standard: KDIGO / KDOQI Clinical Practice Guidelines
"""
import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class UrgencyLevel(str, Enum):
    ROUTINE = "ROUTINE"
    ELEVATED = "ELEVATED_RISK"
    CRITICAL_STAT = "CRITICAL_STAT_PANIC"


class SystemIntegrityStatus(str, Enum):
    VALIDATED = "VALIDATED_OPTIMAL"
    DISCORDANT = "DISCORDANT_ANOMALY"
    RECALIBRATION_REQUIRED = "RECALIBRATION_REQUIRED"


class SystemTaskPayload(BaseModel):
    task_id: str = Field(..., min_length=1, max_length=128, description="Unique task / case identifier")
    target_identifier: str = Field(..., min_length=1, max_length=128, description="Entity, patient key, or genomic/cryptographic target")
    primary_metric: float = Field(..., description="Primary domain measurement or score")
    secondary_metric: float = Field(default=0.0, description="Secondary kinetic or confidence score")
    status_descriptor: str = Field(default="NOMINAL", max_length=64, description="Status code or phenotype descriptor")
    is_critical_flag: bool = Field(default=False, description="Emergency escalation or high priority trigger")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    @field_validator("task_id", "target_identifier", "status_descriptor")
    @classmethod
    def sanitize_string_fields(cls, v: str) -> str:
        """Prevent injection via control characters in string fields."""
        if any(ord(c) < 32 and c not in "\t\n\r" for c in v):
            raise ValueError("Field contains invalid control characters")
        return v.strip()

    @field_validator("primary_metric", "secondary_metric")
    @classmethod
    def validate_metrics(cls, v: float) -> float:
        """Ensure metric values are finite and within safe bounds."""
        if not isinstance(v, (int, float)):
            raise ValueError("Metric must be a numeric value")
        if v != v or v == float('inf') or v == float('-inf'):  # NaN/Inf check
            raise ValueError("Metric must be a finite number")
        if abs(v) > 1e9:
            raise ValueError("Metric value exceeds safe bounds")
        return float(v)


class AgentAlert(BaseModel):
    alert_id: str
    origin_worker: str
    urgency: UrgencyLevel
    summary: str
    technical_details: str
    actionable_remediation: str
    standard_reference: str = "KDIGO / KDOQI Clinical Practice Guidelines"
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ConsensusDossier(BaseModel):
    dossier_id: str
    system_slug: str = "glomerulonephritis-classifier-agent"
    domain: str = "Nephrology & Dialysis Systems"
    task_id: str
    target_identifier: str
    overall_urgency: UrgencyLevel
    integrity_status: SystemIntegrityStatus
    total_alerts: int
    critical_alerts_count: int
    alerts: List[AgentAlert]
    standard_reference: str = "KDIGO / KDOQI Clinical Practice Guidelines"
    consensus_summary: str
    audit_hash: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
