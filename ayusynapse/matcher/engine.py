#!/usr/bin/env python3
"""
Matching Engine for Patient-Trial Matching
Implements inclusion/exclusion semantics and scoring logic
"""

from typing import Dict, List, Any, Optional, Tuple
import logging

from .predicates import Predicate, PredicateEvaluator
from .features import FeatureExtractor
from .coverage_report import CoverageReportGenerator
from .types import MatchResult, TrialMatchResult

logger = logging.getLogger(__name__)



class MatchingEngine:
    """Engine for evaluating patient-trial matches"""
    
    def __init__(self, feature_extractor: Optional[FeatureExtractor] = None):
        """Initialize matching engine with optional feature extractor"""
        self.feature_extractor = feature_extractor or FeatureExtractor()
        self.predicate_evaluator = PredicateEvaluator(self.feature_extractor)
        self.coverage_generator = CoverageReportGenerator()
    
    def evaluate_trial(self, patient_features: Dict[str, Any], trial_predicates: List[Predicate]) -> TrialMatchResult:
        """
        Evaluate a patient against trial predicates
        
        Args:
            patient_features: Extracted patient features
            trial_predicates: List of trial predicates (inclusions and exclusions)
            
        Returns:
            TrialMatchResult with eligibility status and detailed breakdown
        """
        # Separate inclusions and exclusions
        inclusion_predicates = [p for p in trial_predicates if p.inclusion]
        exclusion_predicates = [p for p in trial_predicates if not p.inclusion]
        
        # Step 1: Check exclusions first
        exclusion_results = []
        for predicate in exclusion_predicates:
            result = self.predicate_evaluator.evaluate_predicate(patient_features, predicate)
            match_result = MatchResult(
                predicate=predicate,
                matched=result['match'],
                evidence=result['evidence'],
                error=result.get('error', False)
            )
            exclusion_results.append(match_result)
        
        # Check if any exclusions are triggered
        # For exclusions: if predicate matches (patient has the condition), they are excluded
        triggered_exclusions = [r for r in exclusion_results if r.matched]
        
        if triggered_exclusions:
            # Patient is ineligible due to exclusions
            reasons = [f"Excluded: {r.predicate.reason or r.evidence}" for r in triggered_exclusions]
            return TrialMatchResult(
                eligible=False,
                score=0.0,
                matched_inclusions=[],
                unmatched_inclusions=[],
                missing_inclusions=[],
                exclusions_triggered=triggered_exclusions,
                total_inclusions=len(inclusion_predicates),
                matched_count=0,
                coverage_percentage=0.0,
                reasons=reasons,
                suggested_data=[]  # No data requests needed if excluded
            )
        
        # Step 2: Evaluate inclusions
        inclusion_results = []
        for predicate in inclusion_predicates:
            result = self.predicate_evaluator.evaluate_predicate(patient_features, predicate)
            match_result = MatchResult(
                predicate=predicate,
                matched=result['match'],
                evidence=result['evidence'],
                error=result.get('error', False)
            )
            inclusion_results.append(match_result)
        
        # Categorize inclusion results
        matched_inclusions = [r for r in inclusion_results if r.matched]
        unmatched_inclusions = [r for r in inclusion_results if not r.matched and not r.error]
        missing_inclusions = [r.predicate for r in inclusion_results if not r.matched and r.error]
        
        # For observations that are not found, treat them as missing data
        # This is a more nuanced approach - observations that are "not present" 
        # when we're looking for them should be considered missing, not failed
        for r in inclusion_results:
            if (not r.matched and not r.error and 
                r.predicate.type == "Observation" and 
                "is not present" in r.evidence):
                # Move from unmatched to missing
                if r in unmatched_inclusions:
                    unmatched_inclusions.remove(r)
                missing_inclusions.append(r.predicate)
        
        # Calculate score and coverage
        total_inclusions = len(inclusion_predicates)
        matched_count = len(matched_inclusions)
        coverage_percentage = (matched_count / total_inclusions * 100) if total_inclusions > 0 else 0.0
        
        # Calculate score using new formula
        score = self.compute_score(matched_inclusions, unmatched_inclusions, missing_inclusions, total_inclusions)
        
        # Determine eligibility (can be customized based on requirements)
        eligible = self._determine_eligibility(matched_inclusions, unmatched_inclusions, total_inclusions, score)
        
        # Generate reasons
        reasons = self._generate_reasons(matched_inclusions, unmatched_inclusions, missing_inclusions)
        
        # Generate data requests for missing information
        suggested_data = self._generate_data_requests(missing_inclusions)
        
        # Generate enhanced coverage report
        coverage_report = self.coverage_generator.generate_coverage_report(
            patient_features, 
            TrialMatchResult(
                eligible=eligible,
                score=score,
                matched_inclusions=matched_inclusions,
                unmatched_inclusions=unmatched_inclusions,
                missing_inclusions=missing_inclusions,
                exclusions_triggered=[],
                total_inclusions=total_inclusions,
                matched_count=matched_count,
                coverage_percentage=coverage_percentage,
                reasons=reasons,
                suggested_data=suggested_data
            )
        )
        
        return TrialMatchResult(
            eligible=eligible,
            score=score,
            matched_inclusions=matched_inclusions,
            unmatched_inclusions=unmatched_inclusions,
            missing_inclusions=missing_inclusions,
            exclusions_triggered=[],
            total_inclusions=total_inclusions,
            matched_count=matched_count,
            coverage_percentage=coverage_percentage,
            reasons=reasons,
            suggested_data=suggested_data,
            coverage_report=coverage_report
        )
    
    def compute_score(self, matched_inclusions: List[MatchResult], 
                     unmatched_inclusions: List[MatchResult], 
                     missing_inclusions: List[Predicate], 
                     total_inclusions: int, 
                     alpha: float = 0.25) -> float:
        """
        Compute score using the transparent baseline formula
        
        Args:
            matched_inclusions: List of matched inclusion predicates
            unmatched_inclusions: List of unmatched inclusion predicates  
            missing_inclusions: List of predicates with missing data
            total_inclusions: Total number of inclusion predicates
            alpha: Penalty factor for missing data (default: 0.25)
            
        Returns:
            Score between 0.0 and 100.0
        """
        if total_inclusions == 0:
            return 100.0  # No criteria to match
        
        # Calculate weights
        W = sum(r.predicate.weight for r in matched_inclusions + unmatched_inclusions + 
                [MatchResult(predicate=p, matched=False, evidence="missing") for p in missing_inclusions])
        M = sum(r.predicate.weight for r in matched_inclusions)
        U = sum(p.weight for p in missing_inclusions)
        
        # Log components for explainability
        logger.info(f"Scoring components: M={M}, W={W}, U={U}, alpha={alpha}")
        
        # Apply formula: Score = 100 * (M / W) - α * (U / W) * 100
        if W > 0:
            score = 100 * (M / W) - alpha * (U / W) * 100
            logger.info(f"Score calculation: {100 * (M / W):.2f} - {alpha * (U / W) * 100:.2f} = {score:.2f}")
        else:
            score = 0.0
            logger.warning("Total weight W is 0, setting score to 0")
        
        # Ensure score is within bounds
        score = max(0.0, min(100.0, score))
        
        return score
    
    def _calculate_score(self, matched_inclusions: List[MatchResult], total_inclusions: int) -> float:
        """
        Calculate weighted score based on matched inclusions (legacy method)
        
        Args:
            matched_inclusions: List of matched inclusion predicates
            total_inclusions: Total number of inclusion predicates
            
        Returns:
            Score between 0.0 and 1.0
        """
        if total_inclusions == 0:
            return 1.0  # No criteria to match
        
        # Calculate weighted score
        total_weight = sum(r.predicate.weight for r in matched_inclusions)
        max_possible_weight = sum(r.predicate.weight for r in matched_inclusions)  # This should be all predicates
        
        # For now, use simple percentage, but this could be enhanced
        base_score = len(matched_inclusions) / total_inclusions
        
        # Apply weight bonus
        weight_bonus = min(total_weight / (total_inclusions * 2), 0.2)  # Max 20% bonus for weights
        
        return min(base_score + weight_bonus, 1.0)
    
    def _determine_eligibility(self, matched_inclusions: List[MatchResult], 
                             unmatched_inclusions: List[MatchResult], 
                             total_inclusions: int, 
                             score: float = None) -> bool:
        """
        Determine if patient is eligible based on inclusion criteria
        
        Args:
            matched_inclusions: List of matched inclusion predicates
            unmatched_inclusions: List of unmatched inclusion predicates
            total_inclusions: Total number of inclusion predicates
            score: Computed score (0-100 scale)
            
        Returns:
            True if eligible, False otherwise
        """
        if total_inclusions == 0:
            return True  # No criteria to match
        
        # Use score-based eligibility if available
        if score is not None:
            # Default threshold: 80 points out of 100
            score_threshold = 80.0
            return score >= score_threshold
        
        # Fallback to coverage-based eligibility
        coverage_threshold = 0.8
        coverage = len(matched_inclusions) / total_inclusions
        
        return coverage >= coverage_threshold
    
    def _generate_reasons(self, matched_inclusions: List[MatchResult], 
                         unmatched_inclusions: List[MatchResult], 
                         missing_inclusions: List[Predicate]) -> List[str]:
        """
        Generate human-readable reasons for the match result
        
        Args:
            matched_inclusions: List of matched inclusion predicates
            unmatched_inclusions: List of unmatched inclusion predicates
            missing_inclusions: List of missing inclusion predicates
            
        Returns:
            List of reason strings
        """
        reasons = []
        
        # Add matched criteria
        if matched_inclusions:
            reasons.append(f"✅ Matched {len(matched_inclusions)} inclusion criteria:")
            for result in matched_inclusions:
                predicate = result.predicate
                if predicate.field:
                    reasons.append(f"   • {predicate.type}.{predicate.field}: {result.evidence}")
                elif predicate.code:
                    reasons.append(f"   • {predicate.type}.{predicate.code}: {result.evidence}")
        
        # Add unmatched criteria
        if unmatched_inclusions:
            reasons.append(f"❌ Failed {len(unmatched_inclusions)} inclusion criteria:")
            for result in unmatched_inclusions:
                predicate = result.predicate
                if predicate.field:
                    reasons.append(f"   • {predicate.type}.{predicate.field}: {result.evidence}")
                elif predicate.code:
                    reasons.append(f"   • {predicate.type}.{predicate.code}: {result.evidence}")
        
        # Add missing criteria
        if missing_inclusions:
            reasons.append(f"⚠️  Missing data for {len(missing_inclusions)} criteria:")
            for predicate in missing_inclusions:
                if predicate.field:
                    reasons.append(f"   • {predicate.type}.{predicate.field}")
                elif predicate.code:
                    reasons.append(f"   • {predicate.type}.{predicate.code}")
        
        return reasons
    
    def _generate_data_requests(self, missing_inclusions: List[Predicate]) -> List[str]:
        """
        Generate human-readable data requests for missing information
        
        Args:
            missing_inclusions: List of predicates with missing data
            
        Returns:
            List of human-readable data request strings
        """
        data_requests = []
        
        for predicate in missing_inclusions:
            request = self._create_data_request(predicate)
            if request:
                data_requests.append(request)
        
        return data_requests
    
    def _create_data_request(self, predicate: Predicate) -> str:
        """
        Create a human-readable data request for a specific predicate
        
        Args:
            predicate: Predicate with missing data
            
        Returns:
            Human-readable data request string
        """
        if predicate.type == "Patient":
            if predicate.field == "age":
                return "📋 Need patient age information"
            elif predicate.field == "gender":
                return "📋 Need patient gender information"
            else:
                return f"📋 Need patient {predicate.field} information"
        
        elif predicate.type == "Condition":
            if predicate.code:
                # Try to get a human-readable name for the condition
                condition_name = self._get_condition_name(predicate.code)
                return f"🏥 Need documentation of {condition_name}"
            else:
                return f"🏥 Need documentation of {predicate.field} condition"
        
        elif predicate.type == "Observation":
            if predicate.field:
                # Create specific requests based on common lab tests
                request = self._create_lab_request(predicate)
                if request:
                    return request
                else:
                    return f"🔬 Need {predicate.field} test results"
            else:
                return f"🔬 Need observation with code {predicate.code}"
        
        elif predicate.type == "Medication":
            if predicate.field:
                return f"💊 Need medication history for {predicate.field}"
            else:
                return f"💊 Need medication history for code {predicate.code}"
        
        return f"📋 Need {predicate.type} information for {predicate.field or predicate.code}"
    
    def _create_lab_request(self, predicate: Predicate) -> str:
        """
        Create specific lab test requests based on common test names
        
        Args:
            predicate: Observation predicate with missing data
            
        Returns:
            Specific lab request string or None for generic handling
        """
        field_lower = predicate.field.lower() if predicate.field else ""
        
        # Common lab test mappings
        lab_requests = {
            "her2": "🔬 Need HER2 IHC/ISH testing",
            "ecog": "📊 Need ECOG performance status assessment",
            "creatinine": "🩸 Need serum creatinine test",
            "hemoglobin": "🩸 Need complete blood count (CBC) for hemoglobin",
            "hgb": "🩸 Need complete blood count (CBC) for hemoglobin",
            "wbc": "🩸 Need complete blood count (CBC) for white blood cells",
            "platelets": "🩸 Need complete blood count (CBC) for platelets",
            "alt": "🩸 Need liver function tests (LFTs) for ALT",
            "ast": "🩸 Need liver function tests (LFTs) for AST",
            "bilirubin": "🩸 Need liver function tests (LFTs) for bilirubin",
            "albumin": "🩸 Need serum albumin test",
            "egfr": "🩸 Need estimated glomerular filtration rate (eGFR)",
            "psa": "🔬 Need prostate-specific antigen (PSA) test",
            "ca125": "🔬 Need CA-125 tumor marker test",
            "cea": "🔬 Need carcinoembryonic antigen (CEA) test",
            "afp": "🔬 Need alpha-fetoprotein (AFP) test",
            "hcg": "🔬 Need human chorionic gonadotropin (hCG) test",
            "ldh": "🩸 Need lactate dehydrogenase (LDH) test",
            "alkaline phosphatase": "🩸 Need alkaline phosphatase test",
            "calcium": "🩸 Need serum calcium test",
            "sodium": "🩸 Need basic metabolic panel for sodium",
            "potassium": "🩸 Need basic metabolic panel for potassium",
            "chloride": "🩸 Need basic metabolic panel for chloride",
            "co2": "🩸 Need basic metabolic panel for CO2",
            "bun": "🩸 Need blood urea nitrogen (BUN) test",
            "glucose": "🩸 Need fasting glucose test",
            "a1c": "🩸 Need hemoglobin A1c test",
            "troponin": "🩸 Need troponin test",
            "bnp": "🩸 Need B-type natriuretic peptide (BNP) test",
            "d-dimer": "🩸 Need D-dimer test",
            "pt": "🩸 Need prothrombin time (PT) test",
            "ptt": "🩸 Need partial thromboplastin time (PTT) test",
            "inr": "🩸 Need international normalized ratio (INR) test"
        }
        
        # Check for exact matches first
        if field_lower in lab_requests:
            return lab_requests[field_lower]
        
        # Check for partial matches
        for key, request in lab_requests.items():
            if key in field_lower or field_lower in key:
                return request
        
        # Check for common patterns
        if "count" in field_lower or "cbc" in field_lower:
            return "🩸 Need complete blood count (CBC)"
        elif "function" in field_lower or "lft" in field_lower:
            return "🩸 Need liver function tests (LFTs)"
        elif "metabolic" in field_lower or "bmp" in field_lower:
            return "🩸 Need basic metabolic panel (BMP)"
        elif "comprehensive" in field_lower or "cmp" in field_lower:
            return "🩸 Need comprehensive metabolic panel (CMP)"
        elif "tumor" in field_lower or "marker" in field_lower:
            return "🔬 Need tumor marker testing"
        elif "hormone" in field_lower:
            return "🔬 Need hormone testing"
        elif "vitamin" in field_lower:
            return "🩸 Need vitamin level testing"
        elif "thyroid" in field_lower:
            return "🔬 Need thyroid function tests"
        
        return None  # Let generic handler take over
    
    def _get_condition_name(self, snomed_code: str) -> str:
        """
        Get human-readable condition name from SNOMED code
        
        Args:
            snomed_code: SNOMED CT code
            
        Returns:
            Human-readable condition name
        """
        # Common SNOMED code mappings
        condition_names = {
            "363418001": "biliary tract cancer",
            "128462008": "CNS metastases",
            "254637007": "breast cancer",
            "254632001": "lung cancer",
            "254637007": "prostate cancer",
            "254632001": "colorectal cancer",
            "254637007": "ovarian cancer",
            "254632001": "pancreatic cancer",
            "254637007": "gastric cancer",
            "254632001": "esophageal cancer",
            "254637007": "bladder cancer",
            "254632001": "kidney cancer",
            "254637007": "liver cancer",
            "254632001": "brain cancer",
            "254637007": "leukemia",
            "254632001": "lymphoma",
            "254637007": "melanoma",
            "254632001": "sarcoma",
            "254637007": "multiple myeloma",
            "254632001": "mesothelioma"
        }
        
        return condition_names.get(snomed_code, f"condition (code: {snomed_code})")
    
    def evaluate_multiple_trials(self, patient_features: Dict[str, Any], 
                               trials_data: List[Tuple[str, List[Predicate]]]) -> List[Tuple[str, TrialMatchResult]]:
        """
        Evaluate patient against multiple trials
        
        Args:
            patient_features: Extracted patient features
            trials_data: List of (trial_id, predicates) tuples
            
        Returns:
            List of (trial_id, TrialMatchResult) tuples sorted by score
        """
        results = []
        
        for trial_id, predicates in trials_data:
            result = self.evaluate_trial(patient_features, predicates)
            results.append((trial_id, result))
        
        # Sort by score (descending) and eligibility
        results.sort(key=lambda x: (x[1].eligible, x[1].score), reverse=True)
        
        return results

