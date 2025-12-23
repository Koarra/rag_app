Reference:
  Entity: John Smith    → crimes: ["fraud", "money_laundering", "tax_evasion"]
  Entity: ABC Corp      → crimes: ["corruption"]
  Entity: Jane Doe      → crimes: ["fraud"]

Current:
  Entity: John Smith    → crimes: ["fraud", "money_laundering"]
  Entity: ABC Corp      → crimes: ["corruption"]
  (Jane Doe NOT detected)
```

### Entity Similarity Calculation
```
Reference entities: {John Smith, ABC Corp, Jane Doe}
Current entities:   {John Smith, ABC Corp}

Matched: {John Smith, ABC Corp} = 2 entities
Reference total: 3 entities

Entity Similarity = 2 / 3 = 0.667 (66.7%)
```

### Crime Similarity Calculation
```
John Smith:
  Reference: {fraud, money_laundering, tax_evasion} = 3 crimes
  Current:   {fraud, money_laundering} = 2 crimes
  Matched:   {fraud, money_laundering} = 2 crimes

ABC Corp:
  Reference: {corruption} = 1 crime
  Current:   {corruption} = 1 crime
  Matched:   {corruption} = 1 crime

Jane Doe (missing entity):
  Reference: {fraud} = 1 crime
  Current:   NOT DETECTED
  Matched:   {} = 0 crimes

Total matched crimes:   2 + 1 + 0 = 3 crimes
Total reference crimes: 3 + 1 + 1 = 5 crimes

Crime Similarity = 3 / 5 = 0.60 (60%)
```

### Extraction Quality (Combined Metric)
```
Extraction Quality = (Entity Similarity + Crime Similarity) / 2
                   = (0.667 + 0.60) / 2
                   = 0.633 (63.3%)
```

## Critical Differences from Your Current Code

| Aspect | Your Code | Correct Implementation |
|--------|-----------|----------------------|
| **Crime entities** | Only matched entities | ALL reference entities |
| **Crime metric** | Jaccard (matched/union) | Recall (matched/reference) |
| **Crime aggregation** | Average per-entity scores | Sum total crimes |
| **Missing entities** | Ignored | Contribute 0 matched crimes |

## Key Formulas Summary
```
Entity Similarity = Matched Entities / Reference Entities

Crime Similarity = Σ(Matched Crimes) / Σ(Reference Crimes)
                   across all reference entities

Extraction Quality = (Entity Similarity + Crime Similarity) / 2

