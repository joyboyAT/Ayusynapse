#!/usr/bin/env python3
"""
Coverage Report Generator for Patient-Trial Matching
Provides detailed analysis of missing criteria and actionable recommendations
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from collections import defaultdict

from .predicates import Predicate
from .types import TrialMatchResult, MatchResult

logger = logging.getLogger(__name__)

@dataclass
class CoverageReport:
    """Comprehensive coverage report for a patient-trial match"""
    coverage_percentage: float
    total_criteria: int
    matched_criteria: int
    missing_criteria: int
    failed_criteria: int
    missing_biomarkers: List[str]
    missing_lab_tests: List[str]
    missing_conditions: List[str]
    missing_demographics: List[str]
    missing_medications: List[str]
    recommended_actions: List[str]
    priority_actions: List[str]
    estimated_completion_time: str
    confidence_level: str

class CoverageReportGenerator:
    """Generates comprehensive coverage reports for patient-trial matching"""
    
    def __init__(self):
        """Initialize the coverage report generator"""
        self.biomarker_mappings = self._load_biomarker_mappings()
        self.lab_test_mappings = self._load_lab_test_mappings()
        self.condition_mappings = self._load_condition_mappings()
    
    def _load_biomarker_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Load biomarker-specific information and recommendations"""
        return {
            "her2": {
                "test_name": "HER2 IHC/ISH",
                "urgency": "high",
                "time_to_result": "3-5 days",
                "cost": "$$",
                "description": "HER2 protein expression and gene amplification testing"
            },
            "egfr": {
                "test_name": "EGFR Mutation Testing",
                "urgency": "high", 
                "time_to_result": "7-10 days",
                "cost": "$$$",
                "description": "EGFR gene mutation analysis"
            },
            "alk": {
                "test_name": "ALK Rearrangement Testing",
                "urgency": "high",
                "time_to_result": "7-10 days", 
                "cost": "$$$",
                "description": "ALK gene rearrangement analysis"
            },
            "kras": {
                "test_name": "KRAS Mutation Testing",
                "urgency": "medium",
                "time_to_result": "5-7 days",
                "cost": "$$",
                "description": "KRAS gene mutation analysis"
            },
            "braf": {
                "test_name": "BRAF Mutation Testing", 
                "urgency": "medium",
                "time_to_result": "5-7 days",
                "cost": "$$",
                "description": "BRAF gene mutation analysis"
            },
            "pdl1": {
                "test_name": "PD-L1 IHC Testing",
                "urgency": "medium",
                "time_to_result": "3-5 days",
                "cost": "$$",
                "description": "PD-L1 protein expression testing"
            },
            "msi": {
                "test_name": "MSI/MMR Testing",
                "urgency": "medium",
                "time_to_result": "7-10 days",
                "cost": "$$$",
                "description": "Microsatellite instability testing"
            },
            "tmb": {
                "test_name": "Tumor Mutational Burden",
                "urgency": "medium",
                "time_to_result": "10-14 days",
                "cost": "$$$$",
                "description": "Tumor mutational burden analysis"
            }
        }
    
    def _load_lab_test_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Load lab test-specific information and recommendations"""
        return {
            "hemoglobin": {
                "test_name": "Complete Blood Count (CBC)",
                "urgency": "low",
                "time_to_result": "1-2 hours",
                "cost": "$",
                "description": "Hemoglobin level measurement"
            },
            "creatinine": {
                "test_name": "Comprehensive Metabolic Panel",
                "urgency": "low",
                "time_to_result": "1-2 hours", 
                "cost": "$",
                "description": "Serum creatinine measurement"
            },
            "alt": {
                "test_name": "Liver Function Tests",
                "urgency": "low",
                "time_to_result": "1-2 hours",
                "cost": "$",
                "description": "Alanine aminotransferase measurement"
            },
            "ast": {
                "test_name": "Liver Function Tests", 
                "urgency": "low",
                "time_to_result": "1-2 hours",
                "cost": "$",
                "description": "Aspartate aminotransferase measurement"
            },
            "bilirubin": {
                "test_name": "Liver Function Tests",
                "urgency": "low", 
                "time_to_result": "1-2 hours",
                "cost": "$",
                "description": "Total bilirubin measurement"
            },
            "albumin": {
                "test_name": "Comprehensive Metabolic Panel",
                "urgency": "low",
                "time_to_result": "1-2 hours",
                "cost": "$", 
                "description": "Serum albumin measurement"
            },
            "ecog": {
                "test_name": "ECOG Performance Status Assessment",
                "urgency": "low",
                "time_to_result": "Immediate",
                "cost": "$",
                "description": "Performance status evaluation"
            }
        }
    
    def _load_condition_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Load condition-specific information and recommendations"""
        return {
            "diabetes": {
                "documentation": "Diabetes mellitus diagnosis and management",
                "urgency": "medium",
                "time_to_obtain": "1-2 days",
                "description": "Documentation of diabetes diagnosis and current management"
            },
            "hypertension": {
                "documentation": "Hypertension diagnosis and management", 
                "urgency": "medium",
                "time_to_obtain": "1-2 days",
                "description": "Documentation of hypertension diagnosis and current management"
            },
            "heart_disease": {
                "documentation": "Cardiac history and current status",
                "urgency": "high",
                "time_to_obtain": "2-3 days",
                "description": "Documentation of cardiac conditions and current cardiac status"
            },
            "lung_disease": {
                "documentation": "Pulmonary history and current status",
                "urgency": "high",
                "time_to_obtain": "2-3 days", 
                "description": "Documentation of pulmonary conditions and current respiratory status"
            }
        }
    
    def generate_coverage_report(self, patient_features: Dict[str, Any], 
                               trial_result: TrialMatchResult,
                               trial_id: str = "Unknown") -> CoverageReport:
        """
        Generate a comprehensive coverage report for a patient-trial match
        
        Args:
            patient_features: Extracted patient features
            trial_result: Result of trial evaluation
            trial_id: Trial identifier for context
            
        Returns:
            CoverageReport with detailed analysis
        """
        logger.info(f"Generating coverage report for trial {trial_id}")
        
        # Calculate basic metrics
        total_criteria = trial_result.total_inclusions
        matched_criteria = len(trial_result.matched_inclusions)
        missing_criteria = len(trial_result.missing_inclusions)
        failed_criteria = len(trial_result.unmatched_inclusions)
        
        coverage_percentage = (matched_criteria / total_criteria * 100) if total_criteria > 0 else 0.0
        
        # Categorize missing criteria
        missing_biomarkers = []
        missing_lab_tests = []
        missing_conditions = []
        missing_demographics = []
        missing_medications = []
        
        for predicate in trial_result.missing_inclusions:
            category = self._categorize_missing_criteria(predicate)
            if category == "biomarker":
                missing_biomarkers.append(predicate.field or predicate.code)
            elif category == "lab_test":
                missing_lab_tests.append(predicate.field or predicate.code)
            elif category == "condition":
                missing_conditions.append(predicate.field or predicate.code)
            elif category == "demographic":
                missing_demographics.append(predicate.field or predicate.code)
            elif category == "medication":
                missing_medications.append(predicate.field or predicate.code)
        
        # Generate recommendations
        recommended_actions = self._generate_recommendations(
            missing_biomarkers, missing_lab_tests, missing_conditions, 
            missing_demographics, missing_medications
        )
        
        # Generate priority actions
        priority_actions = self._generate_priority_actions(
            missing_biomarkers, missing_lab_tests, missing_conditions,
            missing_demographics, missing_medications
        )
        
        # Estimate completion time
        estimated_completion_time = self._estimate_completion_time(
            missing_biomarkers, missing_lab_tests, missing_conditions,
            missing_demographics, missing_medications
        )
        
        # Determine confidence level
        confidence_level = self._determine_confidence_level(
            coverage_percentage, missing_criteria, failed_criteria
        )
        
        return CoverageReport(
            coverage_percentage=coverage_percentage,
            total_criteria=total_criteria,
            matched_criteria=matched_criteria,
            missing_criteria=missing_criteria,
            failed_criteria=failed_criteria,
            missing_biomarkers=missing_biomarkers,
            missing_lab_tests=missing_lab_tests,
            missing_conditions=missing_conditions,
            missing_demographics=missing_demographics,
            missing_medications=missing_medications,
            recommended_actions=recommended_actions,
            priority_actions=priority_actions,
            estimated_completion_time=estimated_completion_time,
            confidence_level=confidence_level
        )
    
    def _categorize_missing_criteria(self, predicate: Predicate) -> str:
        """Categorize missing criteria by type"""
        if predicate.type == "Observation":
            field_lower = (predicate.field or "").lower()
            if any(biomarker in field_lower for biomarker in self.biomarker_mappings.keys()):
                return "biomarker"
            elif any(test in field_lower for test in self.lab_test_mappings.keys()):
                return "lab_test"
            else:
                return "lab_test"  # Default for observations
        elif predicate.type == "Condition":
            return "condition"
        elif predicate.type == "Patient":
            return "demographic"
        elif predicate.type == "Medication":
            return "medication"
        else:
            return "other"
    
    def _generate_recommendations(self, missing_biomarkers: List[str], 
                                missing_lab_tests: List[str],
                                missing_conditions: List[str],
                                missing_demographics: List[str],
                                missing_medications: List[str]) -> List[str]:
        """Generate actionable recommendations for missing data"""
        recommendations = []
        
        # Biomarker recommendations
        for biomarker in missing_biomarkers:
            if biomarker.lower() in self.biomarker_mappings:
                info = self.biomarker_mappings[biomarker.lower()]
                recommendations.append(
                    f"🔬 Order {info['test_name']} ({info['description']}) - "
                    f"Results in {info['time_to_result']}, Cost: {info['cost']}"
                )
        
        # Lab test recommendations
        for test in missing_lab_tests:
            if test.lower() in self.lab_test_mappings:
                info = self.lab_test_mappings[test.lower()]
                recommendations.append(
                    f"🩸 Order {info['test_name']} ({info['description']}) - "
                    f"Results in {info['time_to_result']}, Cost: {info['cost']}"
                )
        
        # Condition documentation recommendations
        for condition in missing_conditions:
            if condition.lower() in self.condition_mappings:
                info = self.condition_mappings[condition.lower()]
                recommendations.append(
                    f"📋 {info['documentation']} - "
                    f"Time to obtain: {info['time_to_obtain']}"
                )
        
        # Demographic recommendations
        for demo in missing_demographics:
            if demo.lower() == "age":
                recommendations.append("📋 Verify patient age from medical records")
            elif demo.lower() == "gender":
                recommendations.append("📋 Verify patient gender from medical records")
            else:
                recommendations.append(f"📋 Collect missing {demo} information")
        
        # Medication recommendations
        for med in missing_medications:
            recommendations.append(f"💊 Review medication history for {med}")
        
        return recommendations
    
    def _generate_priority_actions(self, missing_biomarkers: List[str],
                                 missing_lab_tests: List[str],
                                 missing_conditions: List[str],
                                 missing_demographics: List[str],
                                 missing_medications: List[str]) -> List[str]:
        """Generate prioritized action list based on urgency and impact"""
        priority_actions = []
        
        # High priority: Biomarkers (critical for trial eligibility)
        for biomarker in missing_biomarkers:
            if biomarker.lower() in self.biomarker_mappings:
                info = self.biomarker_mappings[biomarker.lower()]
                if info['urgency'] == 'high':
                    priority_actions.append(f"🚨 URGENT: Order {info['test_name']} immediately")
                else:
                    priority_actions.append(f"🔬 Order {info['test_name']} within 48 hours")
        
        # Medium priority: Critical conditions
        for condition in missing_conditions:
            if condition.lower() in self.condition_mappings:
                info = self.condition_mappings[condition.lower()]
                if info['urgency'] == 'high':
                    priority_actions.append(f"📋 PRIORITY: {info['documentation']}")
        
        # Low priority: Basic lab tests and demographics
        for test in missing_lab_tests:
            if test.lower() in self.lab_test_mappings:
                info = self.lab_test_mappings[test.lower()]
                priority_actions.append(f"🩸 Schedule {info['test_name']} at next visit")
        
        for demo in missing_demographics:
            priority_actions.append(f"📋 Update {demo} information in EMR")
        
        return priority_actions
    
    def _estimate_completion_time(self, missing_biomarkers: List[str],
                                missing_lab_tests: List[str],
                                missing_conditions: List[str],
                                missing_demographics: List[str],
                                missing_medications: List[str]) -> str:
        """Estimate time to complete all missing data collection"""
        max_time_days = 0
        
        # Biomarker tests (longest lead time)
        for biomarker in missing_biomarkers:
            if biomarker.lower() in self.biomarker_mappings:
                time_str = self.biomarker_mappings[biomarker.lower()]['time_to_result']
                if 'days' in time_str:
                    # Handle ranges like "5-7 days" by taking the maximum
                    time_parts = time_str.split()[0].split('-')
                    days = int(time_parts[-1])  # Take the last number (maximum)
                    max_time_days = max(max_time_days, days)
        
        # Lab tests
        for test in missing_lab_tests:
            if test.lower() in self.lab_test_mappings:
                time_str = self.lab_test_mappings[test.lower()]['time_to_result']
                if 'hours' in time_str:
                    hours = int(time_str.split()[0])
                    max_time_days = max(max_time_days, hours / 24)
        
        # Conditions
        for condition in missing_conditions:
            if condition.lower() in self.condition_mappings:
                time_str = self.condition_mappings[condition.lower()]['time_to_obtain']
                if 'days' in time_str:
                    # Handle ranges like "5-7 days" by taking the maximum
                    time_parts = time_str.split()[0].split('-')
                    days = int(time_parts[-1])  # Take the last number (maximum)
                    max_time_days = max(max_time_days, days)
        
        if max_time_days == 0:
            return "Immediate"
        elif max_time_days < 1:
            return "Same day"
        elif max_time_days < 2:
            return "1-2 days"
        elif max_time_days < 7:
            return "3-7 days"
        elif max_time_days < 14:
            return "1-2 weeks"
        else:
            return "2+ weeks"
    
    def _determine_confidence_level(self, coverage_percentage: float,
                                  missing_criteria: int,
                                  failed_criteria: int) -> str:
        """Determine confidence level in the match result"""
        if coverage_percentage >= 90 and missing_criteria == 0:
            return "Very High"
        elif coverage_percentage >= 80 and missing_criteria <= 1:
            return "High"
        elif coverage_percentage >= 70 and missing_criteria <= 2:
            return "Medium"
        elif coverage_percentage >= 60 and missing_criteria <= 3:
            return "Low"
        else:
            return "Very Low"
    
    def format_coverage_summary(self, report: CoverageReport) -> str:
        """Format coverage report as a concise summary string"""
        if report.total_criteria == 0:
            return "No criteria to evaluate"
        
        summary_parts = [
            f"{report.coverage_percentage:.1f}% coverage",
            f"({report.matched_criteria}/{report.total_criteria} criteria matched)"
        ]
        
        if report.missing_criteria > 0:
            summary_parts.append(f"{report.missing_criteria} missing")
        
        if report.failed_criteria > 0:
            summary_parts.append(f"{report.failed_criteria} failed")
        
        return " ".join(summary_parts)
    
    def get_missing_biomarkers_summary(self, report: CoverageReport) -> str:
        """Get a summary of missing biomarkers"""
        if not report.missing_biomarkers:
            return "All required biomarkers present"
        
        biomarker_list = ", ".join(report.missing_biomarkers)
        return f"Missing biomarkers: {biomarker_list}"
    
    def get_next_steps_summary(self, report: CoverageReport) -> str:
        """Get a summary of next steps"""
        if not report.priority_actions:
            return "No additional data needed"
        
        if len(report.priority_actions) == 1:
            return f"Next step: {report.priority_actions[0]}"
        else:
            return f"Next steps: {report.priority_actions[0]} and {len(report.priority_actions) - 1} more"

