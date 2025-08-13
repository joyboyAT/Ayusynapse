"""
LLM Integration Module
Contains EMR mapping and patient-trial matching functionality
"""

from .emr_mapper import EMRMappingEngine, FHIRMapping, ReportMapping
from .patient_matcher import PatientTrialMatcher, PatientEMR, TrialRequirements, MatchingResult

__all__ = [
    'EMRMappingEngine',
    'FHIRMapping', 
    'ReportMapping',
    'PatientTrialMatcher',
    'PatientEMR',
    'TrialRequirements',
    'MatchingResult'
] 