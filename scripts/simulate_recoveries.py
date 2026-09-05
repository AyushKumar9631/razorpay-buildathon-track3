"""
Simulate successful recoveries for demo
This will mark some risks as recovered and create recovery outcomes
"""
import psycopg2
from datetime import datetime, timedelta
import random
import uuid

# Your Supabase connection string
DATABASE_URL = "postgresql://postgres.fxhpydjdnwynpywnzpmi:Appleballcatdo@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

print("=" * 60)
print("  Simulating Revenue Recoveries")
print("=" * 60)
print()

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    print("✅ Connected to database")
    print()

    # Get some active risks to mark as recovered
    cur.execute("""
        SELECT id, risk_amount
        FROM revenue_risks
        WHERE status = 'active'
        LIMIT 15
    """)
    risks_to_recover = cur.fetchall()

    print(f"Marking {len(risks_to_recover)} risks as recovered...")

    total_recovered = 0
    for risk_id, risk_amount in risks_to_recover:
        # Mark risk as recovered
        cur.execute("""
            UPDATE revenue_risks
            SET status = 'recovered'
            WHERE id = %s
        """, (risk_id,))

        # Create recovery outcome
        recovery_amount = float(risk_amount) * random.uniform(0.8, 1.0)  # 80-100% recovery
        recovery_hours = random.uniform(1, 48)  # 1-48 hours

        cur.execute("""
            INSERT INTO recovery_outcomes
            (id, revenue_risk_id, recovered_amount, recovered_at, recovery_method, time_to_recovery)
            VALUES (%s, %s, %s, NOW() - INTERVAL '%s hours', %s, %s)
        """, (
            str(uuid.uuid4()),
            risk_id,
            recovery_amount,
            random.randint(1, 72),
            random.choice(['payment_retry', 'customer_contact', 'payment_plan']),
            recovery_hours
        ))

        total_recovered += recovery_amount

    conn.commit()
    print(f"✅ Marked 15 risks as recovered")
    print(f"✅ Total recovered: ₹{total_recovered:,.0f}")
    print()

    # Verify results
    cur.execute("SELECT COUNT(*) FROM revenue_risks WHERE status='active'")
    active_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM revenue_risks WHERE status='recovered'")
    recovered_count = cur.fetchone()[0]

    cur.execute("SELECT SUM(risk_amount) FROM revenue_risks WHERE status='active'")
    total_at_risk = cur.fetchone()[0] or 0

    cur.execute("SELECT SUM(recovered_amount) FROM recovery_outcomes")
    total_recovered_db = cur.fetchone()[0] or 0

    recovery_rate = (recovered_count / max(recovered_count + active_count, 1)) * 100

    print("=" * 60)
    print("  Current Stats")
    print("=" * 60)
    print(f"Active Risks: {active_count}")
    print(f"Recovered Risks: {recovered_count}")
    print(f"Total at Risk: ₹{float(total_at_risk):,.0f}")
    print(f"Total Recovered: ₹{float(total_recovered_db):,.0f}")
    print(f"Recovery Rate: {recovery_rate:.1f}%")
    print()

    cur.close()
    conn.close()

    print("=" * 60)
    print("  ✅ Recovery Simulation Complete!")
    print("=" * 60)
    print()
    print("Refresh your dashboard to see the updated numbers!")
    print()

except Exception as e:
    print(f"❌ Error: {e}")
