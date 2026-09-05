"""Audit trail endpoints for compliance and transparency."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.audit import AuditTrail

router = APIRouter()


@router.get("/logs")
async def get_audit_logs(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    actor: Optional[str] = Query(None, description="Filter by actor"),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get audit trail logs with optional filters."""
    query = db.query(AuditTrail)

    # Apply filters
    if entity_type:
        query = query.filter(AuditTrail.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditTrail.entity_id == entity_id)
    if action:
        query = query.filter(AuditTrail.action.contains(action))
    if actor:
        query = query.filter(AuditTrail.actor == actor)

    # Get total count
    total = query.count()

    # Get paginated results ordered by most recent
    logs = query.order_by(AuditTrail.timestamp.desc()).offset(offset).limit(limit).all()

    # Format response
    results = []
    for log in logs:
        results.append({
            "id": str(log.id),
            "entity_type": log.entity_type,
            "entity_id": str(log.entity_id),
            "action": log.action,
            "actor": log.actor,
            "details": log.details,
            "compliance_check": log.compliance_check,
            "timestamp": log.timestamp.isoformat()
        })

    return {
        "logs": results,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total
    }


@router.get("/stats")
async def get_audit_stats(db: Session = Depends(get_db)):
    """Get audit trail statistics."""
    from sqlalchemy import func

    total_entries = db.query(AuditTrail).count()

    # Count by entity type
    by_entity = {}
    entity_counts = db.query(
        AuditTrail.entity_type,
        func.count(AuditTrail.id).label('count')
    ).group_by(AuditTrail.entity_type).all()

    for entity_type, count in entity_counts:
        by_entity[entity_type] = count

    # Count by action type
    by_action = {}
    action_counts = db.query(
        AuditTrail.action,
        func.count(AuditTrail.id).label('count')
    ).group_by(AuditTrail.action).all()

    for action, count in action_counts:
        by_action[action] = count

    # Count by actor
    by_actor = {}
    actor_counts = db.query(
        AuditTrail.actor,
        func.count(AuditTrail.id).label('count')
    ).group_by(AuditTrail.actor).all()

    for actor, count in actor_counts:
        by_actor[actor] = count

    return {
        "total_entries": total_entries,
        "by_entity_type": by_entity,
        "by_action": by_action,
        "by_actor": by_actor
    }
