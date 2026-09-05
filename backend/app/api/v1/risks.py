"""Risk detection and management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.database import get_db
from app.models.risk import RevenueRisk
from app.models.customer import Customer
from app.services.risk_detection import RiskDetectionService
from app.services.intervention_service import InterventionService

router = APIRouter()


# Pydantic schemas
class RiskResponse(BaseModel):
    id: str
    risk_type: str
    risk_amount: float
    risk_score: Optional[float]
    status: str
    priority: str
    detected_at: str
    customer_id: str
    customer_email: str
    root_cause: Optional[str]
    ai_diagnosis: Optional[dict]

    class Config:
        from_attributes = True


class RiskStatsResponse(BaseModel):
    total_at_risk: float
    total_risks: int
    active_risks: int
    recovered_count: int
    lost_count: int
    recovery_rate: float
    by_type: dict
    by_priority: dict


@router.get("/", response_model=dict)
async def list_risks(
    status: Optional[str] = Query(None, description="Filter by status: active, recovered, lost, expired"),
    risk_type: Optional[str] = Query(None, description="Filter by type: payment_failure, checkout_abandon, etc."),
    priority: Optional[str] = Query(None, description="Filter by priority: low, medium, high, critical"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List all revenue risks with optional filters."""
    query = db.query(RevenueRisk).join(Customer)

    # Apply filters
    if status:
        query = query.filter(RevenueRisk.status == status)
    if risk_type:
        query = query.filter(RevenueRisk.risk_type == risk_type)
    if priority:
        query = query.filter(RevenueRisk.priority == priority)

    # Get total count
    total = query.count()

    # Get paginated results
    risks = query.order_by(RevenueRisk.detected_at.desc()).offset(offset).limit(limit).all()

    # Format response
    results = []
    for risk in risks:
        customer = db.query(Customer).filter(Customer.id == risk.customer_id).first()
        results.append({
            "id": str(risk.id),
            "risk_type": risk.risk_type,
            "risk_amount": float(risk.risk_amount),
            "risk_score": float(risk.risk_score) if risk.risk_score else None,
            "status": risk.status,
            "priority": risk.priority,
            "detected_at": risk.detected_at.isoformat(),
            "customer_id": customer.customer_id if customer else "unknown",
            "customer_email": customer.email if customer else "unknown",
            "root_cause": risk.root_cause,
            "has_ai_diagnosis": risk.ai_diagnosis is not None
        })

    return {
        "risks": results,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total
    }


@router.get("/{risk_id}")
async def get_risk(risk_id: str, db: Session = Depends(get_db)):
    """Get specific risk details with full AI diagnosis."""
    risk = db.query(RevenueRisk).filter(RevenueRisk.id == risk_id).first()

    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    customer = db.query(Customer).filter(Customer.id == risk.customer_id).first()

    # Get interventions for this risk
    from app.models.intervention import Intervention
    interventions = db.query(Intervention).filter(
        Intervention.revenue_risk_id == risk.id
    ).order_by(Intervention.scheduled_at.desc()).all()

    return {
        "id": str(risk.id),
        "risk_type": risk.risk_type,
        "risk_amount": float(risk.risk_amount),
        "risk_score": float(risk.risk_score) if risk.risk_score else None,
        "status": risk.status,
        "priority": risk.priority,
        "detected_at": risk.detected_at.isoformat(),
        "root_cause": risk.root_cause,
        "ai_diagnosis": risk.ai_diagnosis,
        "customer": {
            "id": customer.customer_id if customer else "unknown",
            "email": customer.email if customer else "unknown",
            "name": customer.name if customer else "unknown",
            "tier": customer.tier if customer else "unknown"
        },
        "interventions": [
            {
                "id": str(i.id),
                "type": i.intervention_type,
                "status": i.status,
                "scheduled_at": i.scheduled_at.isoformat() if i.scheduled_at else None,
                "executed_at": i.executed_at.isoformat() if i.executed_at else None
            }
            for i in interventions
        ]
    }


@router.post("/detect")
async def detect_risks(db: Session = Depends(get_db)):
    """Trigger risk detection process across all scenarios."""
    service = RiskDetectionService(db)
    results = service.run_detection()

    return {
        "message": "Risk detection completed",
        "results": results
    }


@router.post("/{risk_id}/analyze")
async def analyze_risk_with_ai(risk_id: str, db: Session = Depends(get_db)):
    """Analyze a specific risk with AI and get diagnosis."""
    service = RiskDetectionService(db)
    result = service.process_risk_with_ai(risk_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return {
        "risk_id": risk_id,
        "ai_analysis": result
    }


@router.post("/{risk_id}/process")
async def process_risk_full_workflow(risk_id: str, db: Session = Depends(get_db)):
    """Process a risk through the complete AI workflow and create intervention."""
    intervention_service = InterventionService(db)
    result = intervention_service.process_risk_and_create_intervention(risk_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/stats/overview")
async def risk_stats(db: Session = Depends(get_db)):
    """Get comprehensive risk statistics."""
    from sqlalchemy import func

    # Total at risk amount
    total_at_risk = db.query(func.sum(RevenueRisk.risk_amount)).filter(
        RevenueRisk.status == 'active'
    ).scalar() or 0

    # Count by status
    total_risks = db.query(RevenueRisk).count()
    active_risks = db.query(RevenueRisk).filter(RevenueRisk.status == 'active').count()
    recovered = db.query(RevenueRisk).filter(RevenueRisk.status == 'recovered').count()
    lost = db.query(RevenueRisk).filter(RevenueRisk.status == 'lost').count()

    # Recovery rate
    recovery_rate = (recovered / max(recovered + lost, 1)) * 100 if (recovered + lost) > 0 else 0

    # By type
    by_type = {}
    type_counts = db.query(
        RevenueRisk.risk_type,
        func.count(RevenueRisk.id).label('count'),
        func.sum(RevenueRisk.risk_amount).label('amount')
    ).filter(RevenueRisk.status == 'active').group_by(RevenueRisk.risk_type).all()

    for risk_type, count, amount in type_counts:
        by_type[risk_type] = {
            "count": count,
            "amount": float(amount) if amount else 0
        }

    # By priority
    by_priority = {}
    priority_counts = db.query(
        RevenueRisk.priority,
        func.count(RevenueRisk.id).label('count')
    ).filter(RevenueRisk.status == 'active').group_by(RevenueRisk.priority).all()

    for priority, count in priority_counts:
        by_priority[priority] = count

    return {
        "total_at_risk": float(total_at_risk),
        "total_risks": total_risks,
        "active_risks": active_risks,
        "recovered_count": recovered,
        "lost_count": lost,
        "recovery_rate": round(recovery_rate, 2),
        "by_type": by_type,
        "by_priority": by_priority
    }
