import logging
from pathlib import Path
import sys

def setup_logger(module_name):
    """Setup logger for any module"""
    # Get the main script name for the log file
    script_name = Path(sys.argv[0]).stem
    
    logger = logging.getLogger(module_name)
    
    # Avoid adding handlers multiple times
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # File handler - all modules log to the same file (main script name)
    file_handler = logging.FileHandler(f'{script_name}.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger




import logging
from logger_config import setup_logger

# Setup logger for this module
logger = setup_logger(__name__)


class DataValidator:
    """Class that validates data"""
    
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"DataValidator '{name}' initialized")
    
    def validate(self, data):
        self.logger.info(f"Starting validation for {self.name}")
        
        try:
            if not data:
                self.logger.warning("Empty data received")
                return False
            
            if len(data) < 5:
                self.logger.error(f"Data too short: {len(data)} items")
                return False
            
            self.logger.info(f"Validation passed: {len(data)} items validated")
            return True
            
        except Exception as e:
            self.logger.exception(f"Validation failed with exception: {e}")
            return False
