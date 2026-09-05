"""
Run AI recovery workflows on test data to generate demo results.

This script:
1. Processes risks with AI agents
2. Creates interventions
3. Simulates recoveries
4. Generates impressive metrics for demo

Run after generate_test_data.py
"""
import random
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.risk import RevenueRisk
from app.models.customer import Customer
from app.models.intervention import Intervention, RecoveryOutcome
from app.services.risk_detection import RiskDetectionService
from app.services.intervention_service import InterventionService


def process_risks_with_ai(db: Session, limit: int = 20):
    """Process risks through AI workflow."""
    print(f"\nProcessing up to {limit} risks with AI...")

    risks = db.query(RevenueRisk).filter(
        RevenueRisk.status == 'active'
    ).limit(limit).all()

    processed = 0
    interventions_created = 0

    intervention_service = InterventionService(db)

    for i, risk in enumerate(risks):
        try:
            print(f"  [{i+1}/{len(risks)}] Processing risk {str(risk.id)[:8]}... ", end="")

            # Process with AI
            result = intervention_service.process_risk_and_create_intervention(str(risk.id))

            if result.get('intervention_created'):
                interventions_created += 1
                print("✓ Intervention created")
            else:
                print("⚠ Compliance blocked")

            processed += 1

        except Exception as e:
            print(f"✗ Error: {e}")
            continue

    print(f"\n✓ Processed {processed} risks, created {interventions_created} interventions")
    return processed, interventions_created


def simulate_intervention_execution(db: Session):
    """Execute pending interventions."""
    print("\nExecuting interventions...")

    pending = db.query(Intervention).filter(
        Intervention.status == 'pending'
    ).all()

    executed = 0
    intervention_service = InterventionService(db)

    for i, intervention in enumerate(pending):
        try:
            result = intervention_service.execute_intervention(str(intervention.id))

            if result.get('status') == 'executed':
                executed += 1
                if (i + 1) % 5 == 0:
                    print(f"  Executed {i + 1} interventions...")

        except Exception as e:
            print(f"  Error executing {str(intervention.id)[:8]}: {e}")
            continue

    print(f"✓ Executed {executed} interventions")
    return executed


def simulate_recoveries(db: Session, success_rate: float = 0.75):
    """Simulate recovery outcomes for executed interventions."""
    print(f"\nSimulating recoveries (target success rate: {success_rate*100}%)...")

    # Get executed interventions without outcomes
    executed = db.query(Intervention).filter(
        Intervention.status == 'executed',
        Intervention.outcome.is_(None)
    ).all()

    intervention_service = InterventionService(db)
    recoveries = 0
    total_recovered = Decimal('0')

    for i, intervention in enumerate(executed):
        # Simulate success based on intervention type and risk
        risk = db.query(RevenueRisk).filter(RevenueRisk.id == intervention.revenue_risk_id).first()

        if not risk:
            continue

        # Base success rate
        base_success = success_rate

        # Adjust by intervention type
        if intervention.intervention_type == 'email_with_update_link':
            type_success = 0.85
        elif intervention.intervention_type == 'immediate_payment_retry':
            type_success = 0.80
        elif intervention.intervention_type == 'sms_reminder':
            type_success = 0.70
        else:
            type_success = 0.75

        # Adjust by risk type
        if risk.risk_type == 'payment_failure':
            if 'expired' in risk.root_cause.lower():
                risk_success = 0.90  # Easy to fix
            else:
                risk_success = 0.70
        elif risk.risk_type == 'subscription_failure':
            risk_success = 0.85
        elif risk.risk_type == 'checkout_abandon':
            risk_success = 0.40  # Harder to recover
        else:
            risk_success = 0.60

        # Combined success probability
        success_prob = (type_success + risk_success) / 2

        # Determine outcome
        if random.random() < success_prob:
            # Success - create recovery
            recovered_amount = float(risk.risk_amount)

            # Some partial recoveries
            if random.random() < 0.15:
                recovered_amount *= random.uniform(0.5, 0.9)

            try:
                outcome = intervention_service.record_recovery(
                    risk_id=str(risk.id),
                    intervention_id=str(intervention.id),
                    recovered_amount=recovered_amount,
                    recovery_method=intervention.intervention_type
                )

                recoveries += 1
                total_recovered += Decimal(str(recovered_amount))

            except Exception as e:
                print(f"  Error recording recovery: {e}")
                continue

        else:
            # Failure - update intervention outcome
            intervention.outcome = 'no_response'
            db.commit()

        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1} interventions...")

    # Mark some risks as lost (those that didn't recover)
    unrecovered = db.query(RevenueRisk).filter(
        RevenueRisk.status == 'active'
    ).all()

    lost_count = 0
    for risk in unrecovered:
        # Check if has failed interventions
        has_intervention = db.query(Intervention).filter(
            Intervention.revenue_risk_id == risk.id
        ).first()

        if has_intervention and random.random() < 0.2:  # 20% become lost
            risk.status = 'lost'
            lost_count += 1

    db.commit()

    print(f"✓ Created {recoveries} successful recoveries")
    print(f"  Total recovered: ₹{float(total_recovered):,.2f}")
    print(f"  Marked {lost_count} risks as lost")

    return recoveries, total_recovered


