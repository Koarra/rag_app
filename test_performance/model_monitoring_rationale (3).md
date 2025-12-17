# Model Performance Monitoring - Strategy Rationale

## Overview

Our LLM predicts two critical outputs:
1. **Which entities are flagged** for criminal activity (entity detection)
2. **What crimes each entity committed** (crime label assignment)

Both components require rigorous monitoring as failures in either undermine the system's effectiveness.

## Why This Strategy?

### 1. **LLM Output Reliability Requires Continuous Validation**

Large Language Models are probabilistic systems whose outputs can vary with model updates, prompt changes, temperature settings, or API modifications. Unlike deterministic systems, LLMs may produce different results for identical inputs over time. Weekly validation against reference datasets with verified correct outputs ensures the LLM maintains consistent performance for our critical entity-flagging task.

This controlled testing environment detects degradation immediately—whether from model version changes, prompt drift, or infrastructure updates—before impacting production decisions.

### 2. **Business Risk Drives Metric Prioritization**

**Entity Detection Risk:**
Missing a flagged criminal entity (false negative) has severe consequences: regulatory penalties, undetected fraud, reputational damage, and legal liability. Incorrectly flagging an entity (false positive) only requires additional investigation time.

**Crime Label Risk:**
Detecting an entity but misidentifying their crimes creates different but equally serious issues:
- Wrong investigation priorities (investigating fraud when it's money laundering)
- Misallocated compliance resources
- Incomplete regulatory reporting if specific crimes go unreported
- Delayed response to high-severity crimes

This dual risk justifies our strict thresholds: ≥85% recall for both entity detection and crime labels. The model must not miss entities OR their associated crimes.

### 3. **Proactive Detection Prevents Downstream Impact**

Waiting for stakeholder complaints or audit failures to reveal issues is too late. Automated weekly checks catch LLM performance degradation within days, not months. Early detection enables:
- Faster root cause diagnosis with fresh context
- Minimal production impact
- Lower remediation costs
- Maintained stakeholder confidence

### 4. **Quantifiable Standards Enable Action**

Clear thresholds provide objective quality gates. Teams know exactly when to investigate. Visual trends distinguish temporary anomalies from systematic degradation requiring different interventions.

**Monitoring Metrics:**

| Metric | Description | Critical | Warning | Priority |
|--------|-------------|----------|---------|----------|
| **Entity Recall** | % of flagged entities detected | ≥85% | ≥80% | HIGHEST |
| **Missed Entities** | Count of undetected entities | 0 | ≤2 | HIGHEST |
| **Crime Recall** | % of actual crimes detected per entity | ≥85% | ≥80% | HIGH |
| **Jaccard Similarity** | Crime label set overlap (avg per entity) | ≥0.85 | ≥0.75 | HIGH |
| **Critical Crime Miss** | Missing high-severity crimes | 0 | - | CRITICAL |
| **Entity Precision** | % correct flagged entities | Monitor | ≥70% | LOW |

**Weekly Performance Tracking:**

```
Entity Recall Over Time                Crime Recall Per Entity (Avg)
100% |                                 100% |                    
 90% |  •──•──•                         90% |  •──•──•──•        
 85% | ━━━━━━━━━━━━━━━  ← Threshold    85% | ━━━━━━━━━━━━━━━  ← Threshold
 82% |        •──•                      80% | ─ ─ ─ ─ ─ ─ ─ ─  ← Warning
 80% | ─ ─ ─ ─ ─ ─ ─ ─  ← Warning      75% |              •      
 78% |            •  ← Alert!               |_________________________
     |_________________________              W1  W2  W3  W4  W5
      W1  W2  W3  W4  W5
```

**How to Read:**
- **Dots (•)**: Actual weekly performance
- **Solid line (━)**: Critical threshold triggering immediate alerts
- **Dashed line (─)**: Warning threshold for monitoring
- Performance **below** threshold lines triggers alerts

### 5. **Audit Trail for Compliance**

In regulated environments, documented monitoring demonstrates due diligence. Weekly metrics prove that performance is actively monitored, standards are enforced, and deviations are investigated. This historical record supports audits and enables retrospective analysis when issues occur.

### 6. **Scalable Automation**

Manual testing doesn't scale with LLM complexity or testing frequency. Automated monitoring runs weekly without additional effort, maintains consistency, and focuses team investigation only when thresholds breach. New metrics can be added without redesigning the process.

## How It Works

### Weekly Validation Process

**Step 1: Reference Dataset**
- Maintains historical inputs with verified correct outputs
- Each record contains: input data → expected flagged entities → expected crimes per entity
- Dataset updated quarterly to reflect current patterns

**Step 2: Model Execution**
```python
# Run LLM on reference inputs
predictions = llm_model.predict(reference_inputs)

# Extract results
detected_entities = predictions['flagged_entities']
entity_crimes = predictions['crimes_per_entity']
```

**Step 3: Entity-Level Metrics**
```python
# Compare detected vs expected entities
entity_recall = len(detected ∩ expected) / len(expected)
missed_entities = expected - detected
false_positives = detected - expected

# Alert if thresholds breached
if entity_recall < 0.85 or len(missed_entities) > 0:
    send_critical_alert(missed_entities)
```

**Step 4: Crime-Level Metrics**
```python
# For each correctly detected entity
crime_recall_scores = []
jaccard_scores = []
critical_misses = []

for entity in (detected ∩ expected):
    predicted_crimes = entity_crimes[entity]
    expected_crimes = reference_crimes[entity]
    
    # Calculate recall (primary metric)
    recall = len(predicted ∩ expected) / len(expected)
    crime_recall_scores.append(recall)
    
    # Calculate Jaccard similarity (overall quality)
    intersection = len(predicted ∩ expected)
    union = len(predicted ∪ expected)
    jaccard = intersection / union if union > 0 else 0
    jaccard_scores.append(jaccard)
    
    # Check critical crime misses
    critical = {'fraud', 'money_laundering', 'terrorism_financing'}
    missed_critical = (expected ∩ critical) - predicted
    
    if missed_critical:
        critical_misses.append((entity, missed_critical))

# Alert on low metrics or critical misses
avg_crime_recall = mean(crime_recall_scores)
avg_jaccard = mean(jaccard_scores)

if avg_crime_recall < 0.85 or avg_jaccard < 0.85 or critical_misses:
    send_alert(avg_crime_recall, avg_jaccard, critical_misses)
```

**Why Jaccard Similarity?**

Jaccard measures set overlap between predicted and expected crime lists:
```
Jaccard = |Predicted ∩ Expected| / |Predicted ∪ Expected|
```

It's ideal for crime labels because:
- Crime lists are **unordered sets** (order doesn't matter)
- Accounts for both **missing crimes** (false negatives) and **extra crimes** (false positives)
- Single metric (0-1 scale) captures overall prediction quality
- Handles variable-length lists naturally

**Example:**
```
Expected:  {fraud, money_laundering, tax_evasion}
Predicted: {fraud, money_laundering, embezzlement}

Intersection: {fraud, money_laundering} = 2
Union: {fraud, money_laundering, tax_evasion, embezzlement} = 4
Jaccard = 2/4 = 0.50
```

**Metric Combination:**
- **Recall (≥85%)**: Primary - ensures we don't miss actual crimes
- **Jaccard (≥0.85)**: Secondary - ensures overall quality including false positives

**Step 5: Visualization & Reporting**
- Update time-series graphs with new data points
- Log metrics to monitoring dashboard
- Generate weekly summary report
- Archive results for audit trail

### Alert Response

**Critical Alerts** (entity recall < 85%, crime recall < 85%, or critical crime miss):
1. Immediate notification to ML team
2. Investigation within 24 hours
3. Root cause analysis: prompt changes, model updates, data drift
4. Remediation plan documented

**Warning Alerts** (metrics in warning range):
1. Log for weekly review
2. Monitor for trend continuation
3. Investigate if warning persists 2+ weeks

### What Gets Monitored

**Entity Detection:**
- Are we finding all flagged entities?
- Which specific entities did we miss?
- Is there a pattern to misses (entity type, crime category)?

**Crime Labeling:**
- For detected entities, are we identifying all their crimes? (Recall)
- What's the overall quality of crime predictions? (Jaccard)
- Which crime types are most often missed?
- Are we adding extra incorrect crimes? (False positives)
- Are critical crimes (fraud, money laundering) being detected?

**Trends Over Time:**
- Is performance stable or degrading?
- Do certain weeks show anomalies?
- Are there seasonal patterns?

## Conclusion

This two-level monitoring strategy ensures LLM reliability for critical entity-flagging decisions:

1. **Entity Detection Level**: Validates that all flagged entities are identified (recall ≥85%)
2. **Crime Label Level**: Validates crime assignments using dual metrics:
   - **Recall (≥85%)**: Ensures actual crimes aren't missed
   - **Jaccard (≥0.85)**: Measures overall prediction quality including false positives

By validating both levels weekly against reference results, prioritizing recall based on business risk, and providing clear performance visibility through automated graphs and alerts, we maintain consistent detection quality. The combination of recall and Jaccard similarity provides comprehensive crime label validation—recall prevents missing crimes while Jaccard controls overall prediction accuracy.

The automated, risk-based approach protects against LLM variability while supporting compliance, investigation effectiveness, and operational efficiency. Weekly validation catches degradation early—whether from model updates, prompt changes, or data drift—enabling rapid response before issues impact production decisions or regulatory compliance.
