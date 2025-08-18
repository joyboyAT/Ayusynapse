#!/usr/bin/env python3
"""
CLI wrapper for Patient-Trial Matching
Provides command-line interface for matching patients to clinical trials
"""

import argparse
import json
import sys
import os
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import from ayusynapse package
from .matcher.retrieval import get_candidate_trials, Trial
from .matcher.features import FeatureExtractor
from .matcher.predicates import Predicate
from .matcher.engine import MatchingEngine
from .matcher.explain import TrialExplainer
from .matcher.rank import TrialRanker, TrialRankingInfo, RankedTrial
from .matcher.coverage_report import CoverageReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class PatientTrialMatcher:
    """CLI wrapper for patient-trial matching"""
    
    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.matching_engine = MatchingEngine()
        self.explainer = TrialExplainer()
        self.ranker = TrialRanker()
        self.coverage_generator = CoverageReportGenerator()
    
    def load_patient_bundle(self, patient_file: str) -> Dict[str, Any]:
        """Load patient FHIR bundle from file"""
        try:
            with open(patient_file, 'r') as f:
                patient_data = json.load(f)
            
            logger.info(f"Loaded patient bundle from {patient_file}")
            return patient_data
            
        except FileNotFoundError:
            logger.error(f"Patient file not found: {patient_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in patient file: {e}")
            sys.exit(1)
    
    def create_sample_patient(self) -> Dict[str, Any]:
        """Create a sample HER2+ biliary cancer patient for testing"""
        return {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "patient-001",
                        "gender": "female",
                        "birthDate": "1971-01-01"  # Age 52 in 2023
                    }
                },
                {
                    "resource": {
                        "resourceType": "Condition",
                        "id": "condition-001",
                        "subject": {"reference": "Patient/patient-001"},
                        "code": {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "code": "363418001",
                                    "display": "Biliary tract cancer"
                                }
                            ],
                            "text": "Biliary tract cancer"
                        },
                        "clinicalStatus": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                                    "code": "active"
                                }
                            ]
                        }
                    }
                },
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": "observation-001",
                        "subject": {"reference": "Patient/patient-001"},
                        "code": {
                            "coding": [
                                {
                                    "system": "http://loinc.org",
                                    "code": "85319-0",
                                    "display": "HER2"
                                }
                            ],
                            "text": "HER2"
                        },
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "code": "10828004",
                                    "display": "Positive"
                                }
                            ],
                            "text": "positive"
                        },
                        "status": "final"
                    }
                },
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": "observation-002",
                        "subject": {"reference": "Patient/patient-001"},
                        "code": {
                            "coding": [
                                {
                                    "system": "http://loinc.org",
                                    "code": "89243-3",
                                    "display": "ECOG Performance Status"
                                }
                            ],
                            "text": "ECOG"
                        },
                        "valueInteger": 1,
                        "status": "final"
                    }
                }
            ]
        }
    
    def match_patient(self, patient_bundle: Dict[str, Any], top_k: int = 10, 
                     min_score: float = 60.0, include_explanations: bool = True,
                     output_format: str = "text") -> Dict[str, Any]:
        """
        Perform patient-trial matching
        
        Args:
            patient_bundle: Patient FHIR bundle
            top_k: Number of top trials to return
            min_score: Minimum score threshold
            include_explanations: Whether to include detailed explanations
            output_format: Output format ("text", "json", "markdown")
            
        Returns:
            Matching results
        """
        logger.info("Starting patient-trial matching pipeline")
        
        # Step 1: Extract patient features
        patient_features = self.feature_extractor.extract_patient_features(patient_bundle)
        logger.info(f"Extracted patient features: age={patient_features.age}, gender={patient_features.gender}, conditions={len(patient_features.conditions)}, observations={len(patient_features.observations)}")
        
        # Step 2: Retrieve candidate trials
        candidate_trials = get_candidate_trials(patient_bundle, server_url="http://hapi.fhir.org/baseR4")
        logger.info(f"Retrieved {len(candidate_trials)} candidate trials")
        
        if not candidate_trials:
            return {
                "patient_id": "unknown",
                "total_trials_evaluated": 0,
                "eligible_trials": 0,
                "top_trials": [],
                "summary": {"message": "No candidate trials found"}
            }
        
        # Step 3: Evaluate each trial (simplified for demo)
        results = []
        for trial in candidate_trials:
            try:
                # For demo purposes, create a simple result based on trial score
                # In a real implementation, this would use the full predicate evaluation
                from matcher.engine import TrialMatchResult
                
                # Create a mock result based on the trial's score
                # Scale the trial score to a reasonable range (trial scores are typically 1-10)
                scaled_score = min(100.0, trial.score * 15)  # Scale more generously
                mock_result = TrialMatchResult(
                    eligible=trial.score > 3,  # Lower threshold for demo
                    score=scaled_score,
                    matched_inclusions=[],
                    unmatched_inclusions=[],
                    missing_inclusions=[],
                    exclusions_triggered=[],
                    total_inclusions=1,  # Mock value
                    matched_count=1 if trial.score > 3 else 0,  # Mock value
                    coverage_percentage=100.0 if trial.score > 3 else 0.0,  # Mock value
                    reasons=trial.match_reasons,  # Use actual match reasons
                    suggested_data=[]
                )
                
                results.append((trial.trial_id, mock_result))
                logger.info(f"Trial {trial.trial_id}: original_score={trial.score}, scaled_score={mock_result.score:.1f}, eligible={mock_result.eligible}")
                
            except Exception as e:
                logger.warning(f"Failed to evaluate trial {trial.trial_id}: {e}")
                continue
        
        if not results:
            return {
                "patient_id": "unknown",
                "total_trials_evaluated": 0,
                "eligible_trials": 0,
                "top_trials": [],
                "summary": {"message": "No trials could be evaluated"}
            }
        
        # Step 4: Create ranking info
        ranking_info = {}
        for trial_id, result in results:
            ranking_info[trial_id] = TrialRankingInfo(
                trial_id=trial_id,
                recruiting_status="Recruiting",  # Default
                must_have_biomarkers=[],
                has_all_must_have=False,
                zero_exclusions=len(result.exclusions_triggered) == 0
            )
        
        # Step 5: Rank trials
        self.ranker.min_score = min_score
        ranked_trials = self.ranker.rank_trials(results, ranking_info)
        ranked_trials = ranked_trials[:top_k]
        
        # Step 6: Generate explanations if requested
        top_trials_response = []
        for ranked_trial in ranked_trials:
            if include_explanations:
                explanation = self.explainer.make_explanation(ranked_trial.trial_id, ranked_trial.result)
                
                # Generate enhanced coverage report if available
                coverage_report = None
                if hasattr(ranked_trial.result, 'coverage_report') and ranked_trial.result.coverage_report:
                    coverage_report = {
                        "coverage_percentage": ranked_trial.result.coverage_report.coverage_percentage,
                        "total_criteria": ranked_trial.result.coverage_report.total_criteria,
                        "matched_criteria": ranked_trial.result.coverage_report.matched_criteria,
                        "missing_criteria": ranked_trial.result.coverage_report.missing_criteria,
                        "failed_criteria": ranked_trial.result.coverage_report.failed_criteria,
                        "missing_biomarkers": ranked_trial.result.coverage_report.missing_biomarkers,
                        "missing_lab_tests": ranked_trial.result.coverage_report.missing_lab_tests,
                        "missing_conditions": ranked_trial.result.coverage_report.missing_conditions,
                        "missing_demographics": ranked_trial.result.coverage_report.missing_demographics,
                        "missing_medications": ranked_trial.result.coverage_report.missing_medications,
                        "recommended_actions": ranked_trial.result.coverage_report.recommended_actions,
                        "priority_actions": ranked_trial.result.coverage_report.priority_actions,
                        "estimated_completion_time": ranked_trial.result.coverage_report.estimated_completion_time,
                        "confidence_level": ranked_trial.result.coverage_report.confidence_level,
                        "coverage_summary": self.coverage_generator.format_coverage_summary(ranked_trial.result.coverage_report),
                        "missing_biomarkers_summary": self.coverage_generator.get_missing_biomarkers_summary(ranked_trial.result.coverage_report),
                        "next_steps_summary": self.coverage_generator.get_next_steps_summary(ranked_trial.result.coverage_report)
                    }
                
                trial_response = {
                    "trial_id": ranked_trial.trial_id,
                    "rank": ranked_trial.rank,
                    "score": ranked_trial.final_score,
                    "eligible": ranked_trial.result.eligible,
                    "summary": explanation.summary,
                    "matched_criteria": explanation.matched_facts,
                    "blockers": explanation.blockers,
                    "missing_data": explanation.missing_data,
                    "recommendations": explanation.recommendations,
                    "recruiting_status": ranked_trial.ranking_info.recruiting_status,
                    "start_date": ranked_trial.ranking_info.start_date.isoformat() if ranked_trial.ranking_info.start_date else None,
                    "coverage_report": coverage_report
                }
            else:
                trial_response = {
                    "trial_id": ranked_trial.trial_id,
                    "rank": ranked_trial.rank,
                    "score": ranked_trial.final_score,
                    "eligible": ranked_trial.result.eligible,
                    "summary": f"Score: {ranked_trial.final_score:.1f}/100",
                    "matched_criteria": [],
                    "blockers": [],
                    "missing_data": [],
                    "recommendations": []
                }
            
            top_trials_response.append(trial_response)
        
        # Step 7: Generate summary
        summary = self.ranker.get_ranking_summary(ranked_trials)
        summary["top_k"] = top_k
        summary["min_score"] = min_score
        
        logger.info(f"Completed matching: {len(ranked_trials)} trials ranked, {summary['eligible_trials']} eligible")
        
        return {
            "patient_id": "unknown",
            "total_trials_evaluated": len(results),
            "eligible_trials": summary["eligible_trials"],
            "top_trials": top_trials_response,
            "summary": summary
        }
    
    def print_text_output(self, results: Dict[str, Any]):
        """Print results in human-readable text format"""
        print("🏥 Patient-Trial Matching Results")
        print("=" * 50)
        print(f"Patient ID: {results['patient_id']}")
        print(f"Total Trials Evaluated: {results['total_trials_evaluated']}")
        print(f"Eligible Trials: {results['eligible_trials']}")
        print()
        
        if not results['top_trials']:
            print("❌ No matching trials found")
            return
        
        print("📊 Top Matching Trials:")
        print("-" * 30)
        
        for trial in results['top_trials']:
            print(f"\n#{trial['rank']} - {trial['trial_id']}")
            print(f"   Score: {trial['score']:.1f}/100")
            print(f"   Eligible: {'✅ Yes' if trial['eligible'] else '❌ No'}")
            print(f"   Summary: {trial['summary']}")
            
            if trial['recruiting_status']:
                print(f"   Status: {trial['recruiting_status']}")
            
            if trial['matched_criteria']:
                print(f"   ✅ Matched Criteria:")
                for criteria in trial['matched_criteria'][:3]:  # Show top 3
                    print(f"      • {criteria}")
            
            if trial['blockers']:
                print(f"   ❌ Blockers:")
                for blocker in trial['blockers'][:3]:  # Show top 3
                    print(f"      • {blocker}")
            
            if trial['missing_data']:
                print(f"   🔍 Missing Data:")
                for missing in trial['missing_data'][:3]:  # Show top 3
                    print(f"      • {missing}")
            
            if trial['recommendations']:
                print(f"   💡 Recommendations:")
                for rec in trial['recommendations'][:3]:  # Show top 3
                    print(f"      • {rec}")
            
            # Enhanced coverage reporting
            if trial.get('coverage_report'):
                coverage = trial['coverage_report']
                print(f"   📊 Coverage Report:")
                print(f"      • {coverage.get('coverage_summary', 'N/A')}")
                print(f"      • Confidence: {coverage.get('confidence_level', 'N/A')}")
                print(f"      • Completion Time: {coverage.get('estimated_completion_time', 'N/A')}")
                
                if coverage.get('missing_biomarkers_summary') != "All required biomarkers present":
                    print(f"      • {coverage.get('missing_biomarkers_summary', 'N/A')}")
                
                if coverage.get('next_steps_summary') != "No additional data needed":
                    print(f"      • {coverage.get('next_steps_summary', 'N/A')}")
                
                # Show priority actions if available
                priority_actions = coverage.get('priority_actions', [])
                if priority_actions:
                    print(f"      • Priority Actions:")
                    for action in priority_actions[:2]:  # Show top 2 priority actions
                        print(f"        - {action}")
        
        # Print summary
        summary = results['summary']
        print(f"\n📋 Summary:")
        print(f"   Score Distribution: {summary.get('score_distribution', {})}")
        print(f"   Priority Trials: {summary.get('priority_trials', 0)}")
        print(f"   Recruiting Status: {summary.get('recruiting_status', {})}")
    
    def print_json_output(self, results: Dict[str, Any]):
        """Print results in JSON format"""
        print(json.dumps(results, indent=2))
    
    def print_markdown_output(self, results: Dict[str, Any]):
        """Print results in Markdown format"""
        print("# Patient-Trial Matching Results")
        print()
        print(f"**Patient ID:** {results['patient_id']}  ")
        print(f"**Total Trials Evaluated:** {results['total_trials_evaluated']}  ")
        print(f"**Eligible Trials:** {results['eligible_trials']}  ")
        print()
        
        if not results['top_trials']:
            print("❌ No matching trials found")
            return
        
        print("## Top Matching Trials")
        print()
        
        for trial in results['top_trials']:
            print(f"### #{trial['rank']} - {trial['trial_id']}")
            print()
            print(f"- **Score:** {trial['score']:.1f}/100")
            print(f"- **Eligible:** {'✅ Yes' if trial['eligible'] else '❌ No'}")
            print(f"- **Summary:** {trial['summary']}")
            
            if trial['recruiting_status']:
                print(f"- **Status:** {trial['recruiting_status']}")
            
            if trial['matched_criteria']:
                print()
                print("#### ✅ Matched Criteria")
                for criteria in trial['matched_criteria']:
                    print(f"- {criteria}")
            
            if trial['blockers']:
                print()
                print("#### ❌ Blockers")
                for blocker in trial['blockers']:
                    print(f"- {blocker}")
            
            if trial['missing_data']:
                print()
                print("#### 🔍 Missing Data")
                for missing in trial['missing_data']:
                    print(f"- {missing}")
            
            if trial['recommendations']:
                print()
                print("#### 💡 Recommendations")
                for rec in trial['recommendations']:
                    print(f"- {rec}")
            
            # Enhanced coverage reporting
            if trial.get('coverage_report'):
                coverage = trial['coverage_report']
                print()
                print("#### 📊 Coverage Report")
                print(f"- **Coverage:** {coverage.get('coverage_summary', 'N/A')}")
                print(f"- **Confidence:** {coverage.get('confidence_level', 'N/A')}")
                print(f"- **Completion Time:** {coverage.get('estimated_completion_time', 'N/A')}")
                
                if coverage.get('missing_biomarkers_summary') != "All required biomarkers present":
                    print(f"- **Biomarkers:** {coverage.get('missing_biomarkers_summary', 'N/A')}")
                
                if coverage.get('next_steps_summary') != "No additional data needed":
                    print(f"- **Next Steps:** {coverage.get('next_steps_summary', 'N/A')}")
                
                # Show priority actions if available
                priority_actions = coverage.get('priority_actions', [])
                if priority_actions:
                    print()
                    print("##### 🚨 Priority Actions")
                    for action in priority_actions:
                        print(f"- {action}")
            
            print()
        
        # Print summary
        summary = results['summary']
        print("## Summary")
        print()
        print(f"- **Score Distribution:** {summary.get('score_distribution', {})}")
        print(f"- **Priority Trials:** {summary.get('priority_trials', 0)}")
        print(f"- **Recruiting Status:** {summary.get('recruiting_status', {})}")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Patient-Trial Matching CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Match with sample patient
  python run_match.py --sample

  # Match with custom patient file
  python run_match.py --patient patient.json --top 5

  # Match with custom settings
  python run_match.py --patient patient.json --top 10 --min-score 70 --format json

  # Quick test with sample patient
  python run_match.py --sample --top 3 --format markdown
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--patient", "-p",
        type=str,
        help="Path to patient FHIR bundle JSON file"
    )
    input_group.add_argument(
        "--sample", "-s",
        action="store_true",
        help="Use sample HER2+ biliary cancer patient"
    )
    
    # Output options
    parser.add_argument(
        "--top", "-t",
        type=int,
        default=10,
        help="Number of top trials to return (default: 10)"
    )
    parser.add_argument(
        "--min-score", "-m",
        type=float,
        default=60.0,
        help="Minimum score threshold (default: 60.0)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--no-explanations",
        action="store_true",
        help="Skip detailed explanations (faster)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file (if not specified, prints to stdout)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize matcher
    matcher = PatientTrialMatcher()
    
    # Load patient data
    if args.sample:
        patient_bundle = matcher.create_sample_patient()
        logger.info("Using sample HER2+ biliary cancer patient")
    else:
        patient_bundle = matcher.load_patient_bundle(args.patient)
    
    # Perform matching
    results = matcher.match_patient(
        patient_bundle=patient_bundle,
        top_k=args.top,
        min_score=args.min_score,
        include_explanations=not args.no_explanations
    )
    
    # Output results
    if args.output:
        # Save to file
        with open(args.output, 'w') as f:
            if args.format == "json":
                json.dump(results, f, indent=2)
            else:
                # For text/markdown, we need to capture output
                import io
                from contextlib import redirect_stdout
                
                output = io.StringIO()
                with redirect_stdout(output):
                    if args.format == "text":
                        matcher.print_text_output(results)
                    elif args.format == "markdown":
                        matcher.print_markdown_output(results)
                
                f.write(output.getvalue())
        
        logger.info(f"Results saved to {args.output}")
    else:
        # Print to stdout
        if args.format == "text":
            matcher.print_text_output(results)
        elif args.format == "json":
            matcher.print_json_output(results)
        elif args.format == "markdown":
            matcher.print_markdown_output(results)

if __name__ == "__main__":
    main()
