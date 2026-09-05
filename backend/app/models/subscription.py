from sqlalchemy import Column, String, DateTime, Numeric, Integer, ForeignKey, Index, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class CustomerSubscription(Base):
    """Customer subscription model for recurring payments."""

    __tablename__ = "customer_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False, index=True)
    subscription_id = Column(String(100), unique=True, nullable=False)
    plan_name = Column(String(100))
    amount = Column(Numeric(12, 2), nullable=False)
    billing_cycle = Column(String(20))  # monthly, quarterly, annual
    status = Column(String(50), nullable=False, index=True)  # active, failed, cancelled, paused
    next_billing_date = Column(Date, index=True)
    failed_attempts = Column(Integer, default=0)
    last_failure_date = Column(DateTime(timezone=True))
    grace_period_end = Column(Date)

    # Relationships
    customer = relationship("Customer", back_populates="subscriptions")

    # Indexes
    __table_args__ = (
        Index('idx_subscription_status_billing', 'status', 'next_billing_date'),
    )

    def __repr__(self):
        return f"<Subscription {self.subscription_id} - {self.status}>"


class AbandonedCart(Base):
    """Abandoned cart model for checkout abandonment tracking."""

    __tablename__ = "abandoned_carts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(String(100), unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=True, index=True)
    session_id = Column(String(100))
    items = Column(JSONB, nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    abandoned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    abandonment_stage = Column(String(50))  # product_view, cart, checkout_info, payment
    recovery_status = Column(String(50), default='pending', index=True)  # pending, contacted, recovered, expired
    recovered_at = Column(DateTime(timezone=True))

    # Relationships
    customer = relationship("Customer", back_populates="abandoned_carts")

    # Indexes
    __table_args__ = (
        Index('idx_cart_status_abandoned', 'recovery_status', 'abandoned_at'),
    )

    def __repr__(self):
        return f"<AbandonedCart {self.cart_id} - {self.total_amount}>"
