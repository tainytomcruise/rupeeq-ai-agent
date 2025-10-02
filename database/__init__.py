# In database/__init__.py

# Make the correct models and init function available when 'database' is imported
from .models import init_db, Call, CallTranscript

__all__ = [
    'init_db',
    'Call',
    'CallTranscript'
]
