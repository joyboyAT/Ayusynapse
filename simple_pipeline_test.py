"""
Simple Pipeline Test - Demonstrates the complete pipeline without heavy dependencies
"""

import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_step_header(step_number: int, title: str, description: str):
    """Print formatted step header"""
    print(f"\n{'='*80}")
    print(f"STEP {step_number}: {title}")
    print(f"{'='*80}")
    print(f"Description: {description}")
    print(f"{'='*80}")

def create_mock_trial_data():
    """Create mock trial data for demonstration"""
    return {
        "cancer": [
            {
                "nct_id": "NCT123456",
                "title": "Phase II Study of EGFR Inhibitor in Lung Cancer",
                "inclusion_criteria": [
                    "Age 18-75 years",
                    "ECOG performance status 0-1",
                    "EGFR mutation positive",
                    "Stage IIIB or IV non-small cell lung cancer"
                ],
                "exclusion_criteria": [
                    "Prior EGFR inhibitor therapy",
                    "Active brain metastases",
                    "Severe cardiac disease"
                ]
            },
            {
                "nct_id": "NCT789012",
                "title": "ALK Inhibitor Trial for Advanced NSCLC",
                "inclusion_criteria": [
                    "ALK rearrangement positive",
                    "ECOG performance status 0-2",
                    "Age 18-80 years",
                    "Measurable disease"
                ],
                "exclusion_criteria": [
                    "Prior ALK inhibitor treatment",
                    "Uncontrolled diabetes",
                    "Pregnancy"
                ]
            }
        ],
        "neurology": [
            {
                "nct_id": "NCT345678",
                "title": "Alzheimer's Disease Biomarker Study",
                "inclusion_criteria": [
                    "Age 50-85 years",
                    "MMSE score 20-26",
                    "Amyloid PET positive",
                    "No significant cognitive impairment"
                ],
                "exclusion_criteria": [
                    "Other neurological disorders",
                    "Severe depression",
                    "Recent stroke"
                ]
            }
        ]
    }

def extract_terminologies_mock(trial_data):
    """Mock terminology extraction"""
    print("Extracting medical terminologies...")
    
    all_terms = []
    for condition, trials in trial_data.items():
        for trial in trials:
            # Extract terms from inclusion criteria
            for criteria in trial.get('inclusion_criteria', []):
                terms = criteria.split()
                all_terms.extend([term for term in terms if len(term) > 3])
    
    # Count frequencies
    term_freq = {}
    for term in all_terms:
        term_freq[term] = term_freq.get(term, 0) + 1
    
    # Get top terms
    top_terms = sorted(term_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "terminologies": all_terms,
        "frequency_analysis": {
            "term_frequencies": term_freq,
            "top_terms": [term for term, freq in top_terms]
        },
        "categorized_terms": {
            "demographics": ["Age", "years"],
            "clinical": ["ECOG", "performance", "status"],
            "biomarkers": ["EGFR", "ALK", "mutation", "positive"],
            "pathology": ["cancer", "disease", "metastases"]
        }
    }

def map_to_emr_mock(terminology_results):
    """Mock EMR mapping"""
    print("Mapping terminologies to EMR structures...")
    
    mappings = {}
    for condition, analysis in terminology_results.items():
        top_terms = analysis['frequency_analysis']['top_terms'][:5]
        condition_mappings = {}
        
        for term in top_terms:
            fhir_mapping = {
                "resource_type": "Observation",
                "code": {
                    "system": "http://loinc.org",
                    "code": f"LOINC_{term.upper()}",
                    "display": term
                },
                "value": "string"
            }
            
            report_mapping = {
                "report_types": ["pathology", "lab", "radiology"],
                "example_mentions": [
                    f"{term} was observed in the specimen",
                    f"Patient shows {term} characteristics",
                    f"{term} levels are within normal range"
                ]
            }
            
            condition_mappings[term] = {
                "fhir_mapping": fhir_mapping,
                "report_mapping": report_mapping,
                "frequency": analysis['frequency_analysis']['term_frequencies'].get(term, 0)
            }
        
        mappings[condition] = condition_mappings
    
    return mappings

