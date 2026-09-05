from sqlalchemy import Column, String, DateTime, Numeric, Integer, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Transaction(Base):
    """Transaction model for storing payment transactions."""

    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default='INR')
    status = Column(String(50), nullable=False, index=True)  # pending, success, failed, abandoned
    payment_method = Column(String(50))  # card, upi, netbanking, wallet
    failure_reason = Column(String(255))
    failure_code = Column(String(50))
    metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="transactions")

    # Indexes
    __table_args__ = (
        Index('idx_transaction_status_created', 'status', 'created_at'),
        Index('idx_transaction_customer_status', 'customer_id', 'status'),
    )

    def __repr__(self):
        return f"<Transaction {self.transaction_id} - {self.status} - {self.amount}>"
