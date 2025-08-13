"""
Clinical Trials Analytics & AI Platform - Main Orchestration
Complete pipeline implementation for clinical trial analysis and patient matching
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.data.collectors.trial_collector import ClinicalTrialCollector
from src.models.nlp.terminology_extractor import MedicalTerminologyExtractor
from src.models.llm.emr_mapper import EMRMappingEngine
from src.models.llm.patient_matcher import PatientTrialMatcher, PatientEMR, TrialRequirements
from src.models.analytics.dashboard import ClinicalTrialAnalytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ClinicalTrialsPlatform:
    """
    Main orchestration class for the Clinical Trials Analytics & AI Platform
    Implements the complete 8-step pipeline:
    1. Data Ingestion
    2. Preprocessing & Parsing
    3. Terminology Mining with LLM
    4. EMR Representation Analysis
    5. Terminology-EMR Alignment
    6. Analytics Dashboard
    7. Generative AI for Clinical Trial–Patient Matching
    8. Final Integration & Reporting
    """
    
    def __init__(self, output_dir: str = "data/processed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.trial_collector = ClinicalTrialCollector()
        self.terminology_extractor = MedicalTerminologyExtractor()
        self.emr_mapper = EMRMappingEngine()
        self.patient_matcher = PatientTrialMatcher()
        self.analytics = ClinicalTrialAnalytics()
        
        # Data storage
        self.trial_data = {}
        self.terminology_analysis = {}
        self.emr_mappings = {}
        self.patient_matching_results = {}
        
    def collect_trial_data(self, conditions: List[str] = None) -> Dict[str, Any]:
        """
        Step 1: Data Ingestion
        Collect clinical trial data from ClinicalTrials.gov
        """
        logger.info("Step 1: Data Ingestion - Collecting clinical trial data")
        
        if conditions is None:
            conditions = ["cancer", "oncology", "neurology", "alzheimer", "parkinson"]
        
        all_trials = {}
        
        for condition in conditions:
            try:
                trials = self.trial_collector.search_trials_by_condition(condition, max_results=10)
                all_trials[condition] = trials
                logger.info(f"Collected {len(trials)} trials for condition: {condition}")
            except Exception as e:
                logger.error(f"Error collecting trials for {condition}: {e}")
        
        self.trial_data = all_trials
        
        # Save raw trial data
        output_file = self.output_dir / "raw_trial_data.json"
        with open(output_file, 'w') as f:
            json.dump(all_trials, f, indent=2, default=str)
        
        logger.info(f"Saved raw trial data to {output_file}")
        return all_trials
    
    def extract_terminologies(self) -> Dict[str, Any]:
        """
        Step 2 & 3: Preprocessing & Parsing + Terminology Mining with LLM
        Extract and analyze medical terminologies from trial criteria
        """
        logger.info("Step 2 & 3: Preprocessing & Terminology Mining")
        
        terminology_results = {}
        
        for condition, trials in self.trial_data.items():
            logger.info(f"Processing terminologies for {condition} trials")
            
            # Extract inclusion/exclusion criteria
            all_criteria = []
            for trial in trials:
                if 'inclusion_criteria' in trial:
                    all_criteria.extend(trial['inclusion_criteria'])
                if 'exclusion_criteria' in trial:
                    all_criteria.extend(trial['exclusion_criteria'])
            
            # Extract terminologies
            terminologies = self.terminology_extractor.extract_terminologies(all_criteria)
            
            # Analyze frequency
            frequency_analysis = self.terminology_extractor.analyze_frequency(terminologies)
            
            terminology_results[condition] = {
                'terminologies': terminologies,
                'frequency_analysis': frequency_analysis,
                'categorized_terms': self.terminology_extractor.categorize_terms(terminologies)
            }
        
        self.terminology_analysis = terminology_results
        
        # Save terminology analysis
        output_file = self.output_dir / "terminology_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(terminology_results, f, indent=2, default=str)
        
        logger.info(f"Saved terminology analysis to {output_file}")
        return terminology_results
    
    def map_to_emr(self) -> Dict[str, Any]:
        """
        Step 4 & 5: EMR Representation Analysis + Terminology-EMR Alignment
        Map medical terminologies to FHIR resources and unstructured reports
        """
        logger.info("Step 4 & 5: EMR Representation Analysis & Alignment")
        
        emr_mappings = {}
        
        for condition, analysis in self.terminology_analysis.items():
            logger.info(f"Mapping terminologies to EMR for {condition}")
            
            top_terminologies = analysis['frequency_analysis']['top_terms'][:5]
            mappings = {}
            
            for term in top_terminologies:
                # Map to FHIR resources
                fhir_mapping = self.emr_mapper.map_terminology_to_fhir(term)
                
                # Map to unstructured reports
                report_mapping = self.emr_mapper.map_terminology_to_reports(term)
                
                mappings[term] = {
                    'fhir_mapping': fhir_mapping,
                    'report_mapping': report_mapping,
                    'frequency': analysis['frequency_analysis']['term_frequencies'].get(term, 0)
                }
            
            emr_mappings[condition] = mappings
        
        self.emr_mappings = emr_mappings
        
        # Save EMR mappings
        output_file = self.output_dir / "emr_mappings.json"
        with open(output_file, 'w') as f:
            json.dump(emr_mappings, f, indent=2, default=str)
        
        logger.info(f"Saved EMR mappings to {output_file}")
        return emr_mappings
    
    def generate_analytics(self) -> Dict[str, Any]:
        """
        Step 6: Analytics Dashboard
        Generate comprehensive analytics and visualizations
        """
        logger.info("Step 6: Analytics Dashboard Generation")
        
        analytics_results = {}
        
        for condition, analysis in self.terminology_analysis.items():
            logger.info(f"Generating analytics for {condition}")
            
            # Generate various charts
            frequency_chart = self.analytics.create_terminology_frequency_chart(
                analysis['frequency_analysis'], condition
            )
            
            distribution_chart = self.analytics.create_category_distribution_chart(
                analysis['categorized_terms'], condition
            )
            
            heatmap_chart = self.analytics.create_heatmap_chart(
                analysis['frequency_analysis'], condition
            )
            
            coverage_chart = self.analytics.create_trial_coverage_chart(
                self.trial_data[condition], condition
            )
            
            # Create comprehensive dashboard
            dashboard = self.analytics.create_comprehensive_dashboard(
                analysis, self.trial_data[condition], condition
            )
            
            analytics_results[condition] = {
                'frequency_chart': frequency_chart,
                'distribution_chart': distribution_chart,
                'heatmap_chart': heatmap_chart,
                'coverage_chart': coverage_chart,
                'dashboard': dashboard
            }
        
        # Generate overall analytics report
        overall_report = self.analytics.generate_analytics_report(
            self.terminology_analysis, self.trial_data
        )
        
        analytics_results['overall_report'] = overall_report
        
        # Save analytics results
        output_file = self.output_dir / "analytics_results.json"
        with open(output_file, 'w') as f:
            json.dump(analytics_results, f, indent=2, default=str)
        
        logger.info(f"Saved analytics results to {output_file}")
        return analytics_results
    
    def perform_patient_matching(self, sample_patients: List[PatientEMR] = None) -> Dict[str, Any]:
        """
        Step 7: Generative AI for Clinical Trial–Patient Matching
        Match patients to clinical trials using LLM-based evaluation
        """
        logger.info("Step 7: Patient-Trial Matching")
        
        if sample_patients is None:
            # Create sample patients for demonstration
            sample_patients = [
                PatientEMR(
                    demographics={'age': 45, 'gender': 'female', 'race': 'caucasian'},
                    clinical_data={'ecog_status': 1, 'tumor_grade': 2, 'metastases': ['lung']},
                    lab_results={'egfr_mutation': 'positive', 'alk_rearrangement': 'negative'},
                    pathology_reports=["Adenocarcinoma, EGFR positive"],
                    radiology_reports=["3cm mass in right upper lobe"],
                    medications=['metformin'],
                    comorbidities=['diabetes']
                ),
                PatientEMR(
                    demographics={'age': 65, 'gender': 'male', 'race': 'african_american'},
                    clinical_data={'ecog_status': 0, 'tumor_grade': 1, 'metastases': []},
                    lab_results={'egfr_mutation': 'negative', 'alk_rearrangement': 'positive'},
                    pathology_reports=["Squamous cell carcinoma"],
                    radiology_reports=["2cm mass in left lower lobe"],
                    medications=['aspirin'],
                    comorbidities=['hypertension']
                )
            ]
        
        matching_results = {}
        
        for i, patient in enumerate(sample_patients):
            logger.info(f"Matching patient {i+1} to trials")
            
            patient_results = {}
            
            # Convert trial data to TrialRequirements format
            for condition, trials in self.trial_data.items():
                for trial in trials[:3]:  # Test with first 3 trials per condition
                    try:
                        # Create TrialRequirements object
                        trial_req = TrialRequirements(
                            trial_id=trial.get('nct_id', f'trial_{i}'),
                            trial_name=trial.get('title', 'Unknown Trial'),
                            inclusion_criteria=trial.get('inclusion_criteria', []),
                            exclusion_criteria=trial.get('exclusion_criteria', []),
                            required_indicators=self._extract_trial_requirements(trial),
                            disease_area=condition
                        )
                        
                        # Perform matching
                        match_result = self.patient_matcher.match_patient_to_trial(patient, trial_req)
                        patient_results[trial_req.trial_id] = match_result
                        
                    except Exception as e:
                        logger.error(f"Error matching patient to trial {trial.get('nct_id', 'unknown')}: {e}")
            
            matching_results[f'patient_{i+1}'] = patient_results
        
        self.patient_matching_results = matching_results
        
        # Save matching results
        output_file = self.output_dir / "patient_matching_results.json"
        with open(output_file, 'w') as f:
            json.dump(matching_results, f, indent=2, default=str)
        
        logger.info(f"Saved patient matching results to {output_file}")
        return matching_results
    
    def _extract_trial_requirements(self, trial: Dict) -> Dict[str, Any]:
        """Extract structured requirements from trial data"""
        requirements = {
            'demographics': {'age_range': (18, 75), 'gender': 'any'},
            'clinical': {'ecog_status': 2, 'tumor_grade': 3},
            'biomarkers': {'egfr_mutation': 'any', 'alk_rearrangement': 'any'},
            'exclusion_medications': [],
            'exclusion_comorbidities': []
        }
        
        # Parse inclusion/exclusion criteria to extract requirements
        criteria_text = ' '.join(trial.get('inclusion_criteria', []) + trial.get('exclusion_criteria', []))
        
        # Simple rule-based extraction (in practice, use more sophisticated NLP)
        if 'age' in criteria_text.lower():
            if '18' in criteria_text and '75' in criteria_text:
                requirements['demographics']['age_range'] = (18, 75)
        
        if 'ecog' in criteria_text.lower():
            if '0-1' in criteria_text:
                requirements['clinical']['ecog_status'] = 1
            elif '0-2' in criteria_text:
                requirements['clinical']['ecog_status'] = 2
        
        return requirements
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """
        Step 8: Final Integration & Reporting
        Generate comprehensive summary report with all findings
        """
        logger.info("Step 8: Final Integration & Reporting")
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'pipeline_steps_completed': [
                'Data Ingestion',
                'Preprocessing & Parsing', 
                'Terminology Mining with LLM',
                'EMR Representation Analysis',
                'Terminology-EMR Alignment',
                'Analytics Dashboard',
                'Patient-Trial Matching',
                'Final Integration & Reporting'
            ],
            'data_summary': {
                'total_trials_collected': sum(len(trials) for trials in self.trial_data.values()),
                'conditions_analyzed': list(self.trial_data.keys()),
                'terminologies_extracted': sum(len(analysis['terminologies']) for analysis in self.terminology_analysis.values()),
                'emr_mappings_created': sum(len(mappings) for mappings in self.emr_mappings.values()),
                'patients_matched': len(self.patient_matching_results)
            },
            'key_findings': {
                'top_terminologies': {},
                'most_common_categories': {},
                'matching_statistics': {}
            },
            'recommendations': [
                "Consider fine-tuning BioBERT for better terminology extraction",
                "Expand trial collection to include more diverse conditions",
                "Implement real-time patient matching API",
                "Add more sophisticated EMR mapping algorithms"
            ]
        }
        
        # Extract key findings
        for condition, analysis in self.terminology_analysis.items():
            top_terms = analysis['frequency_analysis']['top_terms'][:5]
            summary['key_findings']['top_terminologies'][condition] = top_terms
        
        # Calculate matching statistics
        total_matches = 0
        high_confidence_matches = 0
        
        for patient_results in self.patient_matching_results.values():
            for match_result in patient_results.values():
                total_matches += 1
                if match_result.confidence_level == 'HIGH':
                    high_confidence_matches += 1
        
        summary['key_findings']['matching_statistics'] = {
            'total_matches': total_matches,
            'high_confidence_matches': high_confidence_matches,
            'match_rate': high_confidence_matches / total_matches if total_matches > 0 else 0
        }
        
        # Save summary report
        output_file = self.output_dir / "pipeline_summary_report.json"
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Saved pipeline summary report to {output_file}")
        return summary
    
    def run_complete_analysis(self, conditions: List[str] = None) -> Dict[str, Any]:
        """
        Run the complete 8-step pipeline
        """
        logger.info("Starting complete Clinical Trials Analytics Pipeline")
        
        try:
            # Step 1: Data Ingestion
            self.collect_trial_data(conditions)
            
            # Step 2-3: Terminology Extraction
            self.extract_terminologies()
            
            # Step 4-5: EMR Mapping
            self.map_to_emr()
            
            # Step 6: Analytics Generation
            self.generate_analytics()
            
            # Step 7: Patient Matching
            self.perform_patient_matching()
            
            # Step 8: Final Reporting
            summary = self.generate_summary_report()
            
            logger.info("Complete pipeline execution successful!")
            return {
                'status': 'success',
                'summary': summary,
                'output_files': list(self.output_dir.glob('*.json'))
            }
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

def main():
    """Main execution function"""
    platform = ClinicalTrialsPlatform()
    
    # Run complete analysis
    results = platform.run_complete_analysis()
    
    if results['status'] == 'success':
        print("\n=== Pipeline Execution Complete ===")
        print(f"Summary: {results['summary']['data_summary']}")
        print(f"Output files: {len(results['output_files'])} files generated")
        print("\nKey Findings:")
        for condition, terms in results['summary']['key_findings']['top_terminologies'].items():
            print(f"  {condition}: {terms[:3]}")
    else:
        print(f"Pipeline failed: {results['error']}")

if __name__ == "__main__":
    main() 