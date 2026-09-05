from sqlalchemy import Column, String, DateTime, Numeric, Integer, ForeignKey, Index, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Customer(Base):
    """Customer model for storing customer information."""

    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20))
    name = Column(String(255))
    customer_type = Column(String(20), default='B2C')  # B2C, B2B
    tier = Column(String(20), default='standard', index=True)  # standard, premium, enterprise
    lifetime_value = Column(Numeric(12, 2), default=0)
    total_transactions = Column(Integer, default=0)
    failed_transactions = Column(Integer, default=0)
    communication_preferences = Column(JSONB)
    extra_data = Column(JSONB)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    transactions = relationship("Transaction", back_populates="customer")
    revenue_risks = relationship("RevenueRisk", back_populates="customer")
    subscriptions = relationship("CustomerSubscription", back_populates="customer")
    abandoned_carts = relationship("AbandonedCart", back_populates="customer")

    def __repr__(self):
        return f"<Customer {self.customer_id} - {self.email}>"
