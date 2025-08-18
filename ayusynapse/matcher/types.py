"""
Shared types and dataclasses for the matcher module
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class MatchResult:
    """Result of a single predicate evaluation"""
    predicate: 'Predicate'  # Forward reference
    matched: bool
    evidence: str
    error: bool = False

@dataclass
class TrialMatchResult:
    """Complete result of trial evaluation"""
    eligible: bool
    score: float
    matched_inclusions: List[MatchResult]
    unmatched_inclusions: List[MatchResult]
    missing_inclusions: List['Predicate']  # Forward reference
    exclusions_triggered: List[MatchResult]
    total_inclusions: int
    matched_count: int
    coverage_percentage: float
    reasons: List[str]
    suggested_data: List[str]  # Human-readable data requests
    coverage_report: Optional[Any] = None  # Enhanced coverage report