def generate_analytics_mock(terminology_results, trial_data):
    """Mock analytics generation"""
    print("Generating analytics and visualizations...")
    
    analytics = {}
    for condition, analysis in terminology_results.items():
        analytics[condition] = {
            "total_trials": len(trial_data[condition]),
            "total_terminologies": len(analysis['terminologies']),
            "top_terms": analysis['frequency_analysis']['top_terms'][:5],
            "category_distribution": {
                "demographics": len(analysis['categorized_terms']['demographics']),
                "clinical": len(analysis['categorized_terms']['clinical']),
                "biomarkers": len(analysis['categorized_terms']['biomarkers']),
                "pathology": len(analysis['categorized_terms']['pathology'])
            }
        }
    
    return analytics

def patient_matching_mock(trial_data):
    """Mock patient-trial matching"""
    print("Performing patient-trial matching...")
    
    # Mock patient data
    patient = {
        "demographics": {"age": 45, "gender": "female"},
        "clinical_data": {"ecog_status": 1, "tumor_grade": 2},
        "lab_results": {"egfr_mutation": "positive"},
        "pathology_reports": ["Adenocarcinoma, EGFR positive"],
        "medications": ["metformin"],
        "comorbidities": ["diabetes"]
    }
    
    matching_results = {}
    
    for condition, trials in trial_data.items():
        for trial in trials[:2]:  # Test with first 2 trials
            # Simple matching logic
            score = 0.7  # Mock score
            confidence = "HIGH" if score > 0.6 else "MEDIUM"
            
            matching_results[trial['nct_id']] = {
                "trial_name": trial['title'],
                "overall_score": score,
                "confidence_level": confidence,
                "category_scores": {
                    "demographics": 0.8,
                    "clinical": 0.7,
                    "biomarkers": 0.9,
                    "exclusion": 0.6
                },
                "matched_indicators": ["EGFR positive", "ECOG 1"],
                "missing_indicators": ["ALK negative"]
            }
    
    return matching_results

def generate_summary_report(trial_data, terminology_results, emr_mappings, analytics, matching_results):
    """Generate comprehensive summary report"""
    print("Generating comprehensive summary report...")
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "pipeline_steps_completed": [
            "Data Ingestion",
            "Preprocessing & Parsing", 
            "Terminology Mining with LLM",
            "EMR Representation Analysis",
            "Terminology-EMR Alignment",
            "Analytics Dashboard",
            "Patient-Trial Matching",
            "Final Integration & Reporting"
        ],
        "data_summary": {
            "total_trials_collected": sum(len(trials) for trials in trial_data.values()),
            "conditions_analyzed": list(trial_data.keys()),
            "terminologies_extracted": sum(len(analysis['terminologies']) for analysis in terminology_results.values()),
            "emr_mappings_created": sum(len(mappings) for mappings in emr_mappings.values()),
            "patients_matched": len(matching_results)
        },
        "key_findings": {
            "top_terminologies": {},
            "matching_statistics": {}
        },
        "recommendations": [
            "Consider fine-tuning BioBERT for better terminology extraction",
            "Expand trial collection to include more diverse conditions",
            "Implement real-time patient matching API",
            "Add more sophisticated EMR mapping algorithms"
        ]
    }
    
    # Extract key findings
    for condition, analysis in terminology_results.items():
        top_terms = analysis['frequency_analysis']['top_terms'][:5]
        summary['key_findings']['top_terminologies'][condition] = top_terms
    
    # Calculate matching statistics
    total_matches = len(matching_results)
    high_confidence_matches = len([r for r in matching_results.values() if r['confidence_level'] == 'HIGH'])
    
    summary['key_findings']['matching_statistics'] = {
        'total_matches': total_matches,
        'high_confidence_matches': high_confidence_matches,
        'match_rate': high_confidence_matches / total_matches if total_matches > 0 else 0
    }
    
    return summary

