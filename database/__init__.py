# Database package for RupeeQ AI Calling Agent

from .models import DatabaseManager, Call, Transcript, PerformanceMetrics

__all__ = [
    'DatabaseManager',
    'Call',
    'Transcript', 
    'PerformanceMetrics'
]

# Version info
__version__ = '0.1.0'

# Package metadata
__author__ = 'RupeeQ Team'
__description__ = 'Database models and operations for the AI calling agent'
