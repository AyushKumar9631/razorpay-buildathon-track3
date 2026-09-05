"""
Generate realistic test data for AI Revenue Recovery demo.

This script creates:
- Customers with varied profiles
- Transactions (successful and failed)
- Abandoned carts
- Subscriptions
- Revenue risks

Run this to populate the database with demo data.
"""
import random
from datetime import datetime, timedelta
from decimal import Decimal
from faker import Faker
import uuid

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.subscription import CustomerSubscription, AbandonedCart
from app.models.risk import RevenueRisk

fake = Faker()


# Constants
CUSTOMER_TIERS = ['standard', 'premium', 'enterprise']
CUSTOMER_TYPES = ['B2C', 'B2B']
PAYMENT_METHODS = ['card', 'upi', 'netbanking', 'wallet']
TRANSACTION_STATUSES = ['success', 'failed']
FAILURE_REASONS = [
    'card_expired',
    'insufficient_funds',
    'card_declined',
    'network_error',
    'invalid_cvv',
    'bank_timeout',
    'mandate_cancelled',
    'card_lost_stolen'
]
CART_STAGES = ['product_view', 'cart', 'checkout_info', 'payment']


def random_amount(min_val: float = 100, max_val: float = 50000) -> Decimal:
    """Generate random transaction amount."""
    return Decimal(str(round(random.uniform(min_val, max_val), 2)))


def random_date(start_days_ago: int = 90, end_days_ago: int = 0) -> datetime:
    """Generate random datetime in the past."""
    start = datetime.utcnow() - timedelta(days=start_days_ago)
    end = datetime.utcnow() - timedelta(days=end_days_ago)
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)


def generate_customers(db: Session, count: int = 100) -> list:
    """Generate customer profiles."""
    customers = []

    print(f"Generating {count} customers...")

    for i in range(count):
        tier = random.choices(
            CUSTOMER_TIERS,
            weights=[60, 30, 10],  # More standard, fewer enterprise
            k=1
        )[0]

        customer_type = random.choices(
            CUSTOMER_TYPES,
            weights=[70, 30],  # More B2C than B2B
            k=1
        )[0]

        customer = Customer(
            customer_id=f"CUST{str(uuid.uuid4())[:8].upper()}",
            email=fake.email(),
            phone=fake.phone_number()[:20],
            name=fake.name(),
            customer_type=customer_type,
            tier=tier,
            lifetime_value=Decimal('0'),
            total_transactions=0,
            failed_transactions=0,
            communication_preferences={
                "email": True,
                "sms": random.choice([True, False]),
                "preferred_language": random.choice(["english", "hinglish"])
            },
            metadata={
                "signup_date": random_date(365, 30).isoformat(),
                "source": random.choice(["web", "mobile_app", "referral"])
            },
            created_at=random_date(365, 30)
        )

        db.add(customer)
        customers.append(customer)

        if (i + 1) % 20 == 0:
            print(f"  Created {i + 1} customers...")

    db.commit()
    print(f"✓ Created {count} customers")
    return customers


def generate_transactions(db: Session, customers: list, count: int = 500) -> tuple:
    """Generate transaction history."""
    transactions = []
    failed_transactions = []

    print(f"Generating {count} transactions...")

    for i in range(count):
        customer = random.choice(customers)

        # Higher success rate for premium/enterprise
        if customer.tier == 'enterprise':
            success_rate = 0.95
        elif customer.tier == 'premium':
            success_rate = 0.90
        else:
            success_rate = 0.85

        status = 'success' if random.random() < success_rate else 'failed'

        # Amount varies by customer tier
        if customer.tier == 'enterprise':
            amount = random_amount(5000, 50000)
        elif customer.tier == 'premium':
            amount = random_amount(1000, 10000)
        else:
            amount = random_amount(100, 2000)

        failure_reason = None
        failure_code = None
        if status == 'failed':
            failure_reason = random.choice(FAILURE_REASONS)
            failure_code = f"ERR_{failure_reason.upper()}"

        transaction = Transaction(
            transaction_id=f"TXN{str(uuid.uuid4())[:12].upper()}",
            customer_id=customer.id,
            amount=amount,
            currency='INR',
            status=status,
            payment_method=random.choice(PAYMENT_METHODS),
            failure_reason=failure_reason,
            failure_code=failure_code,
            metadata={
                "ip_address": fake.ipv4(),
                "user_agent": "Mozilla/5.0...",
                "device": random.choice(["mobile", "desktop", "tablet"])
            },
            created_at=random_date(60, 0)
        )

        db.add(transaction)
        transactions.append(transaction)

        if status == 'failed':
            failed_transactions.append(transaction)

        # Update customer stats
        customer.total_transactions += 1
        if status == 'success':
            customer.lifetime_value += amount
        else:
            customer.failed_transactions += 1

        if (i + 1) % 100 == 0:
            print(f"  Created {i + 1} transactions...")

    db.commit()
    print(f"✓ Created {count} transactions ({len(failed_transactions)} failed)")
    return transactions, failed_transactions


def generate_abandoned_carts(db: Session, customers: list, count: int = 50) -> list:
    """Generate abandoned cart data."""
    carts = []

    print(f"Generating {count} abandoned carts...")

    for i in range(count):
        customer = random.choice(customers)

        # Random cart items
        num_items = random.randint(1, 5)
        items = []
        total_amount = Decimal('0')

        for _ in range(num_items):
            item_price = random_amount(500, 5000)
            items.append({
                "product_id": f"PROD{random.randint(1000, 9999)}",
                "name": fake.word().title() + " " + fake.word().title(),
                "price": float(item_price),
                "quantity": 1
            })
            total_amount += item_price

        cart = AbandonedCart(
            cart_id=f"CART{str(uuid.uuid4())[:12].upper()}",
            customer_id=customer.id,
            session_id=str(uuid.uuid4()),
            items=items,
            total_amount=total_amount,
            abandoned_at=random_date(7, 0),
            abandonment_stage=random.choice(CART_STAGES),
            recovery_status='pending'
        )

        db.add(cart)
        carts.append(cart)

    db.commit()
    print(f"✓ Created {count} abandoned carts")
    return carts


def generate_subscriptions(db: Session, customers: list, count: int = 30) -> list:
    """Generate subscription data."""
    subscriptions = []

    print(f"Generating {count} subscriptions...")

    # Select customers who are likely to have subscriptions
    subscription_customers = [c for c in customers if c.tier in ['premium', 'enterprise']]

    for i in range(min(count, len(subscription_customers))):
        customer = subscription_customers[i]

        # Subscription amounts
        if customer.tier == 'enterprise':
            amount = random_amount(5000, 20000)
        else:
            amount = random_amount(500, 2000)

        # Some subscriptions have failed
        failed = random.random() < 0.25  # 25% failure rate

        subscription = CustomerSubscription(
            customer_id=customer.id,
            subscription_id=f"SUB{str(uuid.uuid4())[:12].upper()}",
            plan_name=random.choice(['Basic Plan', 'Pro Plan', 'Enterprise Plan']),
            amount=amount,
            billing_cycle=random.choice(['monthly', 'quarterly', 'annual']),
            status='failed' if failed else 'active',
            next_billing_date=datetime.utcnow().date() + timedelta(days=random.randint(1, 30)),
            failed_attempts=random.randint(1, 3) if failed else 0,
            last_failure_date=random_date(7, 0) if failed else None,
            grace_period_end=(datetime.utcnow() + timedelta(days=7)).date() if failed else None
        )

        db.add(subscription)
        subscriptions.append(subscription)

    db.commit()
    print(f"✓ Created {len(subscriptions)} subscriptions")
    return subscriptions


