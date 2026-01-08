"""
Logging utility for driver-mgt
"""

import logging
from pathlib import Path
import sys

def setup_logger(level='INFO'):
    """Setup application logger"""
    
    # Create logger
    logger = logging.getLogger('driver-mgt')
    logger.setLevel(getattr(logging, level))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler
    logger.addHandler(console_handler)
    
    # File handler (if logs directory exists)
    logs_dir = Path.home() / '.config' / 'driver-mgt' / 'logs'
    if logs_dir.exists():
        file_handler = logging.FileHandler(logs_dir / 'driver-mgt.log')
        file_handler.setLevel(getattr(logging, level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
