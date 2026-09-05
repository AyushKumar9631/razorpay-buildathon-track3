# Add Realistic Test Data

This script adds more realistic test data while keeping your existing 50 risks.

## What it adds:
- **20 new risks** with ACTIVE interventions (scheduled, not yet executed)
- **10 failed recovery attempts** (to make success rate more realistic, not 100%)
- **20 new customers**
- **90+ new audit trail entries**

## Final Result:
- Total risks: 80
  - 30 recovered (success)
  - 10 lost (failed)
  - 20 active with interventions in progress
  - 20 pending (from original data)
- Recovery success rate: ~75% (more realistic than 100%)
- Active interventions you can track in real-time

## How to Run:

1. **Update database connection string:**
   Edit line 12 in `add_realistic_data.py`:
   ```python
   DATABASE_URL = "YOUR_SUPABASE_CONNECTION_STRING"
   ```

2. **Run the script:**
   ```bash
   cd scripts
   python add_realistic_data.py
   ```

3. **Verify in your dashboard:**
   - Dashboard should show updated metrics
   - Risks page will have 80 total risks
   - Interventions page will show scheduled interventions
   - Audit trail will have 200+ entries
   - Success rate will be ~75% (not 100%)

## What makes this realistic:

✅ **Active Interventions** - Some risks have interventions that are scheduled but not yet executed (real-world scenario)

✅ **Failed Recoveries** - 10 risks where interventions were executed but customer didn't respond (realistic failure cases)

✅ **Lower Success Rate** - ~75% instead of 100% (more believable for demo)

✅ **Various Stages** - Mix of pending, active, recovered, and lost risks

✅ **Complete Audit Trail** - Every action is logged with compliance checks