def generate_risks(db: Session, failed_transactions: list, carts: list, subscriptions: list) -> list:
    """Generate revenue risk records."""
    risks = []

    print("Generating revenue risks...")

    # Risks from failed transactions
    for transaction in failed_transactions[:20]:  # Take first 20 failed transactions
        customer = db.query(Customer).filter(Customer.id == transaction.customer_id).first()

        # Calculate risk score based on various factors
        base_score = 50
        if 'expired' in transaction.failure_reason.lower():
            base_score = 80  # Easy to fix
        elif 'insufficient' in transaction.failure_reason.lower():
            base_score = 60  # Medium difficulty
        else:
            base_score = 40  # Harder to fix

        # Adjust for customer tier
        if customer.tier == 'enterprise':
            base_score += 10
        elif customer.tier == 'premium':
            base_score += 5

        risk = RevenueRisk(
            transaction_id=transaction.id,
            customer_id=transaction.customer_id,
            risk_type='payment_failure',
            risk_amount=transaction.amount,
            risk_score=Decimal(str(min(base_score, 95))),
            detected_at=transaction.created_at + timedelta(minutes=5),
            status='active',
            root_cause=transaction.failure_reason,
            priority='high' if transaction.amount > 5000 else 'medium'
        )

        db.add(risk)
        risks.append(risk)

    # Risks from abandoned carts
    for cart in carts[:30]:  # Take first 30 carts
        risk = RevenueRisk(
            customer_id=cart.customer_id,
            risk_type='checkout_abandon',
            risk_amount=cart.total_amount,
            risk_score=Decimal('65'),  # Average recovery rate for carts
            detected_at=cart.abandoned_at + timedelta(hours=1),
            status='active',
            root_cause=f"Abandoned at {cart.abandonment_stage}",
            priority='medium'
        )

        db.add(risk)
        risks.append(risk)

    # Risks from failed subscriptions
    failed_subs = [s for s in subscriptions if s.status == 'failed']
    for subscription in failed_subs:
        risk = RevenueRisk(
            customer_id=subscription.customer_id,
            risk_type='subscription_failure',
            risk_amount=subscription.amount,
            risk_score=Decimal('70'),
            detected_at=subscription.last_failure_date or random_date(7, 0),
            status='active',
            root_cause=f"Subscription payment failed - {subscription.failed_attempts} attempts",
            priority='high' if subscription.amount > 1000 else 'medium'
        )

        db.add(risk)
        risks.append(risk)

    db.commit()
    print(f"✓ Created {len(risks)} revenue risks")
    return risks


def main():
    """Main function to generate all test data."""
    print("\n" + "="*60)
    print("AI Revenue Recovery - Test Data Generation")
    print("="*60 + "\n")

    db = SessionLocal()

    try:
        # Generate data
        customers = generate_customers(db, count=100)
        transactions, failed_transactions = generate_transactions(db, customers, count=500)
        carts = generate_abandoned_carts(db, customers, count=50)
        subscriptions = generate_subscriptions(db, customers, count=30)
        risks = generate_risks(db, failed_transactions, carts, subscriptions)

        # Summary
        print("\n" + "="*60)
        print("Data Generation Complete!")
        print("="*60)
        print(f"\n✓ {len(customers)} customers created")
        print(f"✓ {len(transactions)} transactions created ({len(failed_transactions)} failed)")
        print(f"✓ {len(carts)} abandoned carts created")
        print(f"✓ {len(subscriptions)} subscriptions created")
        print(f"✓ {len(risks)} revenue risks created")

        # Calculate totals
        total_at_risk = sum(float(r.risk_amount) for r in risks)
        print(f"\n💰 Total Revenue at Risk: ₹{total_at_risk:,.2f}")
        print(f"📊 Average Risk Score: {sum(float(r.risk_score) for r in risks) / len(risks):.1f}%")

        print("\n" + "="*60)
        print("Ready to run AI recovery workflows!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
