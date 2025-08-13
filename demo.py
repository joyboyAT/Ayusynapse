#!/usr/bin/env python3
"""
Demo script for Clinical Trials Analytics & AI Platform
Shows the complete pipeline from data collection to analytics.
"""

import os
import sys
import json
from datetime import datetime

# Add src to path
sys.path.append('src')

from src.main import ClinicalTrialsPlatform

def main():
    """Run the complete demo pipeline."""
    print("🚀 Clinical Trials Analytics & AI Platform Demo")
    print("=" * 60)
    
    # Initialize platform
    print("\n1. Initializing platform...")
    platform = ClinicalTrialsPlatform()
    print("✅ Platform initialized successfully")
    
    # Step 1: Collect trial data (using sample data for demo)
    print("\n2. Collecting clinical trial data...")
    
    # Create sample trial data for demo
    sample_trials = {
        'oncology': [
            {
                'nct_id': 'NCT12345678',
                'title': 'Study of Novel Therapy in Breast Cancer',
                'conditions': ['Breast Cancer', 'Metastatic Breast Cancer'],
                'inclusion_criteria': 'Age >= 18 years, ECOG performance status 0-2, Hemoglobin >= 10 g/dL, HER2 positive',
                'exclusion_criteria': 'Pregnant women, History of heart disease, Active infection',
                'study_type': 'Interventional',
                'phase': 'Phase 2',
                'enrollment': '100',
                'sponsor': 'Sample Pharma Inc.'
            },
            {
                'nct_id': 'NCT87654321',
                'title': 'Lung Cancer Treatment Study',
                'conditions': ['Lung Cancer', 'Non-Small Cell Lung Cancer'],
                'inclusion_criteria': 'Age >= 18 years, ECOG 0-1, Platelets >= 100,000/μL, EGFR mutation positive',
                'exclusion_criteria': 'Diabetes mellitus, HIV positive, Previous chemotherapy',
                'study_type': 'Interventional',
                'phase': 'Phase 3',
                'enrollment': '200',
                'sponsor': 'Research Institute'
            }
        ],
        'neurology': [
            {
                'nct_id': 'NCT11111111',
                'title': 'Alzheimer Disease Treatment Trial',
                'conditions': ['Alzheimer Disease', 'Dementia'],
                'inclusion_criteria': 'Age 65-85 years, MMSE score 10-26, Amyloid PET positive',
                'exclusion_criteria': 'Severe depression, Stroke within 6 months, Active cancer',
                'study_type': 'Interventional',
                'phase': 'Phase 2',
                'enrollment': '150',
                'sponsor': 'Neurology Research Center'
            }
        ]
    }
    
    # Save sample data
    os.makedirs('data/raw', exist_ok=True)
    with open('data/raw/oncology_trials.json', 'w') as f:
        json.dump(sample_trials['oncology'], f, indent=2)
    with open('data/raw/neurology_trials.json', 'w') as f:
        json.dump(sample_trials['neurology'], f, indent=2)
    
    print(f"✅ Created sample data: {len(sample_trials['oncology'])} oncology trials, {len(sample_trials['neurology'])} neurology trials")
    
    # Step 2: Extract terminologies
    print("\n3. Extracting medical terminologies...")
    analysis_results = platform.extract_terminologies(sample_trials)
    print("✅ Terminology extraction completed")
    
    # Display results
    for specialty, analysis in analysis_results.items():
        if specialty.endswith('_top_indicators'):
            continue
        
        print(f"\n📊 {specialty.upper()} Analysis Results:")
        print(f"  - Total trials: {analysis.get('total_trials', 0)}")
        
        category_frequencies = analysis.get('category_frequencies', {})
        for category, counter in category_frequencies.items():
            total_terms = sum(counter.values())
            unique_terms = len(counter)
            print(f"  - {category.title()}: {total_terms} occurrences, {unique_terms} unique terms")
    
    # Step 3: Map to EMR
    print("\n4. Mapping terminologies to EMR structures...")
    mapping_results = platform.map_to_emr(analysis_results)
    print("✅ EMR mapping completed")
    
    # Display mapping results
    for specialty, specialty_mappings in mapping_results.items():
        print(f"\n🗺️ {specialty.upper()} EMR Mappings:")
        
        for category, category_mappings in specialty_mappings.items():
            print(f"  {category.title()}:")
            
            for terminology, mapping_info in category_mappings.items():
                frequency = mapping_info.get('frequency', 0)
                fhir_mappings = mapping_info.get('fhir_mappings', [])
                report_mappings = mapping_info.get('report_mappings', [])
                
                print(f"    - {terminology} (frequency: {frequency}):")
                print(f"      * FHIR mappings: {len(fhir_mappings)}")
                print(f"      * Report mappings: {len(report_mappings)}")
    
    # Step 4: Generate analytics
    print("\n5. Generating analytics and visualizations...")
    analytics_results = platform.generate_analytics(analysis_results)
    print("✅ Analytics generation completed")
    
    # Display analytics summary
    for specialty, results in analytics_results.items():
        report = results.get('report', {})
        summary = report.get('summary', {})
        
        print(f"\n📈 {specialty.upper()} Analytics Summary:")
        print(f"  - Total trials: {summary.get('total_trials', 0)}")
        print(f"  - Total terminologies: {summary.get('total_terminologies', 0)}")
        print(f"  - Categories analyzed: {summary.get('categories_analyzed', 0)}")
        print(f"  - Most frequent category: {summary.get('most_frequent_category', 'N/A')}")
    
    # Step 5: Generate final report
    print("\n6. Generating comprehensive report...")
    
    final_results = {
        'timestamp': datetime.now().isoformat(),
        'trials_data': {
            'oncology_count': len(sample_trials['oncology']),
            'neurology_count': len(sample_trials['neurology'])
        },
        'analysis_results': analysis_results,
        'mapping_results': mapping_results,
        'analytics_results': analytics_results
    }
    
    summary = platform.generate_summary_report(final_results)
    print("\n" + "=" * 60)
    print("📋 COMPREHENSIVE ANALYSIS REPORT")
    print("=" * 60)
    print(summary)
    
    # Save final results
    os.makedirs('data/processed', exist_ok=True)
    with open('data/processed/final_analysis_results.json', 'w') as f:
        json.dump(final_results, f, indent=2, default=str)
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed successfully!")
    print("\n📁 Generated files:")
    print("  - data/raw/oncology_trials.json")
    print("  - data/raw/neurology_trials.json")
    print("  - data/processed/terminology_analysis.json")
    print("  - data/processed/emr_mappings.json")
    print("  - data/processed/analytics_results.json")
    print("  - data/processed/final_analysis_results.json")
    print("  - reports/ (HTML visualizations)")
    
    print("\n🚀 Next steps:")
    print("1. Run the web API: uvicorn src.api.main:app --reload")
    print("2. Open Jupyter notebooks: jupyter notebook notebooks/")
    print("3. View reports in the reports/ directory")
    print("4. Set OPENAI_API_KEY for full LLM functionality")

if __name__ == "__main__":
    main() 