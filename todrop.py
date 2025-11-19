┌─────────────────┐
│  Daily Scheduler │ (e.g., cron, GitHub Actions)
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Test Runner                    │
│  - Load test article            │
│  - Call Streamlit LLM endpoint  │
│  - Get actual output (JSON)     │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Comparison Engine              │
│  - Load expected output         │
│  - Compare entities & labels    │
│  - Calculate metrics            │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Threshold Checker              │
│  - Entity match rate            │
│  - Label accuracy per entity    │
│  - Overall F1/precision/recall  │
└────────┬────────────────────────┘
         │
         ▼
    ┌───┴───┐
    │ Alert? │
    └───┬───┘
        │
   YES  │  NO
    ┌───┴───┐
    ▼       ▼
  Alert   Log only