def create_sample_trials() -> List[Tuple[str, List[Predicate]]]:
    """Create sample trials for testing"""
    try:
        from .predicates import Predicate
    except ImportError:
        from predicates import Predicate
    
    # Trial 1: HER2+ Biliary Cancer (should be eligible)
    trial1_predicates = [
        # Inclusions
        Predicate(type="Patient", field="age", op=">=", value=18, weight=2, inclusion=True),
        Predicate(type="Condition", code="363418001", op="present", weight=5, inclusion=True),  # Biliary cancer
        Predicate(type="Observation", field="HER2", op="==", value="positive", weight=3, inclusion=True),
        Predicate(type="Observation", field="Hemoglobin", op=">=", value=10, unit="g/dL", weight=1, inclusion=True),
        # Exclusions
        Predicate(type="Medication", field="Trastuzumab", op="present", inclusion=False, reason="Previous HER2 treatment")
    ]
    
    # Trial 2: Excluded due to CNS metastases (patient has CNS metastases)
    trial2_predicates = [
        # Inclusions
        Predicate(type="Patient", field="age", op=">=", value=18, weight=2, inclusion=True),
        Predicate(type="Condition", code="363418001", op="present", weight=5, inclusion=True),  # Biliary cancer
        Predicate(type="Observation", field="HER2", op="==", value="positive", weight=3, inclusion=True),
        # Exclusions
        Predicate(type="Condition", code="128462008", op="present", inclusion=False, reason="CNS metastases")
    ]
    
    # Trial 3: Partial match (missing some criteria, no exclusions)
    trial3_predicates = [
        # Inclusions
        Predicate(type="Patient", field="age", op=">=", value=18, weight=2, inclusion=True),
        Predicate(type="Condition", code="363418001", op="present", weight=5, inclusion=True),  # Biliary cancer
        Predicate(type="Observation", field="HER2", op="==", value="positive", weight=3, inclusion=True),
        Predicate(type="Observation", field="ECOG", op="<=", value=2, weight=2, inclusion=True),  # Missing
        Predicate(type="Observation", field="Creatinine", op="<=", value=1.5, unit="mg/dL", weight=1, inclusion=True),  # Missing
        # No exclusions
    ]
    
    return [
        ("NCT07062263", trial1_predicates),
        ("NCT12345678", trial2_predicates),
        ("NCT87654321", trial3_predicates)
    ]

