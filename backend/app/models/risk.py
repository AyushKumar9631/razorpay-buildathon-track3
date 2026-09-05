from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class RevenueRisk(Base):
    """Revenue risk model for tracking revenue at risk."""

    __tablename__ = "revenue_risks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey('transactions.id'), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False, index=True)
    risk_type = Column(String(50), nullable=False, index=True)  # payment_failure, checkout_abandon, subscription_failure, overdue_invoice, mandate_failure
    risk_amount = Column(Numeric(12, 2), nullable=False)
    risk_score = Column(Numeric(5, 2))  # 0-100 predicted likelihood of permanent loss
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    status = Column(String(50), nullable=False, default='active', index=True)  # active, recovered, lost, expired
    root_cause = Column(Text)
    ai_diagnosis = Column(JSONB)  # AI agent's analysis
    priority = Column(String(20), default='medium', index=True)  # low, medium, high, critical

    # Relationships
    customer = relationship("Customer", back_populates="revenue_risks")
    interventions = relationship("Intervention", back_populates="revenue_risk")
    recovery_outcome = relationship("RecoveryOutcome", back_populates="revenue_risk", uselist=False)

    # Indexes
    __table_args__ = (
        Index('idx_risk_status_detected', 'status', 'detected_at'),
        Index('idx_risk_type_status', 'risk_type', 'status'),
        Index('idx_risk_priority_status', 'priority', 'status'),
    )

    def __repr__(self):
        return f"<RevenueRisk {self.risk_type} - {self.risk_amount} - {self.status}>"
