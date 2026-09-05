"""
Generate test data directly via SQL for demo
This creates customers, transactions, and risks
"""
import psycopg2
from datetime import datetime, timedelta
import random
import uuid

# REPLACE THIS with your actual Supabase connection string
DATABASE_URL = "postgresql://postgres.fxhpydjdnwynpywnzpmi:Appleballcatdo@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

print("=" * 60)
print("  Generating Test Data Directly in Database")
print("=" * 60)
print()

try:
    # Connect to database
    print("Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    print("✅ Connected!")
    print()

    # Generate customers
    print("Creating 20 customers...")
    customers = []
    for i in range(20):
        customer_id = f"CUST{1000 + i}"
        email = f"customer{i+1}@example.com"
        name = f"Test Customer {i+1}"
        tier = random.choice(['standard', 'premium', 'enterprise'])
        ltv = random.randint(10000, 100000)

        cur.execute("""
            INSERT INTO customers (id, customer_id, email, name, tier, lifetime_value, total_transactions, failed_transactions, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (str(uuid.uuid4()), customer_id, email, name, tier, ltv, 0, 0))

        customers.append((customer_id, email))

    conn.commit()
    print(f"✅ Created {len(customers)} customers")
    print()

    # Generate failed transactions
    print("Creating 30 failed transactions...")
    for i in range(30):
        customer_id, email = random.choice(customers)
        amount = random.randint(1000, 50000)

        cur.execute("""
            INSERT INTO transactions (id, transaction_id, customer_id, amount, currency, status, payment_method, failure_reason, created_at, updated_at)
            SELECT %s, %s, c.id, %s, 'INR', 'failed', 'card', 'insufficient_funds', NOW() - INTERVAL '%s hours', NOW()
            FROM customers c WHERE c.customer_id = %s
        """, (str(uuid.uuid4()), f"TXN{i+1000}", amount, random.randint(1, 72), customer_id))

    conn.commit()
    print("✅ Created 30 failed transactions")
    print()

    # Generate revenue risks
    print("Creating 30 revenue risks...")
    for i in range(30):
        customer_id, email = random.choice(customers)
        risk_type = random.choice(['payment_failure', 'checkout_abandonment', 'subscription_failure'])
        amount = random.randint(1000, 50000)
        priority = random.choice(['low', 'medium', 'high'])
        risk_score = random.randint(60, 95)

        cur.execute("""
            INSERT INTO revenue_risks (id, customer_id, risk_type, risk_amount, risk_score, status, priority, detected_at)
            SELECT %s, c.id, %s, %s, %s, 'active', %s, NOW() - INTERVAL '%s hours'
            FROM customers c WHERE c.customer_id = %s
        """, (str(uuid.uuid4()), risk_type, amount, risk_score, priority, random.randint(1, 48), customer_id))

    conn.commit()
    print("✅ Created 30 revenue risks")
    print()

    # Verify data
    print("Verifying data...")
    cur.execute("SELECT COUNT(*) FROM customers")
    customer_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM transactions")
    transaction_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM revenue_risks")
    risk_count = cur.fetchone()[0]

    cur.execute("SELECT SUM(risk_amount) FROM revenue_risks WHERE status='active'")
    total_at_risk = cur.fetchone()[0] or 0

    print(f"✅ Customers: {customer_count}")
    print(f"✅ Transactions: {transaction_count}")
    print(f"✅ Revenue Risks: {risk_count}")
    print(f"✅ Total at Risk: ₹{total_at_risk:,.0f}")
    print()

    cur.close()
    conn.close()

    print("=" * 60)
    print("  ✅ Test Data Created Successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Refresh your frontend dashboard")
    print("2. You should now see data!")
    print("3. Click 'Process with AI' to analyze risks")
    print()

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Make sure you updated DATABASE_URL in the script!")