def test_matching_engine():
    """Test the matching engine with sample data"""
    print("🧪 Testing Matching Engine")
    print("=" * 60)
    
    # Create matching engine
    engine = MatchingEngine()
    
    # Create sample patient features
    patient_features = {
        "age": 52,
        "gender": "female",
        "conditions": [
            {
                "text": "Biliary tract cancer",
                "codes": [
                    {"system": "http://snomed.info/sct", "code": "363418001", "display": "Biliary tract cancer"}
                ],
                "status": "active"
            },
            {
                "text": "CNS metastases",
                "codes": [
                    {"system": "http://snomed.info/sct", "code": "128462008", "display": "CNS metastases"}
                ],
                "status": "active"
            }
        ],
        "observations": [
            {
                "text": "HER2",
                "codes": [
                    {"system": "http://loinc.org", "code": "85319-0", "display": "HER2"}
                ],
                "value": "positive",
                "status": "final"
            },
            {
                "text": "Hemoglobin",
                "codes": [
                    {"system": "http://loinc.org", "code": "718-7", "display": "Hemoglobin"}
                ],
                "value": 13.2,
                "unit": "g/dL",
                "status": "final"
            }
        ],
        "medications": [],
        "lab_results": [],
        "vital_signs": {}
    }
    
    # Create sample trials
    trials_data = create_sample_trials()
    
    # Evaluate all trials
    results = engine.evaluate_multiple_trials(patient_features, trials_data)
    
    # Print results
    for i, (trial_id, result) in enumerate(results, 1):
        print(f"\n📋 Trial {i}: {trial_id}")
        print("-" * 40)
        print(f"   Eligibility: {'✅ ELIGIBLE' if result.eligible else '❌ INELIGIBLE'}")
        print(f"   Score: {result.score:.1f}/100")
        print(f"   Coverage: {result.coverage_percentage:.1f}% ({result.matched_count}/{result.total_inclusions})")
        
        if result.exclusions_triggered:
            print(f"   🚫 Exclusions Triggered: {len(result.exclusions_triggered)}")
            for exclusion in result.exclusions_triggered:
                print(f"      • {exclusion.evidence}")
        
        print(f"   📊 Details:")
        for reason in result.reasons[:5]:  # Show first 5 reasons
            print(f"      {reason}")
        
        if len(result.reasons) > 5:
            print(f"      ... and {len(result.reasons) - 5} more reasons")
        
        # Show suggested data requests
        if result.suggested_data:
            print(f"   📋 Suggested Data Requests:")
            for request in result.suggested_data:
                print(f"      {request}")
    
    print(f"\n✅ Matching engine test completed!")

