"""
Create sample test data to demonstrate elbow plot.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
import test_performance.config as config

# Create logs directory
config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
log_path = config.LOGS_DIR / "test_results.jsonl"

# Clear existing log
if log_path.exists():
    log_path.unlink()
    print(f"Cleared existing log\n")

# Generate 15 sample test runs
print("Generating sample test data...\n")

for i in range(15):
    timestamp = datetime.now() - timedelta(days=15-i, hours=random.randint(0, 23))

    # Simulate performance: good -> drop -> recover
    if i < 5:
        entity_sim = 0.88 + random.uniform(-0.02, 0.03)
        crime_sim = 0.85 + random.uniform(-0.02, 0.03)
    elif i < 10:
        entity_sim = 0.78 + random.uniform(-0.03, 0.02)  # Performance drop
        crime_sim = 0.77 + random.uniform(-0.03, 0.02)
    else:
        entity_sim = 0.86 + random.uniform(-0.02, 0.04)  # Recovery
        crime_sim = 0.84 + random.uniform(-0.02, 0.04)

    # Clamp values
    entity_sim = max(0.0, min(1.0, entity_sim))
    crime_sim = max(0.0, min(1.0, crime_sim))

    # Create result entry
    result = {
        'timestamp': timestamp.isoformat(),
        'test_config': {
            'entity_threshold': config.ENTITY_SIMILARITY_THRESHOLD,
            'crime_threshold': config.CRIME_SIMILARITY_THRESHOLD,
            'articles_tested': len(config.TEST_ARTICLES)
        },
        'aggregate_metrics': {
            'avg_entity_similarity': entity_sim,
            'avg_crime_similarity': crime_sim,
            'entity_passed': entity_sim >= config.ENTITY_SIMILARITY_THRESHOLD,
            'crime_passed': crime_sim >= config.CRIME_SIMILARITY_THRESHOLD,
            'overall_passed': (entity_sim >= config.ENTITY_SIMILARITY_THRESHOLD and
                             crime_sim >= config.CRIME_SIMILARITY_THRESHOLD)
        },
        'individual_results': []
    }

    # Write to log
    with open(log_path, 'a') as f:
        f.write(json.dumps(result) + '\n')

    status = "✅" if result['aggregate_metrics']['overall_passed'] else "❌"
    print(f"Run {i+1:2d} ({timestamp.strftime('%Y-%m-%d')}): "
          f"Entity={entity_sim:.1%}, Crime={crime_sim:.1%} {status}")

print(f"\n✅ Sample data created: {log_path}")
print(f"\nNow run: python test_performance/plot_elbow.py\n")
