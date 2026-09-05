"""
Generate comprehensive demo data with interventions and audit trails
Creates 50 risks: 20 pending, 30 recovered with full AI analysis
"""
import psycopg2
from datetime import datetime, timedelta
import random
import uuid
import json

# REPLACE THIS with your actual Supabase connection string
DATABASE_URL = "postgresql://postgres.fxhpydjdnwynpywnzpmi:Appleballcatdo@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

print("=" * 60)
print("  Generating Complete Demo Data")
print("=" * 60)
print()

# Sample data
CUSTOMER_NAMES = [
    "Rajesh Kumar", "Priya Sharma", "Amit Patel", "Sneha Reddy", "Vikram Singh",
    "Anita Desai", "Rohit Mehta", "Kavya Nair", "Sanjay Verma", "Neha Agarwal",
    "Arjun Malhotra", "Divya Iyer", "Karan Kapoor", "Pooja Gupta", "Ravi Joshi"
]

RISK_TYPES = ['payment_failure', 'checkout_abandonment', 'subscription_failure', 'b2b_receivable']
PRIORITIES = ['low', 'medium', 'high']
TIERS = ['standard', 'premium', 'enterprise']

INTERVENTION_TYPES = ['email', 'sms', 'payment_retry', 'voice_call', 'payment_plan', 'personalized_offer']
CHANNELS = ['email', 'sms', 'whatsapp', 'voice', 'in_app']

FAILURE_REASONS = [
    "Card expired - customer needs to update payment method",
    "Insufficient funds - retry after 3 days recommended",
    "Network timeout during checkout - technical issue",
    "Card declined by bank - suggest alternative payment",
    "Customer abandoned cart at shipping details",
    "Subscription renewal failed - payment method invalid"
]

AI_DIAGNOSES = [
    {
        "diagnosis": "Payment method expired. Customer has good payment history.",
        "root_cause": "Card expired 2 days ago",
        "recommended_intervention": "Send personalized email with payment update link",
        "reasoning": "Premium customer with 95% payment success rate. Simple payment method update needed.",
        "confidence": 0.92
    },
    {
        "diagnosis": "Temporary insufficient funds. Customer is reliable payer.",
        "root_cause": "Insufficient balance at transaction time",
        "recommended_intervention": "Retry payment after 3 days with SMS reminder",
        "reasoning": "Historical data shows customer pays within 5 days of reminder.",
        "confidence": 0.87
    },
    {
        "diagnosis": "High cart abandonment due to unexpected shipping cost.",
        "root_cause": "Customer abandoned at final checkout",
        "recommended_intervention": "Offer free shipping for 24 hours via email",
        "reasoning": "Cart value ₹12,000+ qualifies for free shipping offer. High conversion probability.",
        "confidence": 0.94
    }
]

