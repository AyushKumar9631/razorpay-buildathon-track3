from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.database import Base


class AuditTrail(Base):
    """Audit trail model for compliance logging."""

    __tablename__ = "audit_trail"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False, index=True)  # risk, intervention, recovery
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    actor = Column(String(100), nullable=False)  # ai_agent, system, user_id
    details = Column(JSONB, nullable=False)
    compliance_check = Column(JSONB)  # Which rules were checked
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Indexes
    __table_args__ = (
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_timestamp', 'timestamp'),
    )

    def __repr__(self):
        return f"<AuditTrail {self.entity_type} - {self.action} - {self.timestamp}>"


class ComplianceRule(Base):
    """Compliance rules model for storing business rules."""

    __tablename__ = "compliance_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_name = Column(String(100), unique=True, nullable=False)
    rule_type = Column(String(50), nullable=False)  # stopping_rule, escalation_rule, rate_limit
    conditions = Column(JSONB, nullable=False)
    actions = Column(JSONB, nullable=False)
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<ComplianceRule {self.rule_name} - {self.rule_type}>"