def generate_summary_stats(db: Session):
    """Generate and display summary statistics."""
    print("\n" + "="*60)
    print("DEMO RESULTS - AI Revenue Recovery")
    print("="*60 + "\n")

    # Total risks
    total_risks = db.query(RevenueRisk).count()
    active_risks = db.query(RevenueRisk).filter(RevenueRisk.status == 'active').count()
    recovered_risks = db.query(RevenueRisk).filter(RevenueRisk.status == 'recovered').count()
    lost_risks = db.query(RevenueRisk).filter(RevenueRisk.status == 'lost').count()

    print(f"📊 RISK OVERVIEW")
    print(f"  Total Risks Detected: {total_risks}")
    print(f"  Active (In Progress): {active_risks}")
    print(f"  Recovered: {recovered_risks}")
    print(f"  Lost: {lost_risks}")

    # Calculate amounts
    from sqlalchemy import func

    total_at_risk = db.query(func.sum(RevenueRisk.risk_amount)).scalar() or 0
    active_amount = db.query(func.sum(RevenueRisk.risk_amount)).filter(
        RevenueRisk.status == 'active'
    ).scalar() or 0

    total_recovered = db.query(func.sum(RecoveryOutcome.recovered_amount)).scalar() or 0

    print(f"\n💰 REVENUE IMPACT")
    print(f"  Total Revenue at Risk: ₹{float(total_at_risk):,.2f}")
    print(f"  Currently Active: ₹{float(active_amount):,.2f}")
    print(f"  Successfully Recovered: ₹{float(total_recovered):,.2f}")

    # Calculate recovery rate
    resolved = recovered_risks + lost_risks
    recovery_rate = (recovered_risks / resolved * 100) if resolved > 0 else 0

    print(f"\n📈 PERFORMANCE METRICS")
    print(f"  Recovery Rate: {recovery_rate:.1f}%")

    # Intervention stats
    total_interventions = db.query(Intervention).count()
    executed = db.query(Intervention).filter(Intervention.status == 'executed').count()
    successful = db.query(Intervention).filter(Intervention.outcome == 'success').count()

    intervention_success = (successful / executed * 100) if executed > 0 else 0

    print(f"  Interventions Created: {total_interventions}")
    print(f"  Interventions Executed: {executed}")
    print(f"  Intervention Success Rate: {intervention_success:.1f}%")

    # Average recovery time
    avg_time = db.query(func.avg(RecoveryOutcome.time_to_recovery)).scalar() or 0

    print(f"  Avg Time to Recovery: {float(avg_time):.1f} hours ({float(avg_time)/24:.1f} days)")

    # ROI calculation
    avg_cost_per_intervention = 2.50
    total_cost = executed * avg_cost_per_intervention
    net_revenue = float(total_recovered) - total_cost
    roi = (net_revenue / total_cost * 100) if total_cost > 0 else 0

    print(f"\n💵 ROI ANALYSIS")
    print(f"  Total Cost (interventions): ₹{total_cost:,.2f}")
    print(f"  Net Revenue Recovered: ₹{net_revenue:,.2f}")
    print(f"  ROI: {roi:.0f}%")

    # By risk type
    print(f"\n📋 RECOVERY BY RISK TYPE")

    risk_types = db.query(RevenueRisk.risk_type, func.count(RevenueRisk.id)).group_by(
        RevenueRisk.risk_type
    ).all()

    for risk_type, count in risk_types:
        recovered_count = db.query(RevenueRisk).filter(
            RevenueRisk.risk_type == risk_type,
            RevenueRisk.status == 'recovered'
        ).count()

        lost_count = db.query(RevenueRisk).filter(
            RevenueRisk.risk_type == risk_type,
            RevenueRisk.status == 'lost'
        ).count()

        resolved_total = recovered_count + lost_count
        type_recovery_rate = (recovered_count / resolved_total * 100) if resolved_total > 0 else 0

        print(f"  {risk_type.replace('_', ' ').title()}: {type_recovery_rate:.0f}% ({recovered_count}/{resolved_total})")

    print("\n" + "="*60)
    print("Demo data ready for presentation!")
    print("="*60 + "\n")


def main():
    """Main function to run AI workflows and generate results."""
    print("\n" + "="*60)
    print("AI Revenue Recovery - Workflow Simulation")
    print("="*60)

    db = SessionLocal()

    try:
        # Step 1: Process risks with AI
        processed, interventions = process_risks_with_ai(db, limit=30)

        # Step 2: Execute interventions
        executed = simulate_intervention_execution(db)

        # Step 3: Simulate recoveries
        recoveries, amount = simulate_recoveries(db, success_rate=0.75)

        # Step 4: Generate summary
        generate_summary_stats(db)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
