import logging

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create formatters
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Console handler (outputs to terminal)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Only INFO and above to console
console_handler.setFormatter(formatter)

# File handler (outputs to file)
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)  # All levels to file
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Now log some messages
logger.debug("This only goes to the file")
logger.info("This goes to both console and file")
logger.warning("This also goes to both")
logger.error("Error logged to both destinations")

try:
    1 / 0
except ZeroDivisionError:
    logger.exception("Exception with full traceback")
```

**Console output:**
```
2025-11-12 10:45:30,123 - __main__ - INFO - This goes to both console and file
2025-11-12 10:45:30,124 - __main__ - WARNING - This also goes to both
2025-11-12 10:45:30,125 - __main__ - ERROR - Error logged to both destinations
2025-11-12 10:45:30,126 - __main__ - ERROR - Exception with full traceback
Traceback (most recent call last):
  File "example.py", line 25, in <module>
    1 / 0
ZeroDivisionError: division by zero
```

**app.log file contents:**
```
2025-11-12 10:45:30,122 - __main__ - DEBUG - This only goes to the file
2025-11-12 10:45:30,123 - __main__ - INFO - This goes to both console and file
2025-11-12 10:45:30,124 - __main__ - WARNING - This also goes to both
2025-11-12 10:45:30,125 - __main__ - ERROR - Error logged to both destinations
2025-11-12 10:45:30,126 - __main__ - ERROR - Exception with full traceback
Traceback (most recent call last):
  File "example.py", line 25, in <module>
    1 / 0
ZeroDivisionError: division by zero
