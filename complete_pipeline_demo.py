"""
Complete Clinical Trials Analytics & AI Platform Pipeline Demo
Demonstrates all 8 steps of the pipeline with detailed explanations
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from src.main import ClinicalTrialsPlatform
from src.models.llm.patient_matcher import create_sample_patient_data, create_sample_trial_requirements
from src.models.nlp.biobert_finetuner import create_fine_tuning_demo

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

def demo_complete_pipeline():
    """
    Demonstrate the complete 8-step Clinical Trials Analytics Pipeline
    """
    print("🚀 CLINICAL TRIALS ANALYTICS & AI PLATFORM")
    print("Complete 8-Step Pipeline Demonstration")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize the platform
    platform = ClinicalTrialsPlatform()
    
    # Step 1: Data Ingestion
    print_step_header(1, "DATA INGESTION", 
                     "Collect clinical trial data from ClinicalTrials.gov API")
    print("Collecting trial data for multiple conditions...")
    trial_data = platform.collect_trial_data(["cancer", "oncology", "neurology"])
    print(f"✓ Collected {sum(len(trials) for trials in trial_data.values())} trials across {len(trial_data)} conditions")
    
    # Step 2-3: Preprocessing & Terminology Mining
    print_step_header(2, "PREPROCESSING & TERMINOLOGY MINING", 
                     "Extract and analyze medical terminologies from trial criteria using NLP")
    print("Extracting medical terminologies from inclusion/exclusion criteria...")
    terminology_results = platform.extract_terminologies()
    total_terms = sum(len(analysis['terminologies']) for analysis in terminology_results.values())
    print(f"✓ Extracted {total_terms} medical terminologies")
    
    # Step 4-5: EMR Representation Analysis & Alignment
    print_step_header(4, "EMR REPRESENTATION ANALYSIS & ALIGNMENT", 
                     "Map medical terminologies to FHIR resources and unstructured reports")
    print("Mapping terminologies to EMR structures...")
    emr_mappings = platform.map_to_emr()
    total_mappings = sum(len(mappings) for mappings in emr_mappings.values())
    print(f"✓ Created {total_mappings} EMR mappings")
    
    # Step 6: Analytics Dashboard
    print_step_header(6, "ANALYTICS DASHBOARD", 
                     "Generate comprehensive analytics and visualizations")
    print("Generating analytics and visualizations...")
    analytics_results = platform.generate_analytics()
    print(f"✓ Generated analytics for {len(analytics_results)} conditions")
    
    # Step 7: Patient-Trial Matching
    print_step_header(7, "PATIENT-TRIAL MATCHING", 
                     "Match patients to clinical trials using generative AI")
    print("Performing patient-trial matching...")
    matching_results = platform.perform_patient_matching()
    total_matches = sum(len(patient_results) for patient_results in matching_results.values())
    print(f"✓ Completed {total_matches} patient-trial matches")
    
    # Step 8: Final Integration & Reporting
    print_step_header(8, "FINAL INTEGRATION & REPORTING", 
                     "Generate comprehensive summary report with all findings")
    print("Generating final summary report...")
    summary = platform.generate_summary_report()
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
    
    return platform, summary

def demo_biobert_fine_tuning():
    """Demonstrate BioBERT fine-tuning capabilities"""
    print_step_header("OPTIONAL", "BIOBERT FINE-TUNING", 
                     "Demonstrate fine-tuning BioBERT for clinical trial terminology extraction")
    
    print("Initializing BioBERT fine-tuning demo...")
    fine_tuner = create_fine_tuning_demo()
    
    print("\n✓ BioBERT fine-tuning module ready")
    print("   • Custom entity labels for clinical trial terminology")
    print("   • Training data preparation utilities")
    print("   • Fine-tuning pipeline with evaluation")
    print("   • Inference capabilities for terminology extraction")
    
    return fine_tuner

def demo_patient_matching_detailed():
    """Demonstrate detailed patient-trial matching"""
    print_step_header("DETAILED", "PATIENT-TRIAL MATCHING", 
                     "Detailed demonstration of patient-trial matching with sample data")
    
    from src.models.llm.patient_matcher import PatientTrialMatcher, demo_patient_matching
    
    print("Running detailed patient-trial matching demo...")
    result = demo_patient_matching()
    
    print(f"\n📋 Sample Patient-Trial Match Results:")
    print(f"   • Trial: {result.trial_name}")
    print(f"   • Overall Score: {result.overall_score:.2f}")
    print(f"   • Confidence Level: {result.confidence_level}")
    
    print(f"\n📊 Category Scores:")
    for category, score in result.category_scores.items():
        print(f"   • {category.title()}: {score:.2f}")
    
    print(f"\n✅ Matched Indicators ({len(result.matched_indicators)}):")
    for indicator in result.matched_indicators[:3]:  # Show first 3
        print(f"   • {indicator}")
    
    print(f"\n❌ Missing Indicators ({len(result.missing_indicators)}):")
    for indicator in result.missing_indicators[:3]:  # Show first 3
        print(f"   • {indicator}")
    
    return result

def show_file_structure():
    """Show the complete project file structure"""
    print_step_header("INFO", "PROJECT STRUCTURE", 
                     "Complete file structure of the Clinical Trials Analytics Platform")
    
    structure = """
