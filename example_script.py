import argparse
from typing import Dict, List, Optional, Union
"""Enhanced script: example_script.py.

This script has been enhanced with type hints and documentation.
"""

"""Enhanced script: example_script.py.

This script has been enhanced with type hints and documentation.
"""

import os
import sys

def calculate_sum(a: float, b: float) -> float:
    """Calculate the sum of two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b

def process_file(filename: str) -> Optional[str]:
    """Process a file and return its contents.
    
    Args:
        filename: Path to the file to process
        
    Returns:
        File contents or None if file doesn't exist
    """
    if not os.path.exists(filename):
        return None
    with open(filename, 'r') as f:
        return f.read()

class DataProcessor:
    """A simple data processor class."""
    
    def __init__(self, data: str) -> None:
        """Initialize the processor.
        
        Args:
            data: Data to process
        """
        self.data = data
    
    def process(self) -> str:
        """Process the data.
        
        Returns:
            Processed data in uppercase
        """
        return self.data.upper()

def main() -> None:
    """Main function with argparse support."""
    parser = argparse.ArgumentParser(description="Enhanced example script")
    parser.add_argument("filename", help="File to process")
    
    args = parser.parse_args()
    
    content = process_file(args.filename)
    if content:
        processor = DataProcessor(content)
        result = processor.process()
        print(result)
    else:
        print("File not found")

if __name__ == "__main__":
    main()