# KMPI Monitoring System

## Quick Overview

Automated system that monitors 4 KMPIs using cron jobs. Tests run automatically, reports are generated, and failures trigger alerts.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CRON SCHEDULER                            │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   ┌─────────┐         ┌──────────┐         ┌──────────┐
   │ MONTHLY │         │QUARTERLY │         │BI-ANNUAL │
   │ 1st/mo  │         │Jan/Apr/  │         │ Jan/Jul  │
   │ 2:00 AM │         │Jul/Oct   │         │ 4:00 AM  │
   │         │         │ 3:00 AM  │         │          │
   └────┬────┘         └─────┬────┘         └─────┬────┘
        │                    │                    │
        ▼                    │                    │
┌───────────────┐            │                    │
│monthly_test.py│            │                    │
└───────┬───────┘            │                    │
        │                    │                    │
        ▼                    │                    │
  ┌──────────┐               │                    │
  │run_test  │               │                    │
  │  .py     │               │                    │
  └────┬─────┘               │                    │
       │                     │                    │
       ▼                     ▼                    ▼
┌─────────────┐    ┌──────────────────┐   ┌─────────────────┐
│   SAVE TO   │    │quarterly_report  │   │biannual_        │
│logs/monthly_│    │      .py         │   │productivity.py  │
│202501.json  │    │                  │   │                 │
└─────────────┘    └────────┬─────────┘   └────────┬────────┘
                            │                      │
                   ┌────────┴────────┐    ┌────────┴────────┐
                   │ Read last 3     │    │ Read last 6     │
                   │ monthly files   │    │ months from     │
                   │                 │    │ productivity    │
                   └────────┬────────┘    │ .json           │
                            │             └────────┬────────┘
                   ┌────────┴────────┐             │
                   │ Check KMPIs:    │    ┌────────┴────────┐
                   │ #1: Entity 85%  │    │ Check KMPI #4:  │
                   │ #2: Crime 85%   │    │ Max 400 art/per │
                   │ #5: Entity 83%  │    │                 │
                   └────────┬────────┘    └────────┬────────┘
                            │                      │
                            ▼                      ▼
                   ┌─────────────────┐    ┌─────────────────┐
                   │ PASS/FAIL       │    │ PASS/FAIL       │
                   │ Save report to  │    │ Save report to  │
                   │ kmpi_reports/   │    │ kmpi_reports/   │
                   └─────────────────┘    └─────────────────┘
```

## Execution Flow

### 1. Monthly Execution (Every 1st at 2 AM)

```python
monthly_test.py
  └─> Calls run_test.py (your existing test)
      └─> Tests all articles
          └─> Calculates entity_similarity and crime_similarity
              └─> Saves to: logs/monthly_YYYYMM.json
```

**Output:** `{"entity_similarity": 0.87, "crime_similarity": 0.89, ...}`

### 2. Quarterly Execution (Jan/Apr/Jul/Oct 1st at 3 AM)

```python
quarterly_report.py
  └─> Loads last 3 monthly files
      └─> For each month, checks:
          • Entity >= 85%? (KMPI #1)
          • Crime >= 85%? (KMPI #2)
          • Entity >= 83%? (KMPI #5)
      └─> Result: PASS if ALL months pass ALL checks
                  FAIL if ANY month fails ANY check
      └─> Saves to: kmpi_reports/kmpi_YYYY_QX.json
```

**Logic:** Strict - one bad month = KMPI failed

### 3. Bi-Annual Execution (Jan/Jul 1st at 4 AM)

```python
biannual_productivity.py
  └─> Loads: production_metrics/productivity.json
      └─> Checks last 6 months:
          • Any month > 400 articles/person? (KMPI #4)
      └─> Result: PASS if all ≤ 400
                  FAIL if any > 400
      └─> Saves to: kmpi_reports/productivity_YYYY_HX.json
```

**Logic:** Strict - one month exceeding limit = KMPI failed

## Installation

```bash
# 1. Copy files to your project
cp config.py test_performance/
cp monthly_test.py test_performance/
cp quarterly_report.py test_performance/
cp biannual_productivity.py test_performance/

# 2. View cron commands
./setup_cron.sh

# 3. Add to crontab
crontab -e
# Paste the commands shown by setup_cron.sh
```

## Required Data Sources

| Script | Reads From | You Provide |
|--------|-----------|-------------|
| monthly_test.py | test_articles/, reference_outputs/ | ✅ Already exists |
| quarterly_report.py | logs/monthly_*.json | ⚙️ Generated automatically |
| biannual_productivity.py | production_metrics/productivity.json | ❗ YOU must create |

## Your Responsibility

Update `production_metrics/productivity.json` monthly:

```json
[
  {"month": "2025-01", "avg_articles_per_person": 210},
  {"month": "2025-02", "avg_articles_per_person": 225}
]
```

**Calculation:**
```
avg_articles_per_person = total_articles_processed / number_of_users
```

## Testing

```bash
# Test each script manually
python3 test_performance/monthly_test.py
python3 test_performance/quarterly_report.py      # Needs 3 monthly runs first
python3 test_performance/biannual_productivity.py # Needs 6 months data
```

## Monitoring

```bash
# View cron logs
tail -f test_performance/logs/monthly.log
tail -f test_performance/logs/quarterly.log
tail -f test_performance/logs/productivity.log

# View reports
cat kmpi_reports/kmpi_2025_Q1.json
cat kmpi_reports/productivity_2025_H1.json
```

## KMPI Summary

| KMPI | Metric | Threshold | Frequency | Script |
|------|--------|-----------|-----------|--------|
| #1 | Entity recall | ≥ 85% | Quarterly | quarterly_report.py |
| #2 | Crime recall | ≥ 85% | Quarterly | quarterly_report.py |
| #3 | SME feedback | 80% approved | Bi-annual | ❌ Manual |
| #4 | Productivity | ≤ 400 art/person | Bi-annual | biannual_productivity.py |
| #5 | Entity recall | ≥ 83% | Quarterly | quarterly_report.py |

## Failure Handling

When a KMPI fails:
1. Script exits with code 1
2. Logged to cron log files
3. Report saved with `"passed": false`
4. **Action required:** Root cause analysis (KMPI #1,#2,#5) or IRR re-assessment (KMPI #4)

---

**Simple rule:** If any month is bad, the whole KMPI fails. No exceptions.
