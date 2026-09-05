"""
Add realistic test data with active interventions and failed recoveries
Keeps existing data and adds:
- 20 new risks with active interventions (in progress)
- 10 failed recovery attempts (to reduce success rate)
"""
import psycopg2
from datetime import datetime, timedelta
import random
import uuid
import json

# REPLACE THIS with your actual Supabase connection string
DATABASE_URL = "postgresql://postgres.fxhpydjdnwynpywnzpmi:Appleballcatdo@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

print("=" * 60)
print("  Adding Realistic Demo Data")
print("=" * 60)
print()

# Sample data
CUSTOMER_NAMES = [
    "Aditya Sharma", "Priyanka Gupta", "Karthik Reddy", "Meera Nair", "Siddharth Joshi",
    "Anjali Iyer", "Rahul Malhotra", "Deepika Singh", "Varun Kapoor", "Shreya Desai",
    "Nikhil Patel", "Tanvi Agarwal", "Akash Verma", "Isha Menon", "Aryan Khanna",
    "Riya Bhat", "Kunal Shah", "Nandini Rao", "Rohan Mehta", "Kavita Pillai"
]

RISK_TYPES = ['payment_failure', 'checkout_abandonment', 'subscription_failure', 'b2b_receivable']
PRIORITIES = ['low', 'medium', 'high']
TIERS = ['standard', 'premium', 'enterprise']

INTERVENTION_TYPES = ['email', 'sms', 'payment_retry', 'voice_call', 'payment_plan', 'personalized_offer', 'whatsapp']
CHANNELS = ['email', 'sms', 'whatsapp', 'voice', 'in_app']

FAILURE_REASONS = [
    "Card declined by issuing bank - retry recommended",
    "3D Secure authentication failed - customer abandoned",
    "Payment gateway timeout - technical issue",
    "Card CVV mismatch - security check failed",
    "Customer opted out during checkout flow",
    "Bank server unavailable - retry after 24 hours",
    "Subscription auto-renewal blocked by customer",
    "Invoice disputed - customer claims non-receipt"
]

AI_DIAGNOSES_ACTIVE = [
    {
        "diagnosis": "Payment gateway timeout. No customer fault detected.",
        "root_cause": "Technical issue on payment processor side",
        "recommended_intervention": "Immediate payment retry via email with assistance offer",
        "reasoning": "Customer attempted payment but gateway failed. High conversion probability with proactive support.",
        "confidence": 0.89
    },
    {
        "diagnosis": "Card CVV mismatch - possible customer data entry error.",
        "root_cause": "Incorrect card details entered",
        "recommended_intervention": "Send SMS with payment link and instructions",
        "reasoning": "Customer intent is clear. Simple data correction needed.",
        "confidence": 0.91
    },
    {
        "diagnosis": "High-value cart abandoned at shipping details page.",
        "root_cause": "Unexpected shipping cost or delivery timeline",
        "recommended_intervention": "Personalized offer with expedited shipping discount",
        "reasoning": "Cart value ₹25,000+ justifies intervention cost. Address shipping concerns.",
        "confidence": 0.88
    }
]

AI_DIAGNOSES_FAILED = [
    {
        "diagnosis": "Customer explicitly declined payment - low recovery probability.",
        "root_cause": "Customer changed mind or found alternative",
        "recommended_intervention": "Gentle reminder email with value proposition",
        "reasoning": "Explicit opt-out suggests low intent. Intervention unlikely to succeed.",
        "confidence": 0.45
    },
    {
        "diagnosis": "Invoice disputed due to service quality issues.",
        "root_cause": "Customer dissatisfaction with product/service",
        "recommended_intervention": "Customer support escalation before payment request",
        "reasoning": "Payment issue is secondary to service complaint. Requires resolution first.",
        "confidence": 0.52
    }
]

