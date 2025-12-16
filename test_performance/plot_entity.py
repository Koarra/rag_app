"""
Entity detection performance plot.
Shows how entity similarity changes over time.
"""

import json
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
import test_performance.config as config

# Load test results
log_path = config.LOGS_DIR / "test_results.jsonl"

if not log_path.exists():
    print(f"No test results found at {log_path}")
    print("Run: python test_performance/create_sample_data.py")
    sys.exit(1)

# Read data
timestamps = []
entity_scores = []

with open(log_path, 'r') as f:
    for line in f:
        if line.strip():
            result = json.loads(line)
            timestamps.append(datetime.fromisoformat(result['timestamp']))
            entity_scores.append(result['aggregate_metrics']['avg_entity_similarity'])

if not timestamps:
    print("No data to plot!")
    sys.exit(1)

# Print summary
print(f"\n{'='*50}")
print("ENTITY DETECTION PERFORMANCE")
print(f"{'='*50}")
print(f"Test runs: {len(timestamps)}")
print(f"Average: {sum(entity_scores)/len(entity_scores):.1%}")
print(f"Min: {min(entity_scores):.1%}")
print(f"Max: {max(entity_scores):.1%}")
print(f"Current threshold: {config.ENTITY_SIMILARITY_THRESHOLD:.0%}")

# Count passes
passes = sum(1 for s in entity_scores if s >= config.ENTITY_SIMILARITY_THRESHOLD)
print(f"Pass rate: {passes}/{len(entity_scores)} ({passes/len(entity_scores):.0%})")
print(f"{'='*50}\n")

# Create plot
fig, ax = plt.subplots(figsize=(12, 6))

# Plot entity similarity
ax.plot(timestamps, entity_scores, 'o-', linewidth=3, markersize=10,
        color='#2E86AB', label='Entity Similarity')

# Threshold line
ax.axhline(y=config.ENTITY_SIMILARITY_THRESHOLD, color='red',
           linestyle='--', linewidth=2, label=f'Threshold ({config.ENTITY_SIMILARITY_THRESHOLD:.0%})')

# Fill areas
ax.fill_between(timestamps, entity_scores, config.ENTITY_SIMILARITY_THRESHOLD,
                where=[s >= config.ENTITY_SIMILARITY_THRESHOLD for s in entity_scores],
                alpha=0.3, color='green', label='Passing')
ax.fill_between(timestamps, entity_scores, config.ENTITY_SIMILARITY_THRESHOLD,
                where=[s < config.ENTITY_SIMILARITY_THRESHOLD for s in entity_scores],
                alpha=0.3, color='red', label='Failing')

# Formatting
ax.set_xlabel('Date', fontsize=14, fontweight='bold')
ax.set_ylabel('Entity Similarity', fontsize=14, fontweight='bold')
ax.set_title('Entity Detection Performance Over Time', fontsize=16, fontweight='bold')
ax.legend(loc='best', fontsize=11)
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_ylim([0, 1.05])
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))

plt.tight_layout()

# Save plot
output_dir = config.DAILY_OUTPUTS_DIR
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / 'entity_performance.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')

print(f"✅ Plot saved to: {output_path}\n")
plt.close()