def test_scoring_formula():
    """Unit test the scoring formula with crafted values"""
    print("\n🧪 Testing Scoring Formula")
    print("=" * 50)
    
    engine = MatchingEngine()
    
    # Test cases with known expected results
    test_cases = [
        {
            "name": "Perfect Match",
            "matched_weights": [5, 3, 2],  # M = 10
            "unmatched_weights": [],        # 0
            "missing_weights": [],          # U = 0
            "expected_score": 100.0,        # 100 * (10/10) - 0.25 * (0/10) * 100 = 100
            "description": "All criteria matched, no missing data"
        },
        {
            "name": "Partial Match",
            "matched_weights": [5, 3],      # M = 8
            "unmatched_weights": [2],       # 2
            "missing_weights": [],          # U = 0
            "expected_score": 80.0,         # 100 * (8/10) - 0.25 * (0/10) * 100 = 80
            "description": "Some criteria matched, some failed"
        },
        {
            "name": "Missing Data Penalty",
            "matched_weights": [5, 3],      # M = 8
            "unmatched_weights": [2],       # 2
            "missing_weights": [1],         # U = 1
            "expected_score": 70.5,         # 100 * (8/11) - 0.25 * (1/11) * 100 = 72.73 - 2.27 = 70.46
            "description": "Missing data incurs penalty"
        },
        {
            "name": "All Missing Data",
            "matched_weights": [],           # M = 0
            "unmatched_weights": [],        # 0
            "missing_weights": [5, 3, 2],   # U = 10
            "expected_score": 0.0,          # 100 * (0/10) - 0.25 * (10/10) * 100 = 0 - 25 = -25, but clamped to 0
            "description": "All data missing, maximum penalty (clamped to 0)"
        },
        {
            "name": "No Criteria",
            "matched_weights": [],           # M = 0
            "unmatched_weights": [],        # 0
            "missing_weights": [],          # U = 0
            "expected_score": 100.0,        # No criteria to match
            "description": "No inclusion criteria defined"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 Test {i}: {test_case['name']}")
        print(f"   Description: {test_case['description']}")
        
        # Create mock data structures
        matched_inclusions = [
            MatchResult(
                predicate=Predicate(type="Test", field=f"field_{j}", weight=weight, inclusion=True),
                matched=True,
                evidence=f"Matched with weight {weight}"
            )
            for j, weight in enumerate(test_case['matched_weights'])
        ]
        
        unmatched_inclusions = [
            MatchResult(
                predicate=Predicate(type="Test", field=f"field_{j}", weight=weight, inclusion=True),
                matched=False,
                evidence=f"Failed with weight {weight}"
            )
            for j, weight in enumerate(test_case['unmatched_weights'])
        ]
        
        missing_inclusions = [
            Predicate(type="Test", field=f"field_{j}", weight=weight, inclusion=True)
            for j, weight in enumerate(test_case['missing_weights'])
        ]
        
        total_inclusions = len(matched_inclusions) + len(unmatched_inclusions) + len(missing_inclusions)
        
        # Calculate score
        score = engine.compute_score(matched_inclusions, unmatched_inclusions, missing_inclusions, total_inclusions)
        
        # Check result
        expected = test_case['expected_score']
        tolerance = 0.1  # Allow small floating point differences
        
        if abs(score - expected) <= tolerance:
            print(f"   ✅ PASS: Score = {score:.1f} (expected: {expected:.1f})")
        else:
            print(f"   ❌ FAIL: Score = {score:.1f} (expected: {expected:.1f})")
            print(f"   Components: M={sum(test_case['matched_weights'])}, "
                  f"W={sum(test_case['matched_weights'] + test_case['unmatched_weights'] + test_case['missing_weights'])}, "
                  f"U={sum(test_case['missing_weights'])}")
    
    print(f"\n✅ Scoring formula test completed!")

if __name__ == "__main__":
    test_matching_engine()
    test_scoring_formula()