RECOVERY_MESSAGES = [
    "Hi {name}, your payment didn't go through due to a technical issue. Please try again: [link]",
    "We noticed a problem with your card details. Update and complete your ₹{amount} order: [link]",
    "{name}, your subscription renewal failed. Update payment method to avoid service interruption: [link]",
    "Hi {name}, complete your ₹{amount} order today! We've reserved your items for 48 hours: [link]"
]

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    print("✅ Connected to database!")
    print()

    # Get existing customer count
    cur.execute("SELECT COUNT(*) FROM customers")
    existing_customers = cur.fetchone()[0]
    print(f"Existing customers: {existing_customers}")

    cur.execute("SELECT COUNT(*) FROM revenue_risks")
    existing_risks = cur.fetchone()[0]
    print(f"Existing risks: {existing_risks}")
    print()

    # Create 20 new customers for new risks
    print("Creating 20 new customers...")
    customers = []
    for i in range(20):
        customer_uuid = str(uuid.uuid4())
        customer_id = f"CUST{3000 + i}"
        name = CUSTOMER_NAMES[i % len(CUSTOMER_NAMES)]
        email = f"{name.lower().replace(' ', '.')}_{3000+i}@example.com"
        tier = random.choice(TIERS)
        ltv = random.randint(15000, 150000)

        cur.execute("""
            INSERT INTO customers (id, customer_id, email, name, tier, lifetime_value,
                                 total_transactions, failed_transactions, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW() - INTERVAL '%s days', NOW())
        """, (customer_uuid, customer_id, email, name, tier, ltv,
              random.randint(3, 30), random.randint(1, 5), random.randint(1, 60)))

        customers.append({
            'uuid': customer_uuid,
            'customer_id': customer_id,
            'name': name,
            'email': email,
            'tier': tier
        })

    conn.commit()
    print(f"✅ Created {len(customers)} new customers")
    print()

    # ========================================
    # Part 1: Add 20 risks with ACTIVE interventions
    # ========================================
    print("Creating 20 risks with active interventions...")
    active_count = 0

    for i in range(20):
        customer = customers[i]
        risk_uuid = str(uuid.uuid4())
        risk_type = random.choice(RISK_TYPES)
        amount = random.randint(5000, 85000)
        priority = random.choice(PRIORITIES)
        risk_score = random.randint(70, 95)
        detected_hours_ago = random.randint(6, 72)  # Last 3 days

        ai_diag = random.choice(AI_DIAGNOSES_ACTIVE)
        root_cause = random.choice(FAILURE_REASONS)

        # Insert risk
        cur.execute("""
            INSERT INTO revenue_risks (id, customer_id, risk_type, risk_amount, risk_score,
                                      status, priority, root_cause, ai_diagnosis, detected_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW() - INTERVAL '%s hours')
        """, (risk_uuid, customer['uuid'], risk_type, amount, risk_score,
              'active', priority, root_cause, json.dumps(ai_diag), detected_hours_ago))

        # Audit: risk detected
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

        # Create active intervention
        intervention_uuid = str(uuid.uuid4())
        intervention_type = random.choice(INTERVENTION_TYPES)
        channel = random.choice(CHANNELS)
        strategy = f"recovery_{intervention_type}"

        message = random.choice(RECOVERY_MESSAGES).format(
            name=customer['name'].split()[0],
            amount=f"{amount:,}"
        )

        scheduled_hours = detected_hours_ago - random.randint(1, 6)

        cur.execute("""
            INSERT INTO interventions (id, revenue_risk_id, intervention_type, intervention_strategy,
                                     channel, content, scheduled_at, status,
                                     ai_reasoning, cost)
            VALUES (%s, %s, %s, %s, %s, %s,
                    NOW() - INTERVAL '%s hours',
                    'scheduled', %s, %s)
        """, (intervention_uuid, risk_uuid, intervention_type, strategy, channel, message,
              scheduled_hours,
              f"AI selected {intervention_type} via {channel} - awaiting execution",
              random.randint(5, 30)))

        # Audit: AI analysis
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

        # Audit: Intervention scheduled
        cur.execute("""
            INSERT INTO audit_trail (id, entity_type, entity_id, action, actor, details,
                                   compliance_check, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW() - INTERVAL '%s hours')
        """, (str(uuid.uuid4()), 'intervention', intervention_uuid, 'intervention_scheduled',
              'system', json.dumps({
                  'type': intervention_type,
                  'channel': channel,
                  'recipient': customer['email'],
                  'scheduled_for': 'next_available_slot'
              }), json.dumps({'passed': True, 'checks': ['opt_in_verified', 'rate_limit_ok']}),
              scheduled_hours))

        active_count += 1

    conn.commit()
    print(f"✅ Created {active_count} risks with active interventions")
    print()

    # ========================================
    # Part 2: Add 10 FAILED recovery attempts
    # ========================================
    print("Creating 10 failed recovery attempts...")
    failed_count = 0

    # Get 10 existing customers to use
    cur.execute("SELECT id, customer_id, email, name FROM customers ORDER BY RANDOM() LIMIT 10")
    existing_customers_data = cur.fetchall()

    for i, (cust_uuid, cust_id, cust_email, cust_name) in enumerate(existing_customers_data):
        risk_uuid = str(uuid.uuid4())
        risk_type = random.choice(RISK_TYPES)
        amount = random.randint(3000, 40000)
        priority = random.choice(PRIORITIES)
        risk_score = random.randint(50, 75)
        detected_hours_ago = random.randint(96, 240)  # 4-10 days ago

        ai_diag = random.choice(AI_DIAGNOSES_FAILED)
        root_cause = random.choice(FAILURE_REASONS)

        # Insert risk with status='lost'
        cur.execute("""
            INSERT INTO revenue_risks (id, customer_id, risk_type, risk_amount, risk_score,
                                      status, priority, root_cause, ai_diagnosis, detected_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW() - INTERVAL '%s hours')
        """, (risk_uuid, cust_uuid, risk_type, amount, risk_score,
              'lost', priority, root_cause, json.dumps(ai_diag), detected_hours_ago))

        # Audit: risk detected
        cur.execute("""
            INSERT INTO audit_trail (id, entity_type, entity_id, action, actor, details,
                                   compliance_check, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW() - INTERVAL '%s hours')
        """, (str(uuid.uuid4()), 'revenue_risk', risk_uuid, 'risk_detected',
              'system', json.dumps({
                  'risk_type': risk_type,
                  'amount': amount,
                  'customer': cust_email,
                  'detection_method': 'automated_monitoring'
              }), json.dumps({'passed': True, 'checks': ['amount_threshold', 'customer_validation']}),
              detected_hours_ago))

        # Create failed intervention
        intervention_uuid = str(uuid.uuid4())
        intervention_type = random.choice(INTERVENTION_TYPES)
        channel = random.choice(CHANNELS)
        strategy = f"recovery_{intervention_type}"

        message = random.choice(RECOVERY_MESSAGES).format(
            name=cust_name.split()[0] if cust_name else "Customer",
            amount=f"{amount:,}"
        )

        scheduled_hours = detected_hours_ago - random.randint(12, 48)
        executed_hours = scheduled_hours - random.randint(1, 6)

        cur.execute("""
            INSERT INTO interventions (id, revenue_risk_id, intervention_type, intervention_strategy,
                                     channel, content, scheduled_at, executed_at, status, outcome,
                                     ai_reasoning, cost)
            VALUES (%s, %s, %s, %s, %s, %s,
                    NOW() - INTERVAL '%s hours',
                    NOW() - INTERVAL '%s hours',
                    'executed', 'failed', %s, %s)
        """, (intervention_uuid, risk_uuid, intervention_type, strategy, channel, message,
              scheduled_hours, executed_hours,
              f"AI selected {intervention_type} via {channel} but customer did not respond",
              random.randint(5, 30)))

        # Audit: AI analysis
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

        # Audit: Intervention executed (but failed)
        cur.execute("""
            INSERT INTO audit_trail (id, entity_type, entity_id, action, actor, details,
                                   compliance_check, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW() - INTERVAL '%s hours')
        """, (str(uuid.uuid4()), 'intervention', intervention_uuid, 'intervention_failed',
              'system', json.dumps({
                  'type': intervention_type,
                  'channel': channel,
                  'recipient': cust_email,
                  'failure_reason': 'customer_unresponsive'
              }), json.dumps({'passed': True, 'checks': ['delivery_confirmed', 'compliance_met']}),
              executed_hours))

        failed_count += 1

    conn.commit()
    print(f"✅ Created {failed_count} failed recovery attempts")
    print()

    # Verify final data
    print("Final Dataset Summary:")
    print("=" * 60)

    cur.execute("SELECT COUNT(*) FROM customers")
    print(f"✅ Total Customers: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM revenue_risks")
    print(f"✅ Total Revenue Risks: {cur.fetchone()[0]}")

    cur.execute("SELECT status, COUNT(*) FROM revenue_risks GROUP BY status")
    for status, count in cur.fetchall():
        print(f"   - {status}: {count}")

    cur.execute("SELECT COUNT(*) FROM interventions")
    print(f"✅ Total Interventions: {cur.fetchone()[0]}")

    cur.execute("SELECT status, COUNT(*) FROM interventions GROUP BY status")
    for status, count in cur.fetchall():
        print(f"   - {status}: {count}")

    cur.execute("SELECT COUNT(*) FROM audit_trail")
    print(f"✅ Total Audit Trail Entries: {cur.fetchone()[0]}")

    # Calculate success rate
    cur.execute("SELECT COUNT(*) FROM revenue_risks WHERE status='recovered'")
    recovered = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM revenue_risks WHERE status='lost'")
    lost = cur.fetchone()[0]
    success_rate = (recovered / (recovered + lost) * 100) if (recovered + lost) > 0 else 0
    print(f"✅ Recovery Success Rate: {success_rate:.1f}%")

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
    print("  ✅ Realistic Demo Data Added Successfully!")
    print("=" * 60)
    print()
    print("Your system now has:")
    print(f"- {recovered} recovered risks (success)")
    print(f"- {lost} lost risks (failed recoveries)")
    print(f"- 20 active risks with scheduled interventions")
    print(f"- {success_rate:.1f}% recovery success rate (realistic)")
    print()
    print("✅ Ready for realistic hackathon demo!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
