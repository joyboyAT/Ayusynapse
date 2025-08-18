"""
API Module - RESTful Endpoints

Provides FastAPI endpoints for the patient-trial matching service.
"""

from .match_api import *

__all__ = [
    "match_api",
]
