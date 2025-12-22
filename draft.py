This document describes the testing pipeline architecture that processes 10 articles provided by the business. The system evaluates entity extraction and labeling accuracy through a multi-stage workflow.
The pipeline consists of four main components that process articles sequentially to evaluate model performance:

Monthly Scheduler - The monthly scheduler initiates the testing process and feeds articles into the test runner component.
Test Runner - The test runner performs two key operations:
• Loads each test article
• Calls the Streamlit LLM endpoint to process the article
Comparison Engine - The comparison engine validates the model output by:
• Loading the expected output (JSON format containing entities flagged and labels)
• Comparing the extracted entities and their labels against the expected results
Threshold Checker - The threshold checker evaluates model performance using three key metrics:
• Entity match rate
• Label accuracy per entity
• Overall F1/precision/recall

Performance Evaluation
The threshold performance component determines the overall system health based on a 90% threshold:
• Above threshold (90%): Indicates good performance
• Below threshold (90%): Indicates bad performance and requires attention
Data Flow Summary
The system processes 10 articles monthly through a sequential pipeline that validates entity extraction accuracy. Each stage builds on the previous one, ultimately determining whether the model meets the 90% performance threshold.
