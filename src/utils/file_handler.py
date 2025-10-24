"""
File handling utilities for reading/writing documents and results
"""
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class FileHandler:

    @staticmethod
    def save_text(content: str, filepath: Path) -> None:
        """Save text content to file"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved text to: {filepath}")

    @staticmethod
    def save_json(data: Dict[str, Any], filepath: Path, indent: int = 2) -> None:
        """Save dictionary as JSON file"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        print(f"Saved JSON to: {filepath}")

    @staticmethod
    def load_text(filepath: Path) -> str:
        """Load text content from file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def load_json(filepath: Path) -> Dict[str, Any]:
        """Load JSON file as dictionary"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def get_output_filename(input_filename: str, suffix: str, extension: str = 'json') -> str:
        """
        Generate output filename from input filename

        Args:
            input_filename: Original filename (with or without extension)
            suffix: Suffix to add (e.g., '_summary', '_entities')
            extension: Output file extension (default: 'json')

        Returns:
            Output filename
        """
        stem = Path(input_filename).stem
        return f"{stem}{suffix}.{extension}"

    @staticmethod
    def create_processing_log(
        document_name: str,
        stage: str,
        status: str,
        details: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a processing log entry"""
        log_entry = {
            "document": document_name,
            "stage": stage,
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }
        if details:
            log_entry["details"] = details
        return log_entry
