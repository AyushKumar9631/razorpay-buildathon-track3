"""
AI Agent Tools - Functions that agents can use to interact with the system.
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
import json

from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.risk import RevenueRisk
from app.models.intervention import Intervention
from app.models.audit import AuditTrail


def get_customer_history(customer_id: str, db: Session) -> Dict[str, Any]:
    """Get customer transaction history and profile."""
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()

    if not customer:
        return {"error": "Customer not found"}

    # Get recent transactions
    transactions = db.query(Transaction).filter(
        Transaction.customer_id == customer.id
    ).order_by(Transaction.created_at.desc()).limit(10).all()

    # Get failed transactions count
    failed_count = db.query(Transaction).filter(
        and_(
            Transaction.customer_id == customer.id,
            Transaction.status == 'failed'
        )
    ).count()

    # Get successful transactions
    success_count = db.query(Transaction).filter(
        and_(
            Transaction.customer_id == customer.id,
            Transaction.status == 'success'
        )
    ).count()

    return {
        "customer_id": customer.customer_id,
        "email": customer.email,
        "name": customer.name,
        "tier": customer.tier,
        "customer_type": customer.customer_type,
        "lifetime_value": float(customer.lifetime_value) if customer.lifetime_value else 0,
        "total_transactions": customer.total_transactions,
        "failed_transactions": failed_count,
        "successful_transactions": success_count,
        "success_rate": round((success_count / max(customer.total_transactions, 1)) * 100, 2),
        "recent_transactions": [
            {
                "transaction_id": t.transaction_id,
                "amount": float(t.amount),
                "status": t.status,
                "payment_method": t.payment_method,
                "created_at": t.created_at.isoformat()
            }
            for t in transactions
        ],
        "communication_preferences": customer.communication_preferences or {}
    }


def get_transaction_details(transaction_id: str, db: Session) -> Dict[str, Any]:
    """Get detailed transaction information."""
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id
    ).first()

    if not transaction:
        return {"error": "Transaction not found"}

    return {
        "transaction_id": transaction.transaction_id,
        "amount": float(transaction.amount),
        "currency": transaction.currency,
        "status": transaction.status,
        "payment_method": transaction.payment_method,
        "failure_reason": transaction.failure_reason,
        "failure_code": transaction.failure_code,
        "created_at": transaction.created_at.isoformat(),
        "metadata": transaction.metadata or {}
    }


def calculate_risk_score(
    customer_data: Dict[str, Any],
    transaction_data: Dict[str, Any],
    risk_type: str
) -> float:
    """Calculate risk score (0-100) for revenue loss likelihood."""
    score = 50.0  # Base score

    # Factor 1: Customer success rate
    success_rate = customer_data.get("success_rate", 50)
    if success_rate > 80:
        score -= 15
    elif success_rate < 50:
        score += 20

    # Factor 2: Customer tier
    tier = customer_data.get("tier", "standard")
    if tier == "enterprise":
        score -= 10
    elif tier == "premium":
        score -= 5

    # Factor 3: Transaction amount vs LTV
    amount = transaction_data.get("amount", 0)
    ltv = customer_data.get("lifetime_value", 0)
    if ltv > 0 and amount / ltv < 0.1:
        score += 10  # Small transaction, higher risk of permanent loss

    # Factor 4: Failed transaction count
    failed_count = customer_data.get("failed_transactions", 0)
    if failed_count > 3:
        score += 15
    elif failed_count > 1:
        score += 5

    # Factor 5: Risk type specific
    if risk_type == "payment_failure":
        failure_code = transaction_data.get("failure_code", "")
        if "insufficient_funds" in failure_code.lower():
            score += 10
        elif "card_expired" in failure_code.lower():
            score -= 5  # Easy to fix
    elif risk_type == "checkout_abandon":
        score += 20  # Generally higher loss rate

    # Clamp between 0 and 100
    return max(0, min(100, score))


def calculate_customer_ltv(customer_id: str, db: Session) -> float:
    """Calculate customer lifetime value."""
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()

    if not customer:
        return 0.0

    # Sum of all successful transactions
    total = db.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.customer_id == customer.id,
            Transaction.status == 'success'
        )
    ).scalar()

    return float(total) if total else 0.0


def check_contact_frequency(customer_id: str, db: Session, days: int = 7) -> Dict[str, Any]:
    """Check how many times customer was contacted recently."""
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()

    if not customer:
        return {"error": "Customer not found"}

    # Count interventions in last N days
    since_date = datetime.utcnow() - timedelta(days=days)

    contact_count = db.query(Intervention).join(RevenueRisk).filter(
        and_(
            RevenueRisk.customer_id == customer.id,
            Intervention.executed_at >= since_date,
            Intervention.status == 'executed'
        )
    ).count()

    return {
        "customer_id": customer.customer_id,
        "contacts_last_7_days": contact_count,
        "limit_reached": contact_count >= 3,  # Max 3 contacts per week
        "days_checked": days
    }


def log_audit_trail(
    entity_type: str,
    entity_id: str,
    action: str,
    actor: str,
    details: Dict[str, Any],
    compliance_check: Dict[str, Any],
    db: Session
) -> bool:
    """Log action to audit trail."""
    try:
        audit = AuditTrail(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor=actor,
            details=details,
            compliance_check=compliance_check
        )
        db.add(audit)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error logging audit trail: {e}")
        return False


def get_similar_cases(risk_type: str, customer_tier: str, db: Session, limit: int = 5) -> List[Dict[str, Any]]:
    """Get similar past cases for learning."""
    # Find similar recovered risks
    similar_risks = db.query(RevenueRisk).join(Customer).filter(
        and_(
            RevenueRisk.risk_type == risk_type,
            RevenueRisk.status == 'recovered',
            Customer.tier == customer_tier
        )
    ).limit(limit).all()

    results = []
    for risk in similar_risks:
        # Get the intervention that worked
        successful_intervention = db.query(Intervention).filter(
            and_(
                Intervention.revenue_risk_id == risk.id,
                Intervention.outcome == 'success'
            )
        ).first()

        if successful_intervention:
            results.append({
                "risk_type": risk.risk_type,
                "risk_amount": float(risk.risk_amount),
                "customer_tier": customer_tier,
                "intervention_type": successful_intervention.intervention_type,
                "intervention_strategy": successful_intervention.intervention_strategy,
                "time_to_recovery": "calculated_from_timestamps"
            })

    return results


# Export all tools
AGENT_TOOLS = {
    "get_customer_history": get_customer_history,
    "get_transaction_details": get_transaction_details,
    "calculate_risk_score": calculate_risk_score,
    "calculate_customer_ltv": calculate_customer_ltv,
    "check_contact_frequency": check_contact_frequency,
    "log_audit_trail": log_audit_trail,
    "get_similar_cases": get_similar_cases,
}
