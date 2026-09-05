"""Analytics and reporting endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models.risk import RevenueRisk
from app.models.intervention import Intervention, RecoveryOutcome
from app.models.customer import Customer

router = APIRouter()


@router.get("/overview")
async def analytics_overview(db: Session = Depends(get_db)):
    """Get dashboard overview metrics."""

    # Total revenue at risk (active risks)
    total_at_risk = db.query(func.sum(RevenueRisk.risk_amount)).filter(
        RevenueRisk.status == 'active'
    ).scalar() or 0

    # Total revenue recovered
    total_recovered = db.query(func.sum(RecoveryOutcome.recovered_amount)).scalar() or 0

    # Recovery rate calculation
    total_resolved = db.query(RevenueRisk).filter(
        RevenueRisk.status.in_(['recovered', 'lost'])
    ).count()

    recovered_count = db.query(RevenueRisk).filter(
        RevenueRisk.status == 'recovered'
    ).count()

    recovery_rate = (recovered_count / total_resolved * 100) if total_resolved > 0 else 0

    # Active counts
    active_risks = db.query(RevenueRisk).filter(RevenueRisk.status == 'active').count()
    active_interventions = db.query(Intervention).filter(
        Intervention.status == 'pending'
    ).count()

    # Average recovery time
    avg_recovery_time = db.query(
        func.avg(RecoveryOutcome.time_to_recovery)
    ).scalar() or 0

    # Recent activity (last 24 hours)
    last_24h = datetime.utcnow() - timedelta(hours=24)
    new_risks_24h = db.query(RevenueRisk).filter(
        RevenueRisk.detected_at >= last_24h
    ).count()

    recovered_24h = db.query(RecoveryOutcome).filter(
        RecoveryOutcome.recovered_at >= last_24h
    ).count()

    return {
        "total_revenue_at_risk": float(total_at_risk),
        "total_revenue_recovered": float(total_recovered),
        "recovery_rate": round(recovery_rate, 2),
        "active_risks": active_risks,
        "active_interventions": active_interventions,
        "avg_recovery_time_hours": round(float(avg_recovery_time), 2),
        "last_24h": {
            "new_risks": new_risks_24h,
            "recovered": recovered_24h
        }
    }


@router.get("/recovery-rate")
async def recovery_rate_trend(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Get recovery rate trends over time."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Get daily recovery data
    daily_data = db.query(
        func.date(RecoveryOutcome.recovered_at).label('date'),
        func.count(RecoveryOutcome.id).label('recoveries'),
        func.sum(RecoveryOutcome.recovered_amount).label('amount')
    ).filter(
        RecoveryOutcome.recovered_at >= cutoff_date
    ).group_by(func.date(RecoveryOutcome.recovered_at)).all()

    timeline = []
    for date, count, amount in daily_data:
        timeline.append({
            "date": date.isoformat() if date else datetime.utcnow().date().isoformat(),
            "recoveries": count,
            "amount": float(amount) if amount else 0
        })

    # Calculate overall stats for the period
    total_recoveries = sum(d['recoveries'] for d in timeline)
    total_amount = sum(d['amount'] for d in timeline)

    # Get risks detected in the same period
    total_risks = db.query(RevenueRisk).filter(
        RevenueRisk.detected_at >= cutoff_date
    ).count()

    recovery_rate = (total_recoveries / total_risks * 100) if total_risks > 0 else 0

    return {
        "period": f"last_{days}_days",
        "timeline": timeline,
        "summary": {
            "total_recoveries": total_recoveries,
            "total_amount": total_amount,
            "total_risks": total_risks,
            "recovery_rate": round(recovery_rate, 2)
        }
    }


@router.get("/intervention-effectiveness")
async def intervention_effectiveness(db: Session = Depends(get_db)):
    """Get intervention effectiveness by type and channel."""

    # By type
    by_type = {}
    type_stats = db.query(
        Intervention.intervention_type,
        func.count(Intervention.id).label('total'),
        func.sum(func.case((Intervention.outcome == 'success', 1), else_=0)).label('successful'),
        func.avg(Intervention.cost).label('avg_cost')
    ).filter(
        Intervention.status == 'executed'
    ).group_by(Intervention.intervention_type).all()

    for int_type, total, successful, avg_cost in type_stats:
        success_rate = (successful / total * 100) if total > 0 else 0
        by_type[int_type] = {
            "total": total,
            "successful": successful,
            "success_rate": round(success_rate, 2),
            "avg_cost": round(float(avg_cost), 2) if avg_cost else 0
        }

    # By channel
    by_channel = {}
    channel_stats = db.query(
        Intervention.channel,
        func.count(Intervention.id).label('total'),
        func.sum(func.case((Intervention.outcome == 'success', 1), else_=0)).label('successful')
    ).filter(
        Intervention.status == 'executed'
    ).group_by(Intervention.channel).all()

    for channel, total, successful in channel_stats:
        success_rate = (successful / total * 100) if total > 0 else 0
        by_channel[channel or "unknown"] = {
            "total": total,
            "successful": successful,
            "success_rate": round(success_rate, 2)
        }

    # By risk type
    by_risk_type = {}
    risk_type_stats = db.query(
        RevenueRisk.risk_type,
        func.count(Intervention.id).label('interventions'),
        func.sum(func.case((Intervention.outcome == 'success', 1), else_=0)).label('successful')
    ).join(Intervention, Intervention.revenue_risk_id == RevenueRisk.id).filter(
        Intervention.status == 'executed'
    ).group_by(RevenueRisk.risk_type).all()

    for risk_type, interventions, successful in risk_type_stats:
        success_rate = (successful / interventions * 100) if interventions > 0 else 0
        by_risk_type[risk_type] = {
            "interventions": interventions,
            "successful": successful,
            "success_rate": round(success_rate, 2)
        }

    return {
        "by_type": by_type,
        "by_channel": by_channel,
        "by_risk_type": by_risk_type
    }


@router.get("/revenue-saved")
async def revenue_saved_timeline(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Get revenue saved over time."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Daily revenue recovered
    daily_data = db.query(
        func.date(RecoveryOutcome.recovered_at).label('date'),
        func.sum(RecoveryOutcome.recovered_amount).label('amount'),
        func.count(RecoveryOutcome.id).label('count')
    ).filter(
        RecoveryOutcome.recovered_at >= cutoff_date
    ).group_by(func.date(RecoveryOutcome.recovered_at)).all()

    timeline = []
    cumulative = 0
    for date, amount, count in daily_data:
        cumulative += float(amount) if amount else 0
        timeline.append({
            "date": date.isoformat() if date else datetime.utcnow().date().isoformat(),
            "daily_amount": float(amount) if amount else 0,
            "cumulative_amount": cumulative,
            "recoveries": count
        })

    # Total saved in period
    total_saved = sum(d['daily_amount'] for d in timeline)

    # Calculate ROI (assuming avg cost per intervention)
    total_interventions = db.query(Intervention).filter(
        and_(
            Intervention.executed_at >= cutoff_date,
            Intervention.status == 'executed'
        )
    ).count()

    avg_cost_per_intervention = 2.50  # Placeholder - can be calculated from actual costs
    total_cost = total_interventions * avg_cost_per_intervention
    roi = ((total_saved - total_cost) / total_cost * 100) if total_cost > 0 else 0

    return {
        "period": f"last_{days}_days",
        "timeline": timeline,
        "total_saved": total_saved,
        "total_cost": total_cost,
        "roi_percentage": round(roi, 2),
        "net_revenue": total_saved - total_cost
    }


@router.get("/customer-segments")
async def customer_segment_analysis(db: Session = Depends(get_db)):
    """Analyze recovery performance by customer segment."""

    # By customer tier
    by_tier = {}
    tier_stats = db.query(
        Customer.tier,
        func.count(RevenueRisk.id).label('risks'),
        func.sum(func.case((RevenueRisk.status == 'recovered', 1), else_=0)).label('recovered'),
        func.sum(RevenueRisk.risk_amount).label('total_at_risk')
    ).join(RevenueRisk, RevenueRisk.customer_id == Customer.id).group_by(Customer.tier).all()

    for tier, risks, recovered, total_at_risk in tier_stats:
        recovery_rate = (recovered / risks * 100) if risks > 0 else 0
        by_tier[tier or "unknown"] = {
            "total_risks": risks,
            "recovered": recovered,
            "recovery_rate": round(recovery_rate, 2),
            "total_at_risk": float(total_at_risk) if total_at_risk else 0
        }

    # By customer type (B2B vs B2C)
    by_type = {}
    type_stats = db.query(
        Customer.customer_type,
        func.count(RevenueRisk.id).label('risks'),
        func.sum(func.case((RevenueRisk.status == 'recovered', 1), else_=0)).label('recovered')
    ).join(RevenueRisk, RevenueRisk.customer_id == Customer.id).group_by(Customer.customer_type).all()

    for cust_type, risks, recovered in type_stats:
        recovery_rate = (recovered / risks * 100) if risks > 0 else 0
        by_type[cust_type or "unknown"] = {
            "total_risks": risks,
            "recovered": recovered,
            "recovery_rate": round(recovery_rate, 2)
        }

    return {
        "by_tier": by_tier,
        "by_customer_type": by_type
    }


@router.get("/time-to-recovery")
async def time_to_recovery_analysis(db: Session = Depends(get_db)):
    """Analyze time to recovery metrics."""

    # Average by risk type
    by_risk_type = {}
    risk_type_times = db.query(
        RevenueRisk.risk_type,
        func.avg(RecoveryOutcome.time_to_recovery).label('avg_time'),
        func.min(RecoveryOutcome.time_to_recovery).label('min_time'),
        func.max(RecoveryOutcome.time_to_recovery).label('max_time'),
        func.count(RecoveryOutcome.id).label('count')
    ).join(RecoveryOutcome, RecoveryOutcome.revenue_risk_id == RevenueRisk.id).group_by(
        RevenueRisk.risk_type
    ).all()

    for risk_type, avg_time, min_time, max_time, count in risk_type_times:
        by_risk_type[risk_type] = {
            "avg_hours": round(float(avg_time), 2) if avg_time else 0,
            "min_hours": round(float(min_time), 2) if min_time else 0,
            "max_hours": round(float(max_time), 2) if max_time else 0,
            "sample_size": count
        }

    # Overall statistics
    overall_avg = db.query(func.avg(RecoveryOutcome.time_to_recovery)).scalar() or 0

    return {
        "overall_avg_hours": round(float(overall_avg), 2),
        "by_risk_type": by_risk_type
    }
