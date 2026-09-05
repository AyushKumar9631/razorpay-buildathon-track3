"""
Risk Detection Service - Monitors transactions and detects revenue at risk.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

from app.models.transaction import Transaction
from app.models.customer import Customer
from app.models.risk import RevenueRisk
from app.models.subscription import CustomerSubscription, AbandonedCart
from app.agents.orchestrator import RevenueRecoveryOrchestrator


class RiskDetectionService:
    """Service for detecting revenue risks."""

    def __init__(self, db: Session):
        self.db = db

    def detect_payment_failures(self) -> List[RevenueRisk]:
        """Detect failed payment transactions."""
        risks = []

        # Find failed transactions in the last 24 hours without existing risks
        cutoff_time = datetime.utcnow() - timedelta(hours=24)

        failed_transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.status == 'failed',
                Transaction.created_at >= cutoff_time
            )
        ).all()

        for transaction in failed_transactions:
            # Check if risk already exists
            existing_risk = self.db.query(RevenueRisk).filter(
                RevenueRisk.transaction_id == transaction.id
            ).first()

            if not existing_risk:
                # Create new risk
                risk = RevenueRisk(
                    transaction_id=transaction.id,
                    customer_id=transaction.customer_id,
                    risk_type='payment_failure',
                    risk_amount=transaction.amount,
                    status='active',
                    priority='high' if transaction.amount > 1000 else 'medium',
                    root_cause=transaction.failure_reason
                )
                self.db.add(risk)
                risks.append(risk)

        self.db.commit()
        return risks

    def detect_checkout_abandonment(self) -> List[RevenueRisk]:
        """Detect abandoned carts."""
        risks = []

        # Find abandoned carts in the last 3 hours
        cutoff_time = datetime.utcnow() - timedelta(hours=3)

        abandoned_carts = self.db.query(AbandonedCart).filter(
            and_(
                AbandonedCart.recovery_status == 'pending',
                AbandonedCart.abandoned_at >= cutoff_time
            )
        ).all()

        for cart in abandoned_carts:
            # Check if risk already exists
            existing_risk = self.db.query(RevenueRisk).filter(
                and_(
                    RevenueRisk.customer_id == cart.customer_id,
                    RevenueRisk.risk_type == 'checkout_abandon',
                    RevenueRisk.status == 'active'
                )
            ).first()

            if not existing_risk:
                # Create new risk
                risk = RevenueRisk(
                    customer_id=cart.customer_id,
                    risk_type='checkout_abandon',
                    risk_amount=cart.total_amount,
                    status='active',
                    priority='medium',
                    root_cause=f"Abandoned at {cart.abandonment_stage}"
                )
                self.db.add(risk)
                risks.append(risk)

        self.db.commit()
        return risks

    def detect_subscription_failures(self) -> List[RevenueRisk]:
        """Detect failed subscription renewals."""
        risks = []

        # Find subscriptions with failed status
        failed_subscriptions = self.db.query(CustomerSubscription).filter(
            CustomerSubscription.status == 'failed'
        ).all()

        for subscription in failed_subscriptions:
            # Check if risk already exists
            existing_risk = self.db.query(RevenueRisk).filter(
                and_(
                    RevenueRisk.customer_id == subscription.customer_id,
                    RevenueRisk.risk_type == 'subscription_failure',
                    RevenueRisk.status == 'active'
                )
            ).first()

            if not existing_risk:
                # Create new risk
                risk = RevenueRisk(
                    customer_id=subscription.customer_id,
                    risk_type='subscription_failure',
                    risk_amount=subscription.amount,
                    status='active',
                    priority='high' if subscription.amount > 500 else 'medium',
                    root_cause=f"Subscription payment failed - {subscription.failed_attempts} attempts"
                )
                self.db.add(risk)
                risks.append(risk)

        self.db.commit()
        return risks

    def run_detection(self) -> Dict[str, Any]:
        """Run all detection methods."""
        print("Running risk detection...")

        payment_risks = self.detect_payment_failures()
        cart_risks = self.detect_checkout_abandonment()
        subscription_risks = self.detect_subscription_failures()

        total_detected = len(payment_risks) + len(cart_risks) + len(subscription_risks)

        return {
            "total_detected": total_detected,
            "payment_failures": len(payment_risks),
            "checkout_abandonment": len(cart_risks),
            "subscription_failures": len(subscription_risks),
            "timestamp": datetime.utcnow().isoformat()
        }

    def process_risk_with_ai(self, risk_id: str) -> Dict[str, Any]:
        """Process a specific risk with AI agent."""
        risk = self.db.query(RevenueRisk).filter(RevenueRisk.id == risk_id).first()

        if not risk:
            return {"error": "Risk not found"}

        # Get associated transaction if exists
        transaction_id = "unknown"
        if risk.transaction_id:
            transaction = self.db.query(Transaction).filter(
                Transaction.id == risk.transaction_id
            ).first()
            if transaction:
                transaction_id = transaction.transaction_id

        # Get customer
        customer = self.db.query(Customer).filter(
            Customer.id == risk.customer_id
        ).first()

        if not customer:
            return {"error": "Customer not found"}

        # Run AI agent workflow
        orchestrator = RevenueRecoveryOrchestrator(self.db)
        result = orchestrator.run(
            risk_id=str(risk.id),
            risk_type=risk.risk_type,
            transaction_id=transaction_id,
            customer_id=customer.customer_id
        )

        # Update risk with AI diagnosis
        risk.ai_diagnosis = result['diagnosis']
        risk.risk_score = result['diagnosis'].get('recovery_probability', 50)

        self.db.commit()

        return result
