"""Intervention management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.intervention import Intervention, RecoveryOutcome
from app.models.risk import RevenueRisk
from app.services.intervention_service import InterventionService

router = APIRouter()


# Pydantic schemas
class RecoveryRequest(BaseModel):
    recovered_amount: float
    recovery_method: str
    customer_feedback: Optional[str] = None


@router.get("/")
async def list_interventions(
    status: Optional[str] = Query(None, description="Filter by status: pending, executed, failed, skipped"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List all interventions with optional filters."""
    query = db.query(Intervention).join(RevenueRisk)

    if status:
        query = query.filter(Intervention.status == status)

    total = query.count()
    interventions = query.order_by(Intervention.scheduled_at.desc()).offset(offset).limit(limit).all()

    results = []
    for intervention in interventions:
        risk = db.query(RevenueRisk).filter(RevenueRisk.id == intervention.revenue_risk_id).first()
        results.append({
            "id": str(intervention.id),
            "risk_id": str(intervention.revenue_risk_id),
            "risk_type": risk.risk_type if risk else "unknown",
            "intervention_type": intervention.intervention_type,
            "strategy": intervention.intervention_strategy,
            "channel": intervention.channel,
            "status": intervention.status,
            "outcome": intervention.outcome,
            "scheduled_at": intervention.scheduled_at.isoformat() if intervention.scheduled_at else None,
            "executed_at": intervention.executed_at.isoformat() if intervention.executed_at else None,
            "cost": float(intervention.cost) if intervention.cost else 0
        })

    return {
        "interventions": results,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total
    }


@router.get("/{intervention_id}")
async def get_intervention(intervention_id: str, db: Session = Depends(get_db)):
    """Get specific intervention details including AI reasoning."""
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()

    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    risk = db.query(RevenueRisk).filter(RevenueRisk.id == intervention.revenue_risk_id).first()

    return {
        "id": str(intervention.id),
        "risk_id": str(intervention.revenue_risk_id),
        "risk_type": risk.risk_type if risk else "unknown",
        "risk_amount": float(risk.risk_amount) if risk else 0,
        "intervention_type": intervention.intervention_type,
        "strategy": intervention.intervention_strategy,
        "channel": intervention.channel,
        "content": intervention.content,
        "status": intervention.status,
        "outcome": intervention.outcome,
        "scheduled_at": intervention.scheduled_at.isoformat() if intervention.scheduled_at else None,
        "executed_at": intervention.executed_at.isoformat() if intervention.executed_at else None,
        "ai_reasoning": intervention.ai_reasoning,
        "cost": float(intervention.cost) if intervention.cost else 0,
        "metadata": intervention.metadata
    }


@router.post("/{intervention_id}/execute")
async def execute_intervention(intervention_id: str, db: Session = Depends(get_db)):
    """Execute a specific intervention."""
    service = InterventionService(db)
    result = service.execute_intervention(intervention_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return {
        "message": "Intervention executed successfully",
        "result": result
    }


@router.get("/{intervention_id}/preview")
async def preview_intervention(intervention_id: str, db: Session = Depends(get_db)):
    """Preview generated intervention content before execution."""
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()

    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    # Parse content (stored as JSON string)
    import json
    try:
        content = json.loads(intervention.content) if intervention.content else {}
    except:
        content = {"body": intervention.content}

    return {
        "intervention_id": str(intervention.id),
        "type": intervention.intervention_type,
        "channel": intervention.channel,
        "content": content,
        "preview": {
            "subject": content.get("subject", ""),
            "body": content.get("body", ""),
            "cta": content.get("cta", ""),
            "tone": content.get("tone", "friendly"),
            "language": content.get("language", "english")
        },
        "ai_reasoning": intervention.ai_reasoning
    }


@router.get("/queue/pending")
async def get_intervention_queue(
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """Get pending interventions ready to execute."""
    service = InterventionService(db)
    queue = service.get_intervention_queue(limit=limit)

    return {
        "queue": queue,
        "count": len(queue)
    }


@router.post("/{intervention_id}/record-recovery")
async def record_recovery(
    intervention_id: str,
    recovery: RecoveryRequest,
    db: Session = Depends(get_db)
):
    """Record a successful recovery outcome."""
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()

    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    service = InterventionService(db)

    try:
        outcome = service.record_recovery(
            risk_id=str(intervention.revenue_risk_id),
            intervention_id=intervention_id,
            recovered_amount=recovery.recovered_amount,
            recovery_method=recovery.recovery_method
        )

        return {
            "message": "Recovery recorded successfully",
            "outcome": {
                "id": str(outcome.id),
                "recovered_amount": float(outcome.recovered_amount),
                "recovered_at": outcome.recovered_at.isoformat(),
                "time_to_recovery_hours": float(outcome.time_to_recovery)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats/effectiveness")
async def intervention_effectiveness(db: Session = Depends(get_db)):
    """Get intervention effectiveness statistics."""
    from sqlalchemy import func

    # Success rate by intervention type
    by_type = {}
    type_stats = db.query(
        Intervention.intervention_type,
        func.count(Intervention.id).label('total'),
        func.sum(func.case((Intervention.outcome == 'success', 1), else_=0)).label('successful')
    ).filter(Intervention.status == 'executed').group_by(Intervention.intervention_type).all()

    for int_type, total, successful in type_stats:
        success_rate = (successful / total * 100) if total > 0 else 0
        by_type[int_type] = {
            "total": total,
            "successful": successful,
            "success_rate": round(success_rate, 2)
        }

    # By channel
    by_channel = {}
    channel_stats = db.query(
        Intervention.channel,
        func.count(Intervention.id).label('total'),
        func.sum(func.case((Intervention.outcome == 'success', 1), else_=0)).label('successful')
    ).filter(Intervention.status == 'executed').group_by(Intervention.channel).all()

    for channel, total, successful in channel_stats:
        success_rate = (successful / total * 100) if total > 0 else 0
        by_channel[channel or "unknown"] = {
            "total": total,
            "successful": successful,
            "success_rate": round(success_rate, 2)
        }

    # Overall stats
    total_interventions = db.query(Intervention).filter(Intervention.status == 'executed').count()
    successful_interventions = db.query(Intervention).filter(
        Intervention.outcome == 'success'
    ).count()
    overall_success_rate = (successful_interventions / total_interventions * 100) if total_interventions > 0 else 0

    return {
        "overall": {
            "total_executed": total_interventions,
            "successful": successful_interventions,
            "success_rate": round(overall_success_rate, 2)
        },
        "by_type": by_type,
        "by_channel": by_channel
    }
