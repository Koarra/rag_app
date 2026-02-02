#!/bin/bash
# Simple cron setup for KMPI monitoring

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Setting up KMPI cron jobs..."
echo "Project: $PROJECT_DIR"
echo ""
echo "Add these to your crontab (crontab -e):"
echo ""
echo "# Monthly test - 1st of each month at 2 AM"
echo "0 2 1 * * cd $PROJECT_DIR && python3 test_performance/monthly_test.py >> test_performance/logs/monthly.log 2>&1"
echo ""
echo "# Quarterly report - Jan/Apr/Jul/Oct 1st at 3 AM"
echo "0 3 1 1,4,7,10 * cd $PROJECT_DIR && python3 test_performance/quarterly_report.py >> test_performance/logs/quarterly.log 2>&1"
echo ""
echo "# Bi-annual productivity - Jan/Jul 1st at 4 AM"
echo "0 4 1 1,7 * cd $PROJECT_DIR && python3 test_performance/biannual_productivity.py >> test_performance/logs/productivity.log 2>&1"
echo ""
