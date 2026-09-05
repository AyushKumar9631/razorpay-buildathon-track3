"""
Generate test data by calling the deployed backend API
No local dependencies needed!
"""
import requests
import time
import random
from datetime import datetime, timedelta

# Your deployed backend URL
BACKEND_URL = "https://razorpay-buildathon-track3.onrender.com"

print("=" * 60)
print("  Generating Test Data via API")
print("=" * 60)
print()

def create_risk_via_api(customer_email, amount, risk_type):
    """Create a risk by simulating a failed transaction"""
    try:
        # We'll use the risks detection endpoint
        response = requests.post(
            f"{BACKEND_URL}/api/v1/risks/detect",
            json={
                "customer_email": customer_email,
                "amount": amount,
                "risk_type": risk_type
            },
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  ⚠️  API returned {response.status_code}")
            return None
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

# Test data scenarios
scenarios = [
    {"email": "rajesh.kumar@example.com", "amount": 5000, "type": "payment_failure"},
    {"email": "priya.sharma@example.com", "amount": 12000, "type": "checkout_abandonment"},
    {"email": "amit.patel@example.com", "amount": 25000, "type": "subscription_failure"},
    {"email": "sneha.reddy@example.com", "amount": 8500, "type": "payment_failure"},
    {"email": "vikram.singh@example.com", "amount": 15000, "type": "b2b_receivable"},
    {"email": "anita.desai@example.com", "amount": 3200, "type": "checkout_abandonment"},
    {"email": "rohit.mehta@example.com", "amount": 45000, "type": "payment_failure"},
    {"email": "kavya.nair@example.com", "amount": 9800, "type": "subscription_failure"},
    {"email": "sanjay.verma@example.com", "amount": 67000, "type": "b2b_receivable"},
    {"email": "neha.agarwal@example.com", "amount": 4300, "type": "payment_failure"},
]

print(f"Backend URL: {BACKEND_URL}")
print(f"Creating {len(scenarios)} test scenarios...")
print()

created_count = 0
for i, scenario in enumerate(scenarios, 1):
    print(f"[{i}/{len(scenarios)}] Creating risk for {scenario['email']}... ", end="", flush=True)

    result = create_risk_via_api(
        scenario["email"],
        scenario["amount"],
        scenario["type"]
    )

    if result:
        print("✅")
        created_count += 1
    else:
        print("❌")

    # Small delay to avoid rate limiting
    time.sleep(0.5)

print()
print("=" * 60)
print(f"  ✅ Created {created_count}/{len(scenarios)} test risks!")
print("=" * 60)
print()
print("Next steps:")
print("1. Visit your frontend to see the data")
print("2. Click 'Process with AI' to analyze risks")
print()
print("Frontend URL: (check your Vercel deployment)")
print(f"Backend API: {BACKEND_URL}/docs")
print()