Ayusynapse/
├── 📁 src/                          # Main source code
│   ├── 📁 data/                     # Data collection and processing
│   │   └── 📁 collectors/           # Data collection modules
│   │       └── trial_collector.py   # ClinicalTrials.gov API integration
│   ├── 📁 models/                   # AI/ML models
│   │   ├── 📁 nlp/                  # Natural Language Processing
│   │   │   ├── terminology_extractor.py  # Medical terminology extraction
│   │   │   └── biobert_finetuner.py      # BioBERT fine-tuning module
│   │   ├── 📁 llm/                  # Large Language Models
│   │   │   ├── emr_mapper.py        # EMR mapping engine
│   │   │   └── patient_matcher.py   # Patient-trial matching
│   │   └── 📁 analytics/            # Analytics and visualization
│   │       └── dashboard.py         # Analytics dashboard generation
│   ├── 📁 api/                      # FastAPI web application
│   │   └── main.py                  # REST API endpoints
│   └── main.py                      # Main orchestration class
├── 📁 config/                       # Configuration files
│   └── settings.py                  # Centralized configuration
├── 📁 data/                         # Data storage
│   ├── 📁 raw/                      # Raw trial data
│   └── 📁 processed/                # Processed datasets
├── 📁 reports/                      # Generated reports and visualizations
├── 📁 notebooks/                    # Jupyter notebooks for analysis
├── 📄 requirements.txt              # Python dependencies
├── 📄 setup.py                      # Project setup script
├── 📄 demo.py                       # Basic demo script
├── 📄 complete_pipeline_demo.py     # Complete pipeline demonstration
├── 📄 README.md                     # Project documentation
├── 📄 QUICK_START.md               # Quick start guide
└── 📄 PROJECT_SUMMARY.md           # Detailed project summary
"""
    
    print(structure)

def show_pipeline_steps():
    """Show detailed explanation of each pipeline step"""
    print_step_header("INFO", "PIPELINE STEPS", 
                     "Detailed explanation of each step in the 8-step pipeline")
    
    steps = [
        {
            "step": 1,
            "title": "Data Ingestion",
            "description": "Collect clinical trial data from ClinicalTrials.gov API",
            "components": ["ClinicalTrialCollector", "API integration", "Data validation"],
            "output": "Raw trial data in JSON format"
        },
        {
            "step": 2,
            "title": "Preprocessing & Parsing",
            "description": "Extract inclusion/exclusion criteria and segment text",
            "components": ["Text preprocessing", "Criteria extraction", "Sentence segmentation"],
            "output": "Structured trial criteria data"
        },
        {
            "step": 3,
            "title": "Terminology Mining with LLM",
            "description": "Extract medical terminologies using NLP and LLMs",
            "components": ["BioBERT", "spaCy", "Rule-based extraction", "Frequency analysis"],
            "output": "Categorized medical terminologies with frequencies"
        },
        {
            "step": 4,
            "title": "EMR Representation Analysis",
            "description": "Analyze how terminologies appear in EMR systems",
            "components": ["FHIR mapping", "Report analysis", "Code mapping"],
            "output": "Terminology-to-EMR mappings"
        },
        {
            "step": 5,
            "title": "Terminology-EMR Alignment",
            "description": "Create structured mappings between terminologies and EMR",
            "components": ["JSON mapping creation", "Standard code mapping", "Example extraction"],
            "output": "Structured EMR mapping dictionaries"
        },
        {
            "step": 6,
            "title": "Analytics Dashboard",
            "description": "Generate comprehensive analytics and visualizations",
            "components": ["Plotly charts", "Frequency analysis", "Category distribution", "Heatmaps"],
            "output": "Interactive HTML dashboards and reports"
        },
        {
            "step": 7,
            "title": "Patient-Trial Matching",
            "description": "Match patients to clinical trials using generative AI",
            "components": ["LLM evaluation", "Confidence scoring", "Criteria matching"],
            "output": "Patient-trial matching scores and recommendations"
        },
        {
            "step": 8,
            "title": "Final Integration & Reporting",
            "description": "Generate comprehensive summary reports",
            "components": ["Report generation", "Data compilation", "Recommendations"],
            "output": "Comprehensive JSON reports and summaries"
        }
    ]
    
    for step in steps:
        print(f"\n📋 Step {step['step']}: {step['title']}")
        print(f"   Description: {step['description']}")
        print(f"   Components: {', '.join(step['components'])}")
        print(f"   Output: {step['output']}")

def main():
    """Main demonstration function"""
    print("🎯 CLINICAL TRIALS ANALYTICS & AI PLATFORM")
    print("Complete Pipeline Demonstration")
    print("=" * 80)
    
    try:
        # Show project structure
        show_file_structure()
        
        # Show pipeline steps
        show_pipeline_steps()
        
        # Run complete pipeline
        platform, summary = demo_complete_pipeline()
        
        # Demo BioBERT fine-tuning
        demo_biobert_fine_tuning()
        
        # Demo detailed patient matching
        demo_patient_matching_detailed()
        
        print(f"\n{'='*80}")
        print("🎉 PIPELINE DEMONSTRATION COMPLETE!")
        print(f"{'='*80}")
        print("✅ All 8 steps of the pipeline have been executed successfully")
        print("✅ Generated reports and visualizations are available in the 'reports' directory")
        print("✅ Processed data is stored in 'data/processed' directory")
        print("✅ Web API is available at http://localhost:8000")
        print("\n📚 Next Steps:")
        print("   1. Explore the generated reports in the 'reports' directory")
        print("   2. Check the web API at http://localhost:8000/docs")
        print("   3. Run Jupyter notebooks for interactive analysis")
        print("   4. Fine-tune BioBERT with your specific clinical trial data")
        print("   5. Integrate with real EMR systems for production use")
        
    except Exception as e:
        print(f"\n❌ Pipeline demonstration failed: {e}")
        logger.error(f"Pipeline demonstration failed: {e}", exc_info=True)

if __name__ == "__main__":
    main() 