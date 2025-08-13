"""
Analytics Dashboard for Clinical Trials
Provides comprehensive analytics and visualization for clinical trial data.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from typing import List, Dict, Optional, Tuple
import json
from collections import Counter, defaultdict
import logging

logger = logging.getLogger(__name__)

class ClinicalTrialAnalytics:
    """Analytics engine for clinical trial data analysis."""
    
    def __init__(self):
        """Initialize the analytics engine."""
        self.color_palette = {
            'oncology': '#FF6B6B',
            'neurology': '#4ECDC4',
            'demographics': '#45B7D1',
            'clinical': '#96CEB4',
            'laboratory': '#FFEAA7',
            'pathology': '#DDA0DD',
            'imaging': '#98D8C8',
            'medications': '#F7DC6F'
        }
    
    def analyze_terminology_frequency(self, analysis_results: Dict) -> Dict:
        """
        Analyze terminology frequency across trials.
        
        Args:
            analysis_results: Results from terminology extraction
            
        Returns:
            Dictionary with frequency analysis
        """
        frequency_analysis = {
            'total_trials': analysis_results.get('total_trials', 0),
            'category_stats': {},
            'top_terminologies': {},
            'coverage_metrics': {}
        }
        
        # Analyze each category
        for category, counter in analysis_results.get('category_frequencies', {}).items():
            total_occurrences = sum(counter.values())
            unique_terms = len(counter)
            
            frequency_analysis['category_stats'][category] = {
                'total_occurrences': total_occurrences,
                'unique_terms': unique_terms,
                'avg_occurrences_per_trial': total_occurrences / analysis_results.get('total_trials', 1),
                'top_5_terms': counter.most_common(5)
            }
        
        # Overall top terminologies
        all_terms = Counter()
        for counter in analysis_results.get('category_frequencies', {}).values():
            all_terms.update(counter)
        
        frequency_analysis['top_terminologies']['overall'] = all_terms.most_common(20)
        
        # Coverage analysis
        total_trials = analysis_results.get('total_trials', 0)
        for category, counter in analysis_results.get('category_frequencies', {}).items():
            coverage = len([term for term, count in counter.items() if count > 0])
            frequency_analysis['coverage_metrics'][category] = {
                'trials_with_terms': coverage,
                'coverage_percentage': (coverage / total_trials * 100) if total_trials > 0 else 0
            }
        
        return frequency_analysis
    
    def create_terminology_frequency_chart(self, analysis_results: Dict) -> go.Figure:
        """
        Create a bar chart showing terminology frequency.
        
        Args:
            analysis_results: Results from terminology extraction
            
        Returns:
            Plotly figure object
        """
        # Get top 10 overall terminologies
        all_terms = Counter()
        for counter in analysis_results.get('category_frequencies', {}).values():
            all_terms.update(counter)
        
        top_terms = all_terms.most_common(10)
        terms, frequencies = zip(*top_terms) if top_terms else ([], [])
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(terms),
                y=list(frequencies),
                marker_color='#4ECDC4',
                text=list(frequencies),
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title='Top 10 Most Frequent Medical Terminologies',
            xaxis_title='Terminology',
            yaxis_title='Frequency',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def create_category_distribution_chart(self, analysis_results: Dict) -> go.Figure:
        """
        Create a pie chart showing distribution across categories.
        
        Args:
            analysis_results: Results from terminology extraction
            
        Returns:
            Plotly figure object
        """
        category_counts = {}
        for category, counter in analysis_results.get('category_frequencies', {}).items():
            category_counts[category] = sum(counter.values())
        
        fig = go.Figure(data=[
            go.Pie(
                labels=list(category_counts.keys()),
                values=list(category_counts.values()),
                hole=0.3,
                marker_colors=list(self.color_palette.values())[:len(category_counts)]
            )
        ])
        
        fig.update_layout(
            title='Distribution of Terminologies Across Categories',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def create_heatmap_chart(self, analysis_results: Dict) -> go.Figure:
        """
        Create a heatmap showing terminology frequency by category.
        
        Args:
            analysis_results: Results from terminology extraction
            
        Returns:
            Plotly figure object
        """
        # Prepare data for heatmap
        categories = list(analysis_results.get('category_frequencies', {}).keys())
        all_terms = set()
        for counter in analysis_results.get('category_frequencies', {}).values():
            all_terms.update(counter.keys())
        
        # Get top 15 terms for heatmap
        all_terms_counter = Counter()
        for counter in analysis_results.get('category_frequencies', {}).values():
            all_terms_counter.update(counter)
        
        top_terms = [term for term, _ in all_terms_counter.most_common(15)]
        
        # Create matrix
        matrix = []
        for category in categories:
            row = []
            counter = analysis_results.get('category_frequencies', {}).get(category, Counter())
            for term in top_terms:
                row.append(counter.get(term, 0))
            matrix.append(row)
        
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=top_terms,
            y=categories,
            colorscale='Viridis',
            text=matrix,
            texttemplate="%{text}",
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title='Terminology Frequency Heatmap by Category',
            xaxis_title='Terminology',
            yaxis_title='Category',
            template='plotly_white',
            height=600
        )
        
        return fig
    
    def create_trial_coverage_chart(self, analysis_results: Dict) -> go.Figure:
        """
        Create a chart showing trial coverage by terminology category.
        
        Args:
            analysis_results: Results from terminology extraction
            
        Returns:
            Plotly figure object
        """
        total_trials = analysis_results.get('total_trials', 0)
        categories = []
        coverage_percentages = []
        
        for category, counter in analysis_results.get('category_frequencies', {}).items():
            categories.append(category)
            trials_with_terms = len([term for term, count in counter.items() if count > 0])
            coverage_percentage = (trials_with_terms / total_trials * 100) if total_trials > 0 else 0
            coverage_percentages.append(coverage_percentage)
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=coverage_percentages,
                marker_color='#FF6B6B',
                text=[f'{p:.1f}%' for p in coverage_percentages],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title='Trial Coverage by Terminology Category',
            xaxis_title='Category',
            yaxis_title='Coverage Percentage',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def create_comprehensive_dashboard(self, analysis_results: Dict) -> go.Figure:
        """
        Create a comprehensive dashboard with multiple charts.
        
        Args:
            analysis_results: Results from terminology extraction
            
        Returns:
            Plotly figure object with subplots
        """
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Top Terminologies',
                'Category Distribution',
                'Trial Coverage',
                'Terminology Heatmap'
            ),
            specs=[
                [{"type": "bar"}, {"type": "pie"}],
                [{"type": "bar"}, {"type": "heatmap"}]
            ]
        )
        
        # Add charts
        # 1. Top terminologies
        all_terms = Counter()
        for counter in analysis_results.get('category_frequencies', {}).values():
            all_terms.update(counter)
        
        top_terms = all_terms.most_common(8)
        if top_terms:
            terms, frequencies = zip(*top_terms)
            fig.add_trace(
                go.Bar(x=list(terms), y=list(frequencies), name="Top Terms"),
                row=1, col=1
            )
        
        # 2. Category distribution
        category_counts = {}
        for category, counter in analysis_results.get('category_frequencies', {}).items():
            category_counts[category] = sum(counter.values())
        
        if category_counts:
            fig.add_trace(
                go.Pie(
                    labels=list(category_counts.keys()),
                    values=list(category_counts.values()),
                    name="Categories"
                ),
                row=1, col=2
            )
        
        # 3. Trial coverage
        total_trials = analysis_results.get('total_trials', 0)
        categories = []
        coverage_percentages = []
        
        for category, counter in analysis_results.get('category_frequencies', {}).items():
            categories.append(category)
            trials_with_terms = len([term for term, count in counter.items() if count > 0])
            coverage_percentage = (trials_with_terms / total_trials * 100) if total_trials > 0 else 0
            coverage_percentages.append(coverage_percentage)
        
        if categories:
            fig.add_trace(
                go.Bar(x=categories, y=coverage_percentages, name="Coverage"),
                row=2, col=1
            )
        
        # 4. Heatmap
        top_terms_for_heatmap = [term for term, _ in all_terms.most_common(10)]
        categories_for_heatmap = list(analysis_results.get('category_frequencies', {}).keys())
        
        matrix = []
        for category in categories_for_heatmap:
            row = []
            counter = analysis_results.get('category_frequencies', {}).get(category, Counter())
            for term in top_terms_for_heatmap:
                row.append(counter.get(term, 0))
            matrix.append(row)
        
        if matrix and top_terms_for_heatmap and categories_for_heatmap:
            fig.add_trace(
                go.Heatmap(
                    z=matrix,
                    x=top_terms_for_heatmap,
                    y=categories_for_heatmap,
                    colorscale='Viridis',
                    name="Heatmap"
                ),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title='Clinical Trials Analytics Dashboard',
            template='plotly_white',
            height=800,
            showlegend=False
        )
        
        return fig
    
    def generate_analytics_report(self, analysis_results: Dict) -> Dict:
        """
        Generate a comprehensive analytics report.
        
        Args:
            analysis_results: Results from terminology extraction
            
        Returns:
            Dictionary with comprehensive analytics
        """
        frequency_analysis = self.analyze_terminology_frequency(analysis_results)
        
        report = {
            'summary': {
                'total_trials': analysis_results.get('total_trials', 0),
                'total_terminologies': sum(len(counter) for counter in analysis_results.get('category_frequencies', {}).values()),
                'categories_analyzed': len(analysis_results.get('category_frequencies', {})),
                'most_frequent_category': max(
                    analysis_results.get('category_frequencies', {}).items(),
                    key=lambda x: sum(x[1].values())
                )[0] if analysis_results.get('category_frequencies') else None
            },
            'frequency_analysis': frequency_analysis,
            'top_indicators': {},
            'recommendations': []
        }
        
        # Get top indicators for each category
        for category, counter in analysis_results.get('category_frequencies', {}).items():
            report['top_indicators'][category] = counter.most_common(5)
        
        # Generate recommendations
        total_trials = analysis_results.get('total_trials', 0)
        if total_trials > 0:
            # Coverage recommendations
            for category, metrics in frequency_analysis['coverage_metrics'].items():
                if metrics['coverage_percentage'] < 50:
                    report['recommendations'].append(
                        f"Low coverage in {category} category ({metrics['coverage_percentage']:.1f}%). "
                        f"Consider expanding data collection for this category."
                    )
            
            # Frequency recommendations
            for category, stats in frequency_analysis['category_stats'].items():
                if stats['avg_occurrences_per_trial'] < 2:
                    report['recommendations'].append(
                        f"Low terminology density in {category} category. "
                        f"Consider standardizing terminology usage."
                    )
        
        return report


def main():
    """Demo function to test analytics."""
    analytics = ClinicalTrialAnalytics()
    
    # Sample analysis results
    sample_results = {
        'total_trials': 100,
        'category_frequencies': {
            'demographics': Counter({'age': 85, 'gender': 90, 'bmi': 45}),
            'clinical': Counter({'ecog': 75, 'performance status': 60, 'vital signs': 40}),
            'laboratory': Counter({'hemoglobin': 80, 'platelets': 70, 'creatinine': 65}),
            'pathology': Counter({'her2': 30, 'er': 25, 'pr': 25})
        }
    }
    
    # Generate charts
    frequency_chart = analytics.create_terminology_frequency_chart(sample_results)
    category_chart = analytics.create_category_distribution_chart(sample_results)
    coverage_chart = analytics.create_trial_coverage_chart(sample_results)
    heatmap_chart = analytics.create_heatmap_chart(sample_results)
    
    # Generate report
    report = analytics.generate_analytics_report(sample_results)
    
    print("Analytics Report Generated:")
    print(f"Total Trials: {report['summary']['total_trials']}")
    print(f"Total Terminologies: {report['summary']['total_terminologies']}")
    print(f"Most Frequent Category: {report['summary']['most_frequent_category']}")
    
    print("\nTop Indicators:")
    for category, indicators in report['top_indicators'].items():
        print(f"\n{category.upper()}:")
        for term, count in indicators:
            print(f"  - {term}: {count}")


if __name__ == "__main__":
    main() 