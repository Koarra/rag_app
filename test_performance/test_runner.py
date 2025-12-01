from datetime import datetime
from pathlib import Path
import json
from compare_outputs import compare_outputs
from analyzer import run_analyzer  # Your existing script
from alerts import send_alert
import config

def run_daily_test():
    timestamp = datetime.now().isoformat()
    all_results = []
    
    print(f"Starting daily test run: {timestamp}")
    
    for article_name in config.TEST_ARTICLES:
        print(f"Processing {article_name}...")
        
        # Run your LLM analyzer
        current_output = run_analyzer(f"data/test_articles/{article_name}.txt")
        
        # Load reference
        with open(f"data/reference_outputs/{article_name}.json") as f:
            reference_output = json.load(f)
        
        # Save current output with timestamp
        output_path = f"data/daily_outputs/{article_name}_{timestamp}.json"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(current_output, f, indent=2)
        
        # Compare
        comparison = compare_outputs(reference_output, current_output)
        
        all_results.append({
            'article': article_name,
            'timestamp': timestamp,
            **comparison
        })
        
        print(f"  Entity similarity: {comparison['entity_similarity']:.2%}")
        print(f"  Crime similarity: {comparison['crime_similarity']:.2%}")
    
    # Aggregate metrics
    avg_entity = sum(r['entity_similarity'] for r in all_results) / len(all_results)
    avg_crime = sum(r['crime_similarity'] for r in all_results) / len(all_results)
    
    summary = {
        'timestamp': timestamp,
        'avg_entity_similarity': avg_entity,
        'avg_crime_similarity': avg_crime,
        'threshold': config.SIMILARITY_THRESHOLD,
        'passed': avg_entity >= config.SIMILARITY_THRESHOLD and avg_crime >= config.SIMILARITY_THRESHOLD,
        'individual_results': all_results
    }
    
    # Log results
    log_path = Path("logs/test_results.jsonl")
    log_path.parent.mkdir(exist_ok=True)
    with open(log_path, 'a') as f:
        f.write(json.dumps(summary) + '\n')
    
    # Alert if below threshold
    if not summary['passed']:
        send_alert(summary)
        print(f"⚠️  ALERT: Similarity below {config.SIMILARITY_THRESHOLD:.0%} threshold!")
    else:
        print(f"✓ Test passed")
    
    return summary

if __name__ == "__main__":
    run_daily_test()