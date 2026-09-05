"""AI agent interaction endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.risk import RevenueRisk
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.intervention import Intervention
from app.models.audit import AuditTrail
from app.agents.orchestrator import RevenueRecoveryOrchestrator
from app.agents.tools import get_customer_history, get_transaction_details

router = APIRouter()


# Pydantic schemas
class AnalyzeRiskRequest(BaseModel):
    risk_id: str


class RecommendInterventionRequest(BaseModel):
    risk_id: str


class GenerateMessageRequest(BaseModel):
    intervention_type: str
    customer_id: str
    risk_type: str
    transaction_amount: Optional[float] = 0
    failure_reason: Optional[str] = ""


@router.post("/analyze")
async def analyze_risk(
    request: AnalyzeRiskRequest,
    db: Session = Depends(get_db)
):
    """Analyze a risk scenario using AI - returns diagnosis only."""
    risk = db.query(RevenueRisk).filter(RevenueRisk.id == request.risk_id).first()

    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    customer = db.query(Customer).filter(Customer.id == risk.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Get transaction if exists
    transaction_id = "unknown"
    if risk.transaction_id:
        transaction = db.query(Transaction).filter(Transaction.id == risk.transaction_id).first()
        if transaction:
            transaction_id = transaction.transaction_id

    # Run just the diagnosis part
    orchestrator = RevenueRecoveryOrchestrator(db)

    # Initialize minimal state for diagnosis
    from app.agents.tools import get_customer_history, calculate_risk_score

    customer_data = get_customer_history(customer.customer_id, db)
    transaction_data = get_transaction_details(transaction_id, db) if transaction_id != "unknown" else {}

    risk_score = calculate_risk_score(customer_data, transaction_data, risk.risk_type)

    # Get AI diagnosis
    from app.agents.prompts import format_diagnosis_prompt
    from langchain_core.messages import HumanMessage
    import json

    prompt = format_diagnosis_prompt(transaction_data, customer_data, risk.risk_type)
    messages = [HumanMessage(content=prompt)]
    response = orchestrator.llm.invoke(messages)

    try:
        diagnosis = json.loads(response.content)
    except json.JSONDecodeError:
        diagnosis = {
            "root_cause_category": "technical",
            "severity": "medium",
            "recovery_probability": risk_score,
            "immediate_action": "contact_customer",
            "reasoning": response.content,
            "key_factors": []
        }

    return {
        "risk_id": request.risk_id,
        "analysis": diagnosis,
        "risk_score": risk_score,
        "customer_profile": {
            "tier": customer_data.get("tier"),
            "success_rate": customer_data.get("success_rate"),
            "lifetime_value": customer_data.get("lifetime_value")
        }
    }


@router.post("/recommend")
async def recommend_intervention(
    request: RecommendInterventionRequest,
    db: Session = Depends(get_db)
):
    """Get AI recommendation for intervention strategy."""
    risk = db.query(RevenueRisk).filter(RevenueRisk.id == request.risk_id).first()

    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    customer = db.query(Customer).filter(Customer.id == risk.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Get transaction if exists
    transaction_id = "unknown"
    if risk.transaction_id:
        transaction = db.query(Transaction).filter(Transaction.id == risk.transaction_id).first()
        if transaction:
            transaction_id = transaction.transaction_id

    # Run full AI workflow
    orchestrator = RevenueRecoveryOrchestrator(db)
    result = orchestrator.run(
        risk_id=str(risk.id),
        risk_type=risk.risk_type,
        transaction_id=transaction_id,
        customer_id=customer.customer_id
    )

    return {
        "risk_id": request.risk_id,
        "diagnosis": result.get("diagnosis", {}),
        "recommended_intervention": result.get("recommended_intervention", {}),
        "compliance_approved": result.get("approved", False),
        "compliance_check": result.get("compliance_check", {}),
        "reasoning": result.get("recommended_intervention", {}).get("reasoning", "")
    }


@router.post("/generate-message")
async def generate_message(
    request: GenerateMessageRequest,
    db: Session = Depends(get_db)
):
    """Generate personalized message content using AI."""
    customer = db.query(Customer).filter(Customer.customer_id == request.customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Generate message using AI
    from app.agents.prompts import format_message_prompt
    from app.agents.orchestrator import RevenueRecoveryOrchestrator
    from langchain_core.messages import HumanMessage
    import json

    orchestrator = RevenueRecoveryOrchestrator(db)

    # Create situation summary
    situation = f"Payment of ${request.transaction_amount} "
    if request.risk_type == "payment_failure":
        situation += f"failed. Reason: {request.failure_reason}."
    elif request.risk_type == "checkout_abandon":
        situation += "was abandoned during checkout."
    elif request.risk_type == "subscription_failure":
        situation += "subscription renewal failed."

    # Determine relationship length
    relationship = "long-term" if customer.total_transactions > 10 else "new"

    prompt = format_message_prompt(
        customer_name=customer.name or "Valued Customer",
        customer_tier=customer.tier or "standard",
        relationship_length=relationship,
        situation_summary=situation,
        intervention_type=request.intervention_type,
        channel="email",
        use_hinglish=False
    )

    messages = [HumanMessage(content=prompt)]
    response = orchestrator.llm.invoke(messages)

    try:
        message_content = json.loads(response.content)
    except json.JSONDecodeError:
        message_content = {
            "subject": "Action Required: Update Your Payment Information",
            "body": response.content,
            "cta": "Update Now",
            "tone": "friendly",
            "language": "english"
        }

    return {
        "intervention_type": request.intervention_type,
        "customer_id": request.customer_id,
        "generated_content": message_content
    }


@router.get("/explain/{entity_id}")
async def explain_decision(
    entity_id: str,
    entity_type: str = "intervention",
    db: Session = Depends(get_db)
):
    """Explain AI decision for a specific entity with full transparency."""

    if entity_type == "intervention":
        intervention = db.query(Intervention).filter(Intervention.id == entity_id).first()

        if not intervention:
            raise HTTPException(status_code=404, detail="Intervention not found")

        risk = db.query(RevenueRisk).filter(RevenueRisk.id == intervention.revenue_risk_id).first()

        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "decision": {
                "intervention_type": intervention.intervention_type,
                "strategy": intervention.intervention_strategy,
                "channel": intervention.channel
            },
            "ai_reasoning": intervention.ai_reasoning,
            "context": {
                "risk_type": risk.risk_type if risk else "unknown",
                "risk_amount": float(risk.risk_amount) if risk else 0,
                "ai_diagnosis": risk.ai_diagnosis if risk else {}
            },
            "metadata": intervention.metadata
        }

    elif entity_type == "risk":
        risk = db.query(RevenueRisk).filter(RevenueRisk.id == entity_id).first()

        if not risk:
            raise HTTPException(status_code=404, detail="Risk not found")

        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "decision": {
                "risk_type": risk.risk_type,
                "priority": risk.priority,
                "status": risk.status
            },
            "ai_diagnosis": risk.ai_diagnosis,
            "risk_score": float(risk.risk_score) if risk.risk_score else None,
            "root_cause": risk.root_cause
        }

    else:
        raise HTTPException(status_code=400, detail="Invalid entity type. Use 'intervention' or 'risk'")


@router.get("/audit-trail/{entity_id}")
async def get_audit_trail(
    entity_id: str,
    entity_type: str = "risk",
    db: Session = Depends(get_db)
):
    """Get complete audit trail for an entity showing all AI decisions."""

    audit_logs = db.query(AuditTrail).filter(
        AuditTrail.entity_id == entity_id,
        AuditTrail.entity_type == entity_type
    ).order_by(AuditTrail.timestamp.desc()).all()

    if not audit_logs:
        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "audit_trail": [],
            "message": "No audit trail found"
        }

    trail = []
    for log in audit_logs:
        trail.append({
            "id": str(log.id),
            "action": log.action,
            "actor": log.actor,
            "timestamp": log.timestamp.isoformat(),
            "details": log.details,
            "compliance_check": log.compliance_check
        })

    return {
        "entity_id": entity_id,
        "entity_type": entity_type,
        "audit_trail": trail,
        "total_entries": len(trail)
    }


@router.get("/health")
async def ai_health_check(db: Session = Depends(get_db)):
    """Check if AI system is properly configured and working."""
    from app.config import settings

    checks = {
        "openai_api_key_configured": bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_api_key_here"),
        "llm_model": settings.LLM_MODEL,
        "database_connected": True,  # If we got here, DB is connected
        "ml_predictions_enabled": settings.ENABLE_ML_PREDICTIONS,
        "auto_recovery_enabled": settings.ENABLE_AUTO_RECOVERY
    }

    all_healthy = all([
        checks["openai_api_key_configured"],
        checks["database_connected"]
    ])

    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks,
        "warnings": [] if all_healthy else [
            "OpenAI API key not configured" if not checks["openai_api_key_configured"] else None
        ]
    }
