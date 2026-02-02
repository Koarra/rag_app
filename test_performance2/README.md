# KMPI Monitoring - Complete Setup

## All KMPIs Covered

✅ **KMPI #1**: Entity recall (85%) - Quarterly
✅ **KMPI #2**: Crime recall (85%) - Quarterly  
✅ **KMPI #4**: Article productivity - Bi-annual
✅ **KMPI #5**: Entity recall (83%) - Quarterly
❌ **KMPI #3**: SME feedback - Manual (not automated)

## Files

1. **config.py** - Thresholds: 85%/85%/83%, productivity limits
2. **monthly_test.py** - Runs test monthly, saves result
3. **quarterly_report.py** - Checks KMPI #1, #2, #5 (last 3 months)
4. **biannual_productivity.py** - Checks KMPI #4 (last 6 months)
5. **setup_cron.sh** - Shows cron commands

## Installation

1. Replace `test_performance/config.py` with new version
2. Add the 3 Python scripts to `test_performance/`
3. Run `./setup_cron.sh` to see cron commands
4. Add to crontab: `crontab -e`

## Cron Schedule

```bash
# Monthly test - 1st of each month at 2 AM
0 2 1 * * cd /path/to/project && python3 test_performance/monthly_test.py >> test_performance/logs/monthly.log 2>&1

# Quarterly report - Jan/Apr/Jul/Oct 1st at 3 AM  
0 3 1 1,4,7,10 * cd /path/to/project && python3 test_performance/quarterly_report.py >> test_performance/logs/quarterly.log 2>&1

# Bi-annual productivity - Jan/Jul 1st at 4 AM
0 4 1 1,7 * cd /path/to/project && python3 test_performance/biannual_productivity.py >> test_performance/logs/productivity.log 2>&1
```

## Production Tracking Required (KMPI #4)

For productivity monitoring, create: `production_metrics/productivity.json`

```json
[
  {"month": "2025-01", "avg_articles_per_person": 210},
  {"month": "2025-02", "avg_articles_per_person": 225},
  {"month": "2025-03", "avg_articles_per_person": 240}
]
```

Update this file monthly with production stats:
- Count total articles processed
- Count number of people
- Calculate average per person

## Testing

```bash
# Test monthly
python3 test_performance/monthly_test.py

# After 3 months, test quarterly
python3 test_performance/quarterly_report.py

# After 6 months, test productivity
python3 test_performance/biannual_productivity.py
```

## How It Works

**Monthly**: Runs tests, saves to `logs/monthly_YYYYMM.json`

**Quarterly**: Checks last 3 months:
- KMPI #1 & #2: Both entity and crime >= 85%
- KMPI #5: Entity >= 83%
- FAILS if ANY month below threshold

**Bi-annual**: Checks last 6 months:
- KMPI #4: No month exceeds 400 articles/person
- FAILS if ANY month exceeds limit

## Logs

- `logs/monthly.log` - Monthly cron output
- `logs/quarterly.log` - Quarterly cron output
- `logs/productivity.log` - Productivity cron output
- `logs/monthly_YYYYMM.json` - Monthly test results
- `kmpi_reports/kmpi_YYYY_QX.json` - Quarterly reports
- `kmpi_reports/productivity_YYYY_HX.json` - Productivity reports
