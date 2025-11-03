# How to Run Article Detective

There are two ways to run the Article Detective application:

## Option 1: Using streamlit_app.py (Simple)

This is the direct way to run the application:

```bash
streamlit run streamlit_app.py
```

## Option 2: Using app.py (Entry Point)

This uses the wrapper which provides additional functionality:

```bash
streamlit run app.py
```

Or run directly:

```bash
python app.py
```

## Features of app.py

The `app.py` entry point provides:
- **Environment detection**: Automatically detects Domino vs local environment
- **Custom CSS loading**: Loads `style.css` if it exists
- **Error handling**: Better error logging and display
- **Configuration wrapper**: Helper functions for page setup

## Custom Styling

Edit `style.css` to customize the appearance of the application.

## File Structure

```
rag_app/
├── app.py                  # Main entry point (optional)
├── streamlit_app.py        # Core Streamlit application
├── ui_utils.py            # UI helper functions
├── database_utils.py      # Database operations
├── style.css              # Custom CSS styling
├── step1_summarize.py     # Processing steps
├── step2_extract_entities.py
├── step3_describe_entities.py
├── step4_group_entities.py
├── step5_analyze_risks.py
└── step6_extract_relationships.py
```

## Environment Variables (Domino Deployment)

When deploying on Domino Data Lab, these variables are automatically set:
- `DOMINO_DATASETS_DIR`: Base directory for datasets
- `DOMINO_PROJECT_NAME`: Project name

## Local Development

For local development, files are stored in:
```
./articledetective_assets/
```
