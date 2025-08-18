"""
Ayusynapse - AI-Powered Clinical Trial Matching Platform

A comprehensive platform for intelligent patient-clinical trial matching
using FHIR-compliant data structures and advanced NLP techniques.
"""

__version__ = "1.0.0"
__author__ = "Ayusynapse Team"
__email__ = "contact@ayusynapse.com"

from .matcher import *
from .fhir import *
from .api import *

__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__email__",
]
