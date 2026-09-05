"""
Intervention Service - Manages intervention execution and tracking.
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

from app.models.risk import RevenueRisk
from app.models.intervention import Intervention, RecoveryOutcome
from app.models.customer import Customer
from app.agents.orchestrator import RevenueRecoveryOrchestrator


class InterventionService:
    """Service for managing interventions."""

    def __init__(self, db: Session):
        self.db = db

    def create_intervention(
        self,
        risk_id: str,
        intervention_type: str,
        strategy: str,
        channel: str,
        content: str,
        ai_reasoning: str,
        scheduled_at: Optional[datetime] = None
    ) -> Intervention:
        """Create a new intervention."""
        intervention = Intervention(
            revenue_risk_id=risk_id,
            intervention_type=intervention_type,
            intervention_strategy=strategy,
            channel=channel,
            content=content,
            ai_reasoning=ai_reasoning,
            scheduled_at=scheduled_at or datetime.utcnow(),
            status='pending'
        )

        self.db.add(intervention)
        self.db.commit()
        self.db.refresh(intervention)

        return intervention

    def execute_intervention(self, intervention_id: str) -> Dict[str, Any]:
        """Execute an intervention."""
        intervention = self.db.query(Intervention).filter(
            Intervention.id == intervention_id
        ).first()

        if not intervention:
            return {"error": "Intervention not found"}

        if intervention.status != 'pending':
            return {"error": f"Intervention already {intervention.status}"}

        # For now, simulate execution
        # In production, this would:
        # - Send actual emails via SendGrid
        # - Send SMS via Twilio
        # - Trigger payment retries via payment gateway
        # - Make voice calls for high-value customers

        intervention.executed_at = datetime.utcnow()
        intervention.status = 'executed'
        intervention.outcome = 'pending'  # Will be updated when customer responds

        self.db.commit()

        return {
            "intervention_id": str(intervention.id),
            "status": intervention.status,
            "executed_at": intervention.executed_at.isoformat(),
            "type": intervention.intervention_type,
            "channel": intervention.channel,
            "simulated": True  # Will be False in production
        }

    def record_recovery(
        self,
        risk_id: str,
        intervention_id: Optional[str],
        recovered_amount: float,
        recovery_method: str
    ) -> RecoveryOutcome:
        """Record a successful recovery."""
        risk = self.db.query(RevenueRisk).filter(RevenueRisk.id == risk_id).first()

        if not risk:
            raise ValueError("Risk not found")

        # Calculate time to recovery
        detected_at = risk.detected_at
        recovered_at = datetime.utcnow()
        time_to_recovery = (recovered_at - detected_at).total_seconds() / 3600  # hours

        # Create recovery outcome
        outcome = RecoveryOutcome(
            revenue_risk_id=risk_id,
            intervention_id=intervention_id,
            recovered_amount=recovered_amount,
            recovered_at=recovered_at,
            recovery_method=recovery_method,
            time_to_recovery=time_to_recovery
        )

        # Update risk status
        risk.status = 'recovered'

        # Update intervention outcome if provided
        if intervention_id:
            intervention = self.db.query(Intervention).filter(
                Intervention.id == intervention_id
            ).first()
            if intervention:
                intervention.outcome = 'success'

        self.db.add(outcome)
        self.db.commit()
        self.db.refresh(outcome)

        return outcome

    def get_intervention_queue(self, limit: int = 50) -> list:
        """Get pending interventions ready to execute."""
        interventions = self.db.query(Intervention).filter(
            Intervention.status == 'pending',
            Intervention.scheduled_at <= datetime.utcnow()
        ).order_by(Intervention.scheduled_at).limit(limit).all()

        return [
            {
                "id": str(i.id),
                "risk_id": str(i.revenue_risk_id),
                "type": i.intervention_type,
                "strategy": i.intervention_strategy,
                "channel": i.channel,
                "scheduled_at": i.scheduled_at.isoformat(),
                "ai_reasoning": i.ai_reasoning
            }
            for i in interventions
        ]

    def process_risk_and_create_intervention(self, risk_id: str) -> Dict[str, Any]:
        """Process a risk with AI and create recommended intervention."""
        risk = self.db.query(RevenueRisk).filter(RevenueRisk.id == risk_id).first()

        if not risk:
            return {"error": "Risk not found"}

        # Get customer
        customer = self.db.query(Customer).filter(
            Customer.id == risk.customer_id
        ).first()

        if not customer:
            return {"error": "Customer not found"}

        # Get transaction if exists
        transaction_id = "unknown"
        if risk.transaction_id:
            from app.models.transaction import Transaction
            transaction = self.db.query(Transaction).filter(
                Transaction.id == risk.transaction_id
            ).first()
            if transaction:
                transaction_id = transaction.transaction_id

        # Run AI orchestrator
        orchestrator = RevenueRecoveryOrchestrator(self.db)
        ai_result = orchestrator.run(
            risk_id=str(risk.id),
            risk_type=risk.risk_type,
            transaction_id=transaction_id,
            customer_id=customer.customer_id
        )

        # Update risk with AI diagnosis
        risk.ai_diagnosis = ai_result['diagnosis']
        risk.risk_score = ai_result['diagnosis'].get('recovery_probability', 50)

        # Create intervention if approved
        if ai_result['approved']:
            recommendation = ai_result['recommended_intervention']
            message_content = ai_result['execution_result'].get('message_content', {})

            intervention = self.create_intervention(
                risk_id=str(risk.id),
                intervention_type=recommendation['recommended_intervention'],
                strategy=recommendation['strategy'],
                channel=recommendation['channel'],
                content=str(message_content),
                ai_reasoning=recommendation['reasoning'],
                scheduled_at=datetime.utcnow()  # Immediate execution
            )

            self.db.commit()

            return {
                "risk_id": str(risk.id),
                "intervention_created": True,
                "intervention_id": str(intervention.id),
                "ai_diagnosis": ai_result['diagnosis'],
                "recommendation": recommendation,
                "compliance_approved": True
            }
        else:
            self.db.commit()

            return {
                "risk_id": str(risk.id),
                "intervention_created": False,
                "ai_diagnosis": ai_result['diagnosis'],
                "compliance_approved": False,
                "compliance_check": ai_result['compliance_check']
            }
