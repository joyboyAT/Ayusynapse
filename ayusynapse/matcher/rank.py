#!/usr/bin/env python3
"""
Ranking & Thresholding Module for Patient-Trial Matching
Provides intelligent trial ranking with tie-breaking and special handling
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

try:
    from .engine import TrialMatchResult
    from .predicates import Predicate
except ImportError:
    from engine import TrialMatchResult
    from predicates import Predicate

logger = logging.getLogger(__name__)

@dataclass
class TrialRankingInfo:
    """Additional information for trial ranking"""
    trial_id: str
    start_date: Optional[datetime] = None
    recruiting_status: str = "Unknown"
    must_have_biomarkers: List[str] = None
    has_all_must_have: bool = False
    zero_exclusions: bool = False
    priority_boost: float = 0.0

@dataclass
class RankedTrial:
    """Ranked trial result with metadata"""
    trial_id: str
    result: TrialMatchResult
    rank: int
    final_score: float
    ranking_info: TrialRankingInfo
    tie_breaker_reason: Optional[str] = None

class TrialRanker:
    """Ranks trials based on score, thresholds, and tie-breaking rules"""
    
    def __init__(self, min_score: float = 60.0, priority_threshold: float = 50.0):
        """
        Initialize the trial ranker
        
        Args:
            min_score: Minimum score to include in results (default: 60.0)
            priority_threshold: Score threshold for priority trials (default: 50.0)
        """
        self.min_score = min_score
        self.priority_threshold = priority_threshold
    
    def rank_trials(self, results: List[Tuple[str, TrialMatchResult]], 
                   ranking_info: Optional[Dict[str, TrialRankingInfo]] = None) -> List[RankedTrial]:
        """
        Rank trials based on score and tie-breaking rules
        
        Args:
            results: List of (trial_id, TrialMatchResult) tuples
            ranking_info: Optional dict of trial_id -> TrialRankingInfo for tie-breaking
            
        Returns:
            List of RankedTrial objects sorted by final score
        """
        if not results:
            return []
        
        # Convert to RankedTrial objects
        ranked_trials = []
        for trial_id, result in results:
            # Get ranking info or create default
            info = ranking_info.get(trial_id) if ranking_info else TrialRankingInfo(trial_id=trial_id)
            
            # Calculate final score with priority boost
            final_score = self._calculate_final_score(result, info)
            
            ranked_trial = RankedTrial(
                trial_id=trial_id,
                result=result,
                rank=0,  # Will be set after sorting
                final_score=final_score,
                ranking_info=info
            )
            ranked_trials.append(ranked_trial)
        
        # Apply minimum score threshold
        filtered_trials = [rt for rt in ranked_trials if rt.final_score >= self.min_score]
        
        # Apply priority rules for special cases
        priority_trials = self._apply_priority_rules(filtered_trials)
        
        # Sort by final score (descending)
        sorted_trials = sorted(priority_trials, key=lambda rt: rt.final_score, reverse=True)
        
        # Apply tie-breaking
        sorted_trials = self._apply_tie_breakers(sorted_trials)
        
        # Set ranks
        for i, trial in enumerate(sorted_trials, 1):
            trial.rank = i
        
        return sorted_trials
    
    def _calculate_final_score(self, result: TrialMatchResult, info: TrialRankingInfo) -> float:
        """
        Calculate final score with priority boost
        
        Args:
            result: Trial match result
            info: Trial ranking information
            
        Returns:
            Final score with priority adjustments
        """
        base_score = result.score
        
        # Check for priority conditions
        priority_boost = 0.0
        
        # Priority 1: Zero exclusions and has all must-have biomarkers
        if info.zero_exclusions and info.has_all_must_have:
            priority_boost = 20.0  # Significant boost
            info.priority_boost = priority_boost
            logger.info(f"Priority boost for {info.trial_id}: zero exclusions + all must-have biomarkers")
        
        # Priority 2: Zero exclusions only
        elif info.zero_exclusions:
            priority_boost = 10.0  # Moderate boost
            info.priority_boost = priority_boost
            logger.info(f"Priority boost for {info.trial_id}: zero exclusions")
        
        # Priority 3: Has all must-have biomarkers
        elif info.has_all_must_have:
            priority_boost = 5.0  # Small boost
            info.priority_boost = priority_boost
            logger.info(f"Priority boost for {info.trial_id}: all must-have biomarkers")
        
        final_score = min(100.0, base_score + priority_boost)
        
        return final_score
    
    def _apply_priority_rules(self, trials: List[RankedTrial]) -> List[RankedTrial]:
        """
        Apply special priority rules for trials that should be included even with lower scores
        
        Args:
            trials: List of ranked trials
            
        Returns:
            List with priority trials included
        """
        priority_trials = []
        
        for trial in trials:
            # Always include trials that meet minimum threshold
            if trial.final_score >= self.min_score:
                priority_trials.append(trial)
                continue
            
            # Special case: Include trials with zero exclusions and all must-have biomarkers
            # even if score is slightly below threshold
            if (trial.ranking_info.zero_exclusions and 
                trial.ranking_info.has_all_must_have and 
                trial.final_score >= self.priority_threshold):
                priority_trials.append(trial)
                logger.info(f"Including priority trial {trial.trial_id} with score {trial.final_score:.1f}")
                continue
        
        return priority_trials
    
    def _apply_tie_breakers(self, trials: List[RankedTrial]) -> List[RankedTrial]:
        """
        Apply tie-breaking rules when trials have the same score
        
        Args:
            trials: List of ranked trials sorted by score
            
        Returns:
            List with tie-breaking applied
        """
        if len(trials) <= 1:
            return trials
        
        # Group trials by score
        score_groups = {}
        for trial in trials:
            score = trial.final_score
            if score not in score_groups:
                score_groups[score] = []
            score_groups[score].append(trial)
        
        # Apply tie-breaking within each score group
        final_trials = []
        for score in sorted(score_groups.keys(), reverse=True):
            group = score_groups[score]
            
            if len(group) == 1:
                final_trials.append(group[0])
            else:
                # Apply tie-breaking rules
                sorted_group = self._break_ties(group)
                final_trials.extend(sorted_group)
        
        return final_trials
    
    def _break_ties(self, trials: List[RankedTrial]) -> List[RankedTrial]:
        """
        Break ties between trials with the same score
        
        Args:
            trials: List of trials with the same score
            
        Returns:
            List sorted by tie-breaking criteria
        """
        if len(trials) <= 1:
            return trials
        
        # Sort by multiple criteria
        sorted_trials = sorted(trials, key=lambda t: (
            # 1. Recruiting status (recruiting first)
            self._recruiting_status_priority(t.ranking_info.recruiting_status),
            # 2. Start date (newer first)
            self._date_priority(t.ranking_info.start_date),
            # 3. Priority boost (higher first)
            -t.ranking_info.priority_boost,
            # 4. Trial ID (alphabetical for consistency)
            t.trial_id
        ))
        
        # Add tie-breaker reasons
        for i, trial in enumerate(sorted_trials):
            if i > 0:
                prev_trial = sorted_trials[i-1]
                if trial.final_score == prev_trial.final_score:
                    trial.tie_breaker_reason = self._get_tie_breaker_reason(trial, prev_trial)
        
        return sorted_trials
    
    def _recruiting_status_priority(self, status: str) -> int:
        """Convert recruiting status to priority number (lower = higher priority)"""
        status_priorities = {
            "Recruiting": 1,
            "Active, not recruiting": 2,
            "Not yet recruiting": 3,
            "Completed": 4,
            "Terminated": 5,
            "Suspended": 6,
            "Withdrawn": 7,
            "Unknown": 8
        }
        return status_priorities.get(status, 8)
    
    def _date_priority(self, start_date: Optional[datetime]) -> int:
        """Convert start date to priority number (lower = higher priority)"""
        if start_date is None:
            return 999999  # Very low priority for unknown dates
        
        # Newer dates get lower numbers (higher priority)
        # Use days since epoch for comparison
        return int(start_date.timestamp() / 86400)
    
    def _get_tie_breaker_reason(self, trial: RankedTrial, prev_trial: RankedTrial) -> str:
        """Generate human-readable tie-breaker reason"""
        reasons = []
        
        # Check recruiting status
        if (self._recruiting_status_priority(trial.ranking_info.recruiting_status) < 
            self._recruiting_status_priority(prev_trial.ranking_info.recruiting_status)):
            reasons.append(f"more favorable recruiting status ({trial.ranking_info.recruiting_status})")
        
        # Check start date
        if (trial.ranking_info.start_date and prev_trial.ranking_info.start_date and
            trial.ranking_info.start_date > prev_trial.ranking_info.start_date):
            reasons.append(f"newer trial (started {trial.ranking_info.start_date.strftime('%Y-%m-%d')})")
        
        # Check priority boost
        if trial.ranking_info.priority_boost > prev_trial.ranking_info.priority_boost:
            reasons.append("higher priority criteria match")
        
        if reasons:
            return f"Tie broken by: {', '.join(reasons)}"
        else:
            return "Tie broken by trial ID (alphabetical)"
    
    def get_ranking_summary(self, ranked_trials: List[RankedTrial]) -> Dict[str, Any]:
        """
        Generate a summary of the ranking results
        
        Args:
            ranked_trials: List of ranked trials
            
        Returns:
            Summary dictionary
        """
        if not ranked_trials:
            return {"total_trials": 0, "eligible_trials": 0}
        
        total_trials = len(ranked_trials)
        eligible_trials = len([rt for rt in ranked_trials if rt.result.eligible])
        
        # Score distribution
        score_ranges = {
            "excellent": len([rt for rt in ranked_trials if rt.final_score >= 90]),
            "good": len([rt for rt in ranked_trials if 80 <= rt.final_score < 90]),
            "fair": len([rt for rt in ranked_trials if 70 <= rt.final_score < 80]),
            "marginal": len([rt for rt in ranked_trials if 60 <= rt.final_score < 70])
        }
        
        # Priority trials
        priority_trials = len([rt for rt in ranked_trials if rt.ranking_info.priority_boost > 0])
        
        # Recruiting status distribution
        recruiting_counts = {}
        for rt in ranked_trials:
            status = rt.ranking_info.recruiting_status
            recruiting_counts[status] = recruiting_counts.get(status, 0) + 1
        
        return {
            "total_trials": total_trials,
            "eligible_trials": eligible_trials,
            "score_distribution": score_ranges,
            "priority_trials": priority_trials,
            "recruiting_status": recruiting_counts,
            "min_score_threshold": self.min_score,
            "priority_threshold": self.priority_threshold
        }

def create_sample_ranking_info() -> Dict[str, TrialRankingInfo]:
    """Create sample ranking information for testing"""
    from datetime import datetime, timedelta
    
    return {
        "NCT07062263": TrialRankingInfo(
            trial_id="NCT07062263",
            start_date=datetime(2023, 6, 15),
            recruiting_status="Recruiting",
            must_have_biomarkers=["HER2"],
            has_all_must_have=True,
            zero_exclusions=True
        ),
        "NCT12345678": TrialRankingInfo(
            trial_id="NCT12345678",
            start_date=datetime(2023, 3, 10),
            recruiting_status="Active, not recruiting",
            must_have_biomarkers=["HER2", "ECOG"],
            has_all_must_have=False,
            zero_exclusions=True
        ),
        "NCT87654321": TrialRankingInfo(
            trial_id="NCT87654321",
            start_date=datetime(2023, 8, 20),
            recruiting_status="Recruiting",
            must_have_biomarkers=["HER2"],
            has_all_must_have=True,
            zero_exclusions=False
        ),
        "NCT99999999": TrialRankingInfo(
            trial_id="NCT99999999",
            start_date=datetime(2022, 12, 1),
            recruiting_status="Not yet recruiting",
            must_have_biomarkers=["HER2", "ECOG", "Hemoglobin"],
            has_all_must_have=False,
            zero_exclusions=False
        ),
        "NCT11111111": TrialRankingInfo(
            trial_id="NCT11111111",
            start_date=datetime(2023, 9, 5),
            recruiting_status="Recruiting",
            must_have_biomarkers=["HER2"],
            has_all_must_have=True,
            zero_exclusions=True
        )
    }

def test_ranking():
    """Test the ranking system with sample data"""
    print("🧪 Testing Trial Ranking System")
    print("=" * 50)
    
    try:
        from matcher.engine import MatchingEngine
        from matcher.predicates import Predicate
    except ImportError:
        from engine import MatchingEngine
        from predicates import Predicate
    
    # Create sample trial results
    engine = MatchingEngine()
    
    # Sample patient
    patient = {
        "age": 52,
        "gender": "female",
        "conditions": [
            {
                "text": "Biliary tract cancer",
                "codes": [{"code": "363418001"}],
                "status": "active"
            }
        ],
        "observations": [
            {
                "text": "HER2",
                "value": "positive",
                "status": "final"
            },
            {
                "text": "ECOG",
                "value": 1,
                "status": "final"
            },
            {
                "text": "Hemoglobin",
                "value": 13.2,
                "unit": "g/dL",
                "status": "final"
            }
        ],
        "medications": [],
        "lab_results": [],
        "vital_signs": {}
    }
    
    # Sample trials with different characteristics
    trials_data = [
        ("NCT07062263", [
            Predicate(type="Patient", field="age", op=">=", value=18, weight=2, inclusion=True),
            Predicate(type="Condition", code="363418001", op="present", weight=5, inclusion=True),
            Predicate(type="Observation", field="HER2", op="==", value="positive", weight=3, inclusion=True),
            Predicate(type="Observation", field="ECOG", op="<=", value=2, weight=2, inclusion=True),
        ]),
        ("NCT12345678", [
            Predicate(type="Patient", field="age", op=">=", value=18, weight=2, inclusion=True),
            Predicate(type="Condition", code="363418001", op="present", weight=5, inclusion=True),
            Predicate(type="Observation", field="HER2", op="==", value="positive", weight=3, inclusion=True),
            Predicate(type="Observation", field="ECOG", op="<=", value=2, weight=2, inclusion=True),
            Predicate(type="Observation", field="Hemoglobin", op=">=", value=10, unit="g/dL", weight=1, inclusion=True),
        ]),
        ("NCT87654321", [
            Predicate(type="Patient", field="age", op=">=", value=18, weight=2, inclusion=True),
            Predicate(type="Condition", code="363418001", op="present", weight=5, inclusion=True),
            Predicate(type="Observation", field="HER2", op="==", value="positive", weight=3, inclusion=True),
            # Missing ECOG - will have lower score
        ]),
        ("NCT99999999", [
            Predicate(type="Patient", field="age", op=">=", value=18, weight=2, inclusion=True),
            Predicate(type="Condition", code="363418001", op="present", weight=5, inclusion=True),
            Predicate(type="Observation", field="HER2", op="==", value="positive", weight=3, inclusion=True),
            Predicate(type="Observation", field="ECOG", op="<=", value=2, weight=2, inclusion=True),
            Predicate(type="Observation", field="Hemoglobin", op=">=", value=15, unit="g/dL", weight=1, inclusion=True),  # Will fail
        ]),
        ("NCT11111111", [
            Predicate(type="Patient", field="age", op=">=", value=18, weight=2, inclusion=True),
            Predicate(type="Condition", code="363418001", op="present", weight=5, inclusion=True),
            Predicate(type="Observation", field="HER2", op="==", value="positive", weight=3, inclusion=True),
            Predicate(type="Observation", field="ECOG", op="<=", value=2, weight=2, inclusion=True),
            Predicate(type="Observation", field="Hemoglobin", op=">=", value=10, unit="g/dL", weight=1, inclusion=True),
        ])
    ]
    
    # Evaluate all trials
    results = []
    for trial_id, predicates in trials_data:
        result = engine.evaluate_trial(patient, predicates)
        results.append((trial_id, result))
    
    # Create ranking info
    ranking_info = create_sample_ranking_info()
    
    # Rank trials
    ranker = TrialRanker(min_score=60.0, priority_threshold=50.0)
    ranked_trials = ranker.rank_trials(results, ranking_info)
    
    # Display results
    print("📊 Ranked Trial Results")
    print("-" * 30)
    
    for ranked_trial in ranked_trials:
        print(f"\n#{ranked_trial.rank} - {ranked_trial.trial_id}")
        print(f"   Base Score: {ranked_trial.result.score:.1f}/100")
        print(f"   Final Score: {ranked_trial.final_score:.1f}/100")
        print(f"   Priority Boost: +{ranked_trial.ranking_info.priority_boost:.1f}")
        print(f"   Status: {ranked_trial.ranking_info.recruiting_status}")
        print(f"   Start Date: {ranked_trial.ranking_info.start_date.strftime('%Y-%m-%d') if ranked_trial.ranking_info.start_date else 'Unknown'}")
        print(f"   Zero Exclusions: {ranked_trial.ranking_info.zero_exclusions}")
        print(f"   All Must-Have: {ranked_trial.ranking_info.has_all_must_have}")
        print(f"   Eligible: {ranked_trial.result.eligible}")
        
        if ranked_trial.tie_breaker_reason:
            print(f"   Tie Breaker: {ranked_trial.tie_breaker_reason}")
    
    # Show summary
    summary = ranker.get_ranking_summary(ranked_trials)
    print(f"\n📋 Ranking Summary")
    print("-" * 20)
    print(f"Total Trials: {summary['total_trials']}")
    print(f"Eligible Trials: {summary['eligible_trials']}")
    print(f"Priority Trials: {summary['priority_trials']}")
    print(f"Score Distribution: {summary['score_distribution']}")
    print(f"Recruiting Status: {summary['recruiting_status']}")
    
    print(f"\n✅ Ranking test completed!")

if __name__ == "__main__":
    test_ranking()
