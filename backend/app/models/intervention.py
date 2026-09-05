from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Intervention(Base):
    """Intervention model for tracking recovery actions."""

    __tablename__ = "interventions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    revenue_risk_id = Column(UUID(as_uuid=True), ForeignKey('revenue_risks.id'), nullable=False, index=True)
    intervention_type = Column(String(50), nullable=False)  # email, sms, payment_retry, voice_call, payment_plan
    intervention_strategy = Column(String(100))  # immediate_retry, dunning_sequence, personalized_offer
    channel = Column(String(50))  # email, sms, whatsapp, voice
    content = Column(Text)  # Generated message/script
    scheduled_at = Column(DateTime(timezone=True), index=True)
    executed_at = Column(DateTime(timezone=True), index=True)
    status = Column(String(50), nullable=False, default='pending', index=True)  # pending, executed, failed, skipped
    outcome = Column(String(50))  # success, failure, no_response, opted_out
    ai_reasoning = Column(Text)  # Why this intervention was chosen
    cost = Column(Numeric(8, 2))  # Cost of intervention
    extra_data = Column(JSONB)  # Renamed from 'metadata' to avoid SQLAlchemy conflict

    # Relationships
    revenue_risk = relationship("RevenueRisk", back_populates="interventions")

    # Indexes
    __table_args__ = (
        Index('idx_intervention_status_scheduled', 'status', 'scheduled_at'),
        Index('idx_intervention_risk_status', 'revenue_risk_id', 'status'),
    )

    def __repr__(self):
        return f"<Intervention {self.intervention_type} - {self.status}>"


class RecoveryOutcome(Base):
    """Recovery outcome model for tracking recovery results."""

    __tablename__ = "recovery_outcomes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    revenue_risk_id = Column(UUID(as_uuid=True), ForeignKey('revenue_risks.id'), nullable=False, unique=True, index=True)
    intervention_id = Column(UUID(as_uuid=True), ForeignKey('interventions.id'), nullable=True)
    recovered_amount = Column(Numeric(12, 2), nullable=False, default=0)
    recovered_at = Column(DateTime(timezone=True), index=True)
    recovery_method = Column(String(100))
    time_to_recovery = Column(Numeric(10, 2))  # Hours to recovery
    customer_feedback = Column(Text)

    # Relationships
    revenue_risk = relationship("RevenueRisk", back_populates="recovery_outcome")

    def __repr__(self):
        return f"<RecoveryOutcome {self.recovered_amount} - {self.recovery_method}>"
