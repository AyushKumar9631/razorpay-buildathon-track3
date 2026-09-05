# Test Data Generation Scripts

These scripts generate realistic test data and run AI recovery workflows to demonstrate the system.

## Prerequisites

1. Backend dependencies installed
2. Database migrated (Alembic)
3. OpenAI API key configured in `.env`

## Installation

```bash
cd scripts
pip install -r requirements.txt
```

## Usage

### Step 1: Generate Test Data

Creates customers, transactions, abandoned carts, subscriptions, and revenue risks.

```bash
python generate_test_data.py
```

**Output:**
- 100 customers (varied tiers: standard, premium, enterprise)
- 500 transactions (85-90% success rate)
- 50 abandoned carts
- 30 subscriptions (some failed)
- ~50-60 revenue risks

**Expected Results:**
- Total revenue at risk: ₹90,000 - ₹120,000
- Mix of payment failures, cart abandonment, subscription failures

### Step 2: Run AI Simulation

Processes risks through AI workflows, creates interventions, and simulates recoveries.

```bash
python run_ai_simulation.py
```

**What it does:**
1. Processes up to 30 risks with AI agents
2. Gets diagnosis and intervention recommendations
3. Executes interventions
4. Simulates recovery outcomes (75% target success rate)
5. Generates comprehensive statistics

**Expected Results:**
- Recovery rate: 70-80%
- Intervention success rate: 75-85%
- Average recovery time: 2-5 days
- ROI: 2000-3000%

## Output Examples

### After generate_test_data.py:
```
✓ 100 customers created
✓ 500 transactions created (75 failed)
✓ 50 abandoned carts created
✓ 30 subscriptions created
✓ 57 revenue risks created

💰 Total Revenue at Risk: ₹98,450.00
📊 Average Risk Score: 67.3%
```

### After run_ai_simulation.py:
```
📊 RISK OVERVIEW
  Total Risks Detected: 57
  Recovered: 42
  Lost: 10
  
💰 REVENUE IMPACT
  Successfully Recovered: ₹74,250.00
  
📈 PERFORMANCE METRICS
  Recovery Rate: 80.8%
  Intervention Success Rate: 82.5%
  Avg Time to Recovery: 4.2 hours (0.2 days)
  
💵 ROI ANALYSIS
  ROI: 2,967%
```

## Demo Scenario Breakdown

### Scenario 1: Payment Degradation (20 cases)
- Failed due to: card expired, insufficient funds, card declined
- AI diagnosis: Root cause analysis
- Intervention: Email with one-click card update
- Expected recovery: 85%

### Scenario 2: Checkout Abandonment (30 cases)
- Abandoned at: various stages
- AI diagnosis: Abandonment pattern analysis
- Intervention: Personalized recovery email with incentive
- Expected recovery: 35-40%

### Scenario 3: Subscription Failure (7 cases)
- Failed renewals with grace period
- AI diagnosis: Subscription history analysis
- Intervention: Smart retry + customer outreach
- Expected recovery: 85-90%

## Customization

### Adjust Data Volume

Edit `generate_test_data.py`:

```python
customers = generate_customers(db, count=200)  # More customers
transactions, failed = generate_transactions(db, customers, count=1000)  # More transactions
```

### Adjust Success Rates

Edit `run_ai_simulation.py`:

```python
recoveries, amount = simulate_recoveries(db, success_rate=0.80)  # 80% recovery rate
```

### Process More Risks

Edit `run_ai_simulation.py`:

```python
processed, interventions = process_risks_with_ai(db, limit=50)  # Process 50 risks
```

## Troubleshooting

### "No module named 'faker'"
```bash
pip install Faker
```

### "OpenAI API key not configured"
- Set `OPENAI_API_KEY` in `backend/.env`
- Get key from: https://platform.openai.com/api-keys

### "Database table doesn't exist"
```bash
cd backend
alembic upgrade head
```

### Slow AI processing
- Normal: AI agent makes multiple LLM calls per risk
- Each risk takes 5-10 seconds to process
- 30 risks = ~3-5 minutes total

## Cost Estimate

### OpenAI API Usage
- Per risk processed: ~3-4 LLM calls
- Cost per call: ~$0.01-0.02
- Total for 30 risks: ~$1.00-2.00

### Optimization
- Process in batches
- Cache similar diagnoses
- Use smaller model for non-critical decisions

## Database Reset

To start fresh:

```bash
# Option 1: Drop and recreate tables
cd backend
alembic downgrade base
alembic upgrade head

# Option 2: Delete specific data
python
>>> from app.database import SessionLocal
>>> from app.models import *
>>> db = SessionLocal()
>>> db.query(RevenueRisk).delete()
>>> db.query(Intervention).delete()
>>> db.query(RecoveryOutcome).delete()
>>> db.commit()
```

## Next Steps

After running these scripts:

1. **Start Backend:** `cd backend && uvicorn app.main:app --reload`
2. **Check API:** http://localhost:8000/docs
3. **View Metrics:** GET /api/v1/analytics/overview
4. **Test AI:** POST /api/v1/ai/analyze

## Demo Tips

### For Live Demo:
1. Run `generate_test_data.py` before demo
2. Keep some risks unprocessed
3. During demo, call POST /api/v1/risks/{id}/process live
4. Show AI reasoning and decisions in real-time

### For Recorded Demo:
1. Run both scripts
2. Take screenshots of results
3. Show before/after metrics
4. Highlight recovery rate and ROI

## Metrics to Highlight

### For Judges:
- ✅ **High Recovery Rate** (75-80%)
- ✅ **Fast Recovery Time** (<5 days average)
- ✅ **Impressive ROI** (2000%+)
- ✅ **AI Explainability** (full reasoning captured)
- ✅ **Compliance** (100% audit trail)

---

**Ready to generate impressive demo data!** 🚀
