"""
Simple elbow plot for performance test results.
Shows how entity and crime similarity metrics change over time.
"""

import json
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
import test_performance.config as config


# Load test results from log file
log_path = config.LOGS_DIR / "test_results.jsonl"

if not log_path.exists():
    print(f"No test results found at {log_path}")
    print("Run tests first: python test_performance/run_test.py")
    sys.exit(1)

# Read data
timestamps = []
entity_scores = []
crime_scores = []

with open(log_path, 'r') as f:
    for line in f:
        if line.strip():
            result = json.loads(line)
            timestamps.append(datetime.fromisoformat(result['timestamp']))
            entity_scores.append(result['aggregate_metrics']['avg_entity_similarity'])
            crime_scores.append(result['aggregate_metrics']['avg_crime_similarity'])

if not timestamps:
    print("No data to plot!")
    sys.exit(1)

# Print summary
print(f"\nTest runs: {len(timestamps)}")
print(f"Entity similarity: {sum(entity_scores)/len(entity_scores):.1%} avg")
print(f"Crime similarity: {sum(crime_scores)/len(crime_scores):.1%} avg")

# Create plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
fig.suptitle('Performance Over Time', fontsize=16, fontweight='bold')

# Plot 1: Entity Similarity
ax1.plot(timestamps, entity_scores, 'o-', linewidth=2, markersize=8, color='#2E86AB')
ax1.axhline(y=config.ENTITY_SIMILARITY_THRESHOLD, color='red', linestyle='--', linewidth=2)
ax1.set_ylabel('Entity Similarity', fontsize=12, fontweight='bold')
ax1.set_title('Entity Detection Performance')
ax1.grid(True, alpha=0.3)
ax1.set_ylim([0, 1.05])
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))

# Plot 2: Crime Similarity
ax2.plot(timestamps, crime_scores, 's-', linewidth=2, markersize=8, color='#A23B72')
ax2.axhline(y=config.CRIME_SIMILARITY_THRESHOLD, color='red', linestyle='--', linewidth=2)
ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
ax2.set_ylabel('Crime Similarity', fontsize=12, fontweight='bold')
ax2.set_title('Crime Classification Performance')
ax2.grid(True, alpha=0.3)
ax2.set_ylim([0, 1.05])
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))

plt.tight_layout()

# Save plot
output_dir = config.DAILY_OUTPUTS_DIR
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / 'performance_plot.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')

print(f"\n✅ Plot saved to: {output_path}\n")
plt.close()