RECOVERY_MESSAGES = [
    "Hi {name}, we noticed your payment didn't go through. Update your card details here: [link]. We've saved your order!",
    "Your subscription is about to expire! Update payment method now to continue: [link]",
    "Complete your ₹{amount} order today and get 10% off! Valid for 24 hours: [link]",
    "Hi {name}, your payment failed. We can split this into 3 monthly payments. Interested? Reply YES."
]

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    print("✅ Connected to database!")
    print()

    # Clear existing test data (optional)
    print("Clearing old test data...")
    cur.execute("DELETE FROM audit_trail")
    cur.execute("DELETE FROM recovery_outcomes")
    cur.execute("DELETE FROM interventions")
    cur.execute("DELETE FROM revenue_risks")
    cur.execute("DELETE FROM transactions")
    cur.execute("DELETE FROM customers")
    conn.commit()
    print("✅ Cleared old data")
    print()

    # Create 50 customers
    print("Creating 50 customers...")
    customers = []
    for i in range(50):
        customer_uuid = str(uuid.uuid4())
        customer_id = f"CUST{2000 + i}"
        name = CUSTOMER_NAMES[i % len(CUSTOMER_NAMES)]
        email = f"{name.lower().replace(' ', '.')}_{i}@example.com"
        tier = random.choice(TIERS)
        ltv = random.randint(20000, 200000)

        cur.execute("""
            INSERT INTO customers (id, customer_id, email, name, tier, lifetime_value,
                                 total_transactions, failed_transactions, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW() - INTERVAL '%s days', NOW())
        """, (customer_uuid, customer_id, email, name, tier, ltv,
              random.randint(5, 50), random.randint(0, 3), random.randint(1, 90)))

        customers.append({
            'uuid': customer_uuid,
            'customer_id': customer_id,
            'name': name,
            'email': email,
            'tier': tier
        })

    conn.commit()
    print(f"✅ Created {len(customers)} customers")
    print()

    # Create 50 revenue risks (30 recovered, 20 pending)
    print("Creating 50 revenue risks...")
    risks_created = 0
    recovered_count = 0
    pending_count = 0

    for i in range(50):
        customer = customers[i % len(customers)]
        risk_uuid = str(uuid.uuid4())
        risk_type = random.choice(RISK_TYPES)
        amount = random.randint(2000, 75000)
        priority = random.choice(PRIORITIES)
        risk_score = random.randint(65, 98)

        # First 30 are recovered, last 20 are pending
        if i < 30:
            status = 'recovered'
            detected_hours_ago = random.randint(48, 240)  # 2-10 days ago
            recovered_count += 1
        else:
            status = 'active'
            detected_hours_ago = random.randint(1, 48)  # Last 2 days
            pending_count += 1

        # Insert risk
        ai_diag = random.choice(AI_DIAGNOSES)
        root_cause = random.choice(FAILURE_REASONS)

        cur.execute("""
            INSERT INTO revenue_risks (id, customer_id, risk_type, risk_amount, risk_score,
                                      status, priority, root_cause, ai_diagnosis, detected_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW() - INTERVAL '%s hours')
        """, (risk_uuid, customer['uuid'], risk_type, amount, risk_score,
              status, priority, root_cause, json.dumps(ai_diag), detected_hours_ago))

        # Create audit trail entry for risk detection
        cur.execute("""
            INSERT INTO audit_trail (id, entity_type, entity_id, action, actor, details,
                                   compliance_check, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW() - INTERVAL '%s hours')
        """, (str(uuid.uuid4()), 'revenue_risk', risk_uuid, 'risk_detected',
              'system', json.dumps({
                  'risk_type': risk_type,
                  'amount': amount,
                  'customer': customer['email'],
                  'detection_method': 'automated_monitoring'
              }), json.dumps({'passed': True, 'checks': ['amount_threshold', 'customer_validation']}),
              detected_hours_ago))

        # For recovered risks, create interventions and outcomes
        if status == 'recovered':
            intervention_uuid = str(uuid.uuid4())
            intervention_type = random.choice(INTERVENTION_TYPES)
            channel = random.choice(CHANNELS)
            strategy = f"immediate_recovery_{intervention_type}"

            message = random.choice(RECOVERY_MESSAGES).format(
                name=customer['name'].split()[0],
                amount=f"{amount:,}"
            )

            scheduled_hours = detected_hours_ago - random.randint(2, 12)
            executed_hours = scheduled_hours - random.randint(1, 4)

            cur.execute("""
                INSERT INTO interventions (id, revenue_risk_id, intervention_type, intervention_strategy,
                                         channel, content, scheduled_at, executed_at, status, outcome,
                                         ai_reasoning, cost)
                VALUES (%s, %s, %s, %s, %s, %s,
                        NOW() - INTERVAL '%s hours',
                        NOW() - INTERVAL '%s hours',
                        'executed', 'success', %s, %s)
            """, (intervention_uuid, risk_uuid, intervention_type, strategy, channel, message,
                  scheduled_hours, executed_hours,
                  f"AI selected {intervention_type} via {channel} based on customer tier and risk amount",
                  random.randint(5, 50)))

            # Audit trail for AI analysis
            cur.execute("""
                INSERT INTO audit_trail (id, entity_type, entity_id, action, actor, details,
                                       compliance_check, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW() - INTERVAL '%s hours')
            """, (str(uuid.uuid4()), 'revenue_risk', risk_uuid, 'ai_analysis_completed',
                  'ai_agent', json.dumps({
                      'model': 'openai/gpt-oss-120b',
                      'diagnosis': ai_diag['diagnosis'],
                      'confidence': ai_diag['confidence'],
                      'recommended_action': intervention_type
                  }), json.dumps({'passed': True, 'checks': ['gdpr_compliance', 'communication_frequency']}),
                  scheduled_hours + 1))

            # Audit trail for intervention execution
            cur.execute("""
                INSERT INTO audit_trail (id, entity_type, entity_id, action, actor, details,
                                       compliance_check, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW() - INTERVAL '%s hours')
            """, (str(uuid.uuid4()), 'intervention', intervention_uuid, 'intervention_executed',
                  'system', json.dumps({
                      'type': intervention_type,
                      'channel': channel,
                      'recipient': customer['email'],
                      'message_sent': True
                  }), json.dumps({'passed': True, 'checks': ['opt_in_verified', 'rate_limit_ok']}),
                  executed_hours))

            # Create recovery outcome
            recovered_amount = amount * random.uniform(0.85, 1.0)  # 85-100% recovery
            recovery_time = detected_hours_ago - executed_hours

            cur.execute("""
                INSERT INTO recovery_outcomes (id, revenue_risk_id, intervention_id,
                                             recovered_amount, recovered_at, recovery_method,
                                             time_to_recovery, customer_feedback)
                VALUES (%s, %s, %s, %s, NOW() - INTERVAL '%s hours', %s, %s, %s)
            """, (str(uuid.uuid4()), risk_uuid, intervention_uuid, recovered_amount,
                  executed_hours - random.randint(1, 12),
                  f"{intervention_type}_via_{channel}",
                  recovery_time / 24.0,  # Convert to days
                  "Thank you for the reminder!" if random.random() > 0.5 else None))

            # Audit trail for recovery
            cur.execute("""
                INSERT INTO audit_trail (id, entity_type, entity_id, action, actor, details,
                                       compliance_check, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW() - INTERVAL '%s hours')
            """, (str(uuid.uuid4()), 'revenue_risk', risk_uuid, 'revenue_recovered',
                  'customer', json.dumps({
                      'original_amount': amount,
                      'recovered_amount': recovered_amount,
                      'recovery_rate': (recovered_amount / amount) * 100,
                      'intervention': intervention_type
                  }), json.dumps({'passed': True, 'checks': ['payment_verified', 'fraud_check']}),
                  executed_hours - random.randint(1, 8)))

        risks_created += 1

    conn.commit()
    print(f"✅ Created {risks_created} revenue risks")
    print(f"   - {recovered_count} recovered")
    print(f"   - {pending_count} pending")
    print()

    # Verify data
    print("Verifying complete dataset...")
    cur.execute("SELECT COUNT(*) FROM customers")
    print(f"✅ Customers: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM revenue_risks")
    print(f"✅ Revenue Risks: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM interventions")
    print(f"✅ Interventions: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM recovery_outcomes")
    print(f"✅ Recovery Outcomes: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM audit_trail")
    print(f"✅ Audit Trail Entries: {cur.fetchone()[0]}")

    cur.execute("SELECT SUM(risk_amount) FROM revenue_risks WHERE status='active'")
    total_at_risk = cur.fetchone()[0] or 0
    print(f"✅ Total at Risk: ₹{total_at_risk:,.0f}")

    cur.execute("SELECT SUM(recovered_amount) FROM recovery_outcomes")
    total_recovered = cur.fetchone()[0] or 0
    print(f"✅ Total Recovered: ₹{total_recovered:,.0f}")

    cur.close()
    conn.close()

    print()
    print("=" * 60)
    print("  ✅ Complete Demo Data Created Successfully!")
    print("=" * 60)
    print()
    print("Your system now has:")
    print("- 50 customers with realistic profiles")
    print("- 50 revenue risks (30 recovered, 20 pending)")
    print("- 30 interventions with AI reasoning")
    print("- 30 recovery outcomes with metrics")
    print(f"- {30 * 4 + 20} audit trail entries (full compliance log)")
    print()
    print("✅ Ready for hackathon demo!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
