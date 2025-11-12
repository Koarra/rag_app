import logging
from pathlib import Path
import sys

# Setup logger for this module
def setup_logger():
    script_name = Path(sys.argv[0]).stem
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # File handler
    file_handler = logging.FileHandler(f'{script_name}.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger()


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


class DataProcessor:
    """Class that processes data"""
    
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"DataProcessor '{name}' initialized")
    
    def process(self, data):
        self.logger.info(f"Starting processing for {self.name}")
        
        try:
            result = [x * 2 for x in data]
            self.logger.debug(f"Processed {len(result)} items")
            self.logger.info("Processing completed successfully")
            return result
            
        except Exception as e:
            self.logger.exception(f"Processing failed: {e}")
            return None


class AnalysisManager:
    """Main class that orchestrates the analysis"""
    
    def __init__(self, config_name):
        self.config_name = config_name
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"AnalysisManager initialized with config: {config_name}")
        
        # Initialize the other classes
        self.validator = DataValidator("MainValidator")
        self.processor = DataProcessor("MainProcessor")
    
    def run_analysis(self, data):
        self.logger.info("=" * 50)
        self.logger.info("Starting analysis run")
        self.logger.info("=" * 50)
        
        # Step 1: Validate data
        self.logger.info("Step 1: Validating data")
        is_valid = self.validator.validate(data)
        
        if not is_valid:
            self.logger.error("Analysis aborted due to validation failure")
            return None
        
        # Step 2: Process data
        self.logger.info("Step 2: Processing data")
        result = self.processor.process(data)
        
        if result is None:
            self.logger.error("Analysis aborted due to processing failure")
            return None
        
        self.logger.info("Analysis completed successfully")
        self.logger.info(f"Final result: {len(result)} items processed")
        self.logger.info("=" * 50)
        
        return result


# Main execution
if __name__ == "__main__":
    logger.info("Application started")
    
    # Create the main analysis manager
    manager = AnalysisManager("production_config")
    
    # Test with valid data
    test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    result = manager.run_analysis(test_data)
    
    logger.info("\n")
    
    # Test with invalid data (too short)
    invalid_data = [1, 2, 3]
    result = manager.run_analysis(invalid_data)
    
    logger.info("Application finished")