def run_complete_pipeline():
    """Run the complete 8-step pipeline with mock data"""
    print("🚀 CLINICAL TRIALS ANALYTICS & AI PLATFORM")
    print("Complete 8-Step Pipeline Demonstration (Mock Data)")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Step 1: Data Ingestion
        print_step_header(1, "DATA INGESTION", 
                         "Collect clinical trial data from ClinicalTrials.gov API")
        print("Collecting trial data for multiple conditions...")
        trial_data = create_mock_trial_data()
        print(f"✓ Collected {sum(len(trials) for trials in trial_data.values())} trials across {len(trial_data)} conditions")
        
        # Step 2-3: Preprocessing & Terminology Mining
        print_step_header(2, "PREPROCESSING & TERMINOLOGY MINING", 
                         "Extract and analyze medical terminologies from trial criteria using NLP")
        print("Extracting medical terminologies from inclusion/exclusion criteria...")
        terminology_results = {}
        for condition, trials in trial_data.items():
            terminology_results[condition] = extract_terminologies_mock({condition: trials})
        total_terms = sum(len(analysis['terminologies']) for analysis in terminology_results.values())
        print(f"✓ Extracted {total_terms} medical terminologies")
        
        # Step 4-5: EMR Representation Analysis & Alignment
        print_step_header(4, "EMR REPRESENTATION ANALYSIS & ALIGNMENT", 
                         "Map medical terminologies to FHIR resources and unstructured reports")
        print("Mapping terminologies to EMR structures...")
        emr_mappings = map_to_emr_mock(terminology_results)
        total_mappings = sum(len(mappings) for mappings in emr_mappings.values())
        print(f"✓ Created {total_mappings} EMR mappings")
        
        # Step 6: Analytics Dashboard
        print_step_header(6, "ANALYTICS DASHBOARD", 
                         "Generate comprehensive analytics and visualizations")
        print("Generating analytics and visualizations...")
        analytics = generate_analytics_mock(terminology_results, trial_data)
        print(f"✓ Generated analytics for {len(analytics)} conditions")
        
        # Step 7: Patient-Trial Matching
        print_step_header(7, "PATIENT-TRIAL MATCHING", 
                         "Match patients to clinical trials using generative AI")
        print("Performing patient-trial matching...")
        matching_results = patient_matching_mock(trial_data)
        total_matches = len(matching_results)
        print(f"✓ Completed {total_matches} patient-trial matches")
        
        # Step 8: Final Integration & Reporting
        print_step_header(8, "FINAL INTEGRATION & REPORTING", 
                         "Generate comprehensive summary report with all findings")
        print("Generating final summary report...")
        summary = generate_summary_report(trial_data, terminology_results, emr_mappings, analytics, matching_results)
        print(f"✓ Generated comprehensive summary report")
        
        # Display Results Summary
        print(f"\n{'='*80}")
        print("PIPELINE EXECUTION SUMMARY")
        print(f"{'='*80}")
        
        data_summary = summary['data_summary']
        print(f"📊 Data Summary:")
        print(f"   • Total Trials Collected: {data_summary['total_trials_collected']}")
        print(f"   • Conditions Analyzed: {', '.join(data_summary['conditions_analyzed'])}")
        print(f"   • Terminologies Extracted: {data_summary['terminologies_extracted']}")
        print(f"   • EMR Mappings Created: {data_summary['emr_mappings_created']}")
        print(f"   • Patients Matched: {data_summary['patients_matched']}")
        
        print(f"\n🔍 Key Findings:")
        for condition, terms in summary['key_findings']['top_terminologies'].items():
            print(f"   • {condition.title()}: {', '.join(terms[:3])}")
        
        matching_stats = summary['key_findings']['matching_statistics']
        print(f"\n🎯 Matching Statistics:")
        print(f"   • Total Matches: {matching_stats['total_matches']}")
        print(f"   • High Confidence Matches: {matching_stats['high_confidence_matches']}")
        print(f"   • Match Rate: {matching_stats['match_rate']:.2%}")
        
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(summary['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        # Save results to files
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "pipeline_results.json", 'w') as f:
            json.dump({
                "trial_data": trial_data,
                "terminology_results": terminology_results,
                "emr_mappings": emr_mappings,
                "analytics": analytics,
                "matching_results": matching_results,
                "summary": summary
            }, f, indent=2, default=str)
        
        print(f"\n✅ Pipeline completed successfully!")
        print(f"✅ Results saved to: {output_dir / 'pipeline_results.json'}")
        print(f"✅ Web API ready at: http://localhost:8000")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline execution failed: {e}")
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    run_complete_pipeline() 