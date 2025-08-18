#!/usr/bin/env python3
"""
Explainability Module for Patient-Trial Matching
Generates human-readable explanations of matching results
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

try:
    from .engine import TrialMatchResult, MatchResult
    from .predicates import Predicate
except ImportError:
    from engine import TrialMatchResult, MatchResult
    from predicates import Predicate

logger = logging.getLogger(__name__)

@dataclass
class TrialExplanation:
    """Structured explanation of trial matching result"""
    trial_id: str
    eligible: bool
    score: float
    summary: str
    matched_facts: List[str]
    blockers: List[str]
    missing_data: List[str]
    recommendations: List[str]

class TrialExplainer:
    """Generates human-readable explanations of trial matching results"""
    
    def __init__(self):
        """Initialize the explainer"""
        pass
    
    def make_explanation(self, trial_id: str, result: TrialMatchResult) -> TrialExplanation:
        """
        Create a comprehensive explanation of trial matching result
        
        Args:
            trial_id: Trial identifier
            result: TrialMatchResult from matching engine
            
        Returns:
            TrialExplanation with structured explanation
        """
        # Generate summary
        summary = self._generate_summary(trial_id, result)
        
        # Extract matched facts
        matched_facts = self._extract_matched_facts(result.matched_inclusions)
        
        # Identify blockers
        blockers = self._identify_blockers(result)
        
        # Get missing data requests
        missing_data = result.suggested_data.copy()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(result)
        
        return TrialExplanation(
            trial_id=trial_id,
            eligible=result.eligible,
            score=result.score,
            summary=summary,
            matched_facts=matched_facts,
            blockers=blockers,
            missing_data=missing_data,
            recommendations=recommendations
        )
    
    def _generate_summary(self, trial_id: str, result: TrialMatchResult) -> str:
        """Generate a concise summary of the trial match result"""
        if result.eligible:
            if result.score >= 95:
                return f"✅ **Excellent Match** - Patient is highly eligible for {trial_id} (Score: {result.score:.1f}/100)"
            elif result.score >= 80:
                return f"✅ **Good Match** - Patient meets eligibility criteria for {trial_id} (Score: {result.score:.1f}/100)"
            else:
                return f"⚠️ **Marginal Match** - Patient barely meets criteria for {trial_id} (Score: {result.score:.1f}/100)"
        else:
            if result.exclusions_triggered:
                return f"❌ **Excluded** - Patient is ineligible for {trial_id} due to exclusion criteria"
            elif result.score < 50:
                return f"❌ **Poor Match** - Patient does not meet most criteria for {trial_id} (Score: {result.score:.1f}/100)"
            else:
                return f"❌ **Insufficient Match** - Patient needs additional data for {trial_id} (Score: {result.score:.1f}/100)"
    
    def _extract_matched_facts(self, matched_inclusions: List[MatchResult]) -> List[str]:
        """Extract human-readable facts from matched inclusion criteria"""
        facts = []
        
        for match in matched_inclusions:
            predicate = match.predicate
            evidence = match.evidence
            
            if predicate.type == "Patient":
                if predicate.field == "age":
                    facts.append(f"📋 **Age Requirement Met**: {evidence}")
                elif predicate.field == "gender":
                    facts.append(f"📋 **Gender Requirement Met**: {evidence}")
                else:
                    facts.append(f"📋 **Patient {predicate.field}**: {evidence}")
            
            elif predicate.type == "Condition":
                if predicate.code:
                    facts.append(f"🏥 **Condition Present**: {evidence}")
                else:
                    facts.append(f"🏥 **{predicate.field} Condition**: {evidence}")
            
            elif predicate.type == "Observation":
                if predicate.field:
                    facts.append(f"🔬 **{predicate.field} Test**: {evidence}")
                else:
                    facts.append(f"🔬 **Lab Test**: {evidence}")
            
            elif predicate.type == "Medication":
                if predicate.field:
                    facts.append(f"💊 **Medication History**: {evidence}")
                else:
                    facts.append(f"💊 **Medication**: {evidence}")
        
        return facts
    
    def _identify_blockers(self, result: TrialMatchResult) -> List[str]:
        """Identify factors that prevent eligibility"""
        blockers = []
        
        # Check exclusions first
        if result.exclusions_triggered:
            for exclusion in result.exclusions_triggered:
                predicate = exclusion.predicate
                evidence = exclusion.evidence
                
                if predicate.type == "Condition":
                    blockers.append(f"🚫 **Exclusion - Condition**: {predicate.reason or evidence}")
                elif predicate.type == "Medication":
                    blockers.append(f"🚫 **Exclusion - Medication**: {predicate.reason or evidence}")
                elif predicate.type == "Observation":
                    blockers.append(f"🚫 **Exclusion - Lab Result**: {predicate.reason or evidence}")
                else:
                    blockers.append(f"🚫 **Exclusion**: {predicate.reason or evidence}")
        
        # Check failed inclusion criteria
        for unmatched in result.unmatched_inclusions:
            predicate = unmatched.predicate
            evidence = unmatched.evidence
            
            # Determine severity based on weight
            severity = "Critical" if predicate.weight >= 5 else "Important" if predicate.weight >= 3 else "Standard"
            
            if predicate.type == "Patient":
                if predicate.field == "age":
                    blockers.append(f"❌ **{severity} - Age Requirement**: {evidence}")
                elif predicate.field == "gender":
                    blockers.append(f"❌ **{severity} - Gender Requirement**: {evidence}")
                else:
                    blockers.append(f"❌ **{severity} - Patient {predicate.field}**: {evidence}")
            
            elif predicate.type == "Condition":
                if predicate.code:
                    blockers.append(f"❌ **{severity} - Required Condition**: {evidence}")
                else:
                    blockers.append(f"❌ **{severity} - {predicate.field} Condition**: {evidence}")
            
            elif predicate.type == "Observation":
                if predicate.field:
                    blockers.append(f"❌ **{severity} - {predicate.field} Test**: {evidence}")
                else:
                    blockers.append(f"❌ **{severity} - Lab Test**: {evidence}")
            
            elif predicate.type == "Medication":
                if predicate.field:
                    blockers.append(f"❌ **{severity} - Medication Requirement**: {evidence}")
                else:
                    blockers.append(f"❌ **{severity} - Medication**: {evidence}")
        
        return blockers
    
    def _generate_recommendations(self, result: TrialMatchResult) -> List[str]:
        """Generate actionable recommendations based on the result"""
        recommendations = []
        
        if result.eligible:
            if result.score >= 95:
                recommendations.append("🎯 **Strong Recommendation**: Patient is an excellent candidate for this trial")
            elif result.score >= 80:
                recommendations.append("✅ **Recommended**: Patient meets eligibility criteria and should be considered")
            else:
                recommendations.append("⚠️ **Consider with Caution**: Patient barely meets criteria - monitor closely")
        else:
            if result.exclusions_triggered:
                recommendations.append("🚫 **Not Recommended**: Patient has exclusion criteria that cannot be overcome")
            elif result.score < 50:
                recommendations.append("❌ **Not Recommended**: Patient does not meet most criteria")
            else:
                recommendations.append("📋 **Data Collection Needed**: Gather missing information before reconsidering")
        
        # Add specific recommendations based on missing data
        if result.suggested_data:
            recommendations.append("📊 **Next Steps**: Order the following tests/information:")
            for data_request in result.suggested_data:
                recommendations.append(f"   • {data_request}")
        
        # Add recommendations for failed criteria
        if result.unmatched_inclusions:
            critical_failures = [u for u in result.unmatched_inclusions if u.predicate.weight >= 5]
            if critical_failures:
                recommendations.append("🔍 **Critical Issues**: Address these high-priority criteria:")
                for failure in critical_failures[:3]:  # Show top 3
                    predicate = failure.predicate
                    if predicate.type == "Observation":
                        recommendations.append(f"   • Ensure {predicate.field} meets requirement: {predicate.op} {predicate.value}")
                    elif predicate.type == "Condition":
                        recommendations.append(f"   • Verify {predicate.field or predicate.code} condition status")
        
        return recommendations
    
    def format_markdown(self, explanation: TrialExplanation) -> str:
        """Format explanation as markdown"""
        md = []
        
        # Header
        md.append(f"# Trial Match Explanation: {explanation.trial_id}")
        md.append("")
        
        # Summary
        md.append("## Summary")
        md.append(explanation.summary)
        md.append("")
        
        # Score
        md.append(f"**Match Score**: {explanation.score:.1f}/100")
        md.append("")
        
        # Matched Facts
        if explanation.matched_facts:
            md.append("## ✅ Matched Criteria")
            for fact in explanation.matched_facts:
                md.append(f"- {fact}")
            md.append("")
        
        # Blockers
        if explanation.blockers:
            md.append("## ❌ Blocking Factors")
            for blocker in explanation.blockers:
                md.append(f"- {blocker}")
            md.append("")
        
        # Missing Data
        if explanation.missing_data:
            md.append("## 📋 Missing Information")
            for data in explanation.missing_data:
                md.append(f"- {data}")
            md.append("")
        
        # Recommendations
        if explanation.recommendations:
            md.append("## 🎯 Recommendations")
            for rec in explanation.recommendations:
                md.append(f"- {rec}")
            md.append("")
        
        return "\n".join(md)
    
    def format_text(self, explanation: TrialExplanation) -> str:
        """Format explanation as plain text"""
        lines = []
        
        # Header
        lines.append(f"TRIAL MATCH EXPLANATION: {explanation.trial_id}")
        lines.append("=" * 60)
        lines.append("")
        
        # Summary
        lines.append("SUMMARY:")
        lines.append(explanation.summary)
        lines.append(f"Match Score: {explanation.score:.1f}/100")
        lines.append("")
        
        # Matched Facts
        if explanation.matched_facts:
            lines.append("MATCHED CRITERIA:")
            for fact in explanation.matched_facts:
                lines.append(f"  ✓ {fact}")
            lines.append("")
        
        # Blockers
        if explanation.blockers:
            lines.append("BLOCKING FACTORS:")
            for blocker in explanation.blockers:
                lines.append(f"  ✗ {blocker}")
            lines.append("")
        
        # Missing Data
        if explanation.missing_data:
            lines.append("MISSING INFORMATION:")
            for data in explanation.missing_data:
                lines.append(f"  ? {data}")
            lines.append("")
        
        # Recommendations
        if explanation.recommendations:
            lines.append("RECOMMENDATIONS:")
            for rec in explanation.recommendations:
                lines.append(f"  → {rec}")
            lines.append("")
        
        return "\n".join(lines)

def create_sample_explanation() -> TrialExplanation:
    """Create a sample explanation for testing"""
    # This would normally come from the matching engine
    # For testing, we'll create a mock explanation
    
    explanation = TrialExplanation(
        trial_id="NCT07062263",
        eligible=True,
        score=85.5,
        summary="✅ **Good Match** - Patient meets eligibility criteria for NCT07062263 (Score: 85.5/100)",
        matched_facts=[
            "📋 **Age Requirement Met**: age: 52.0 >= 18.0",
            "🏥 **Condition Present**: Condition with code 363418001 is present: Biliary tract cancer",
            "🔬 **HER2 Test**: HER2: positive equals positive",
            "🔬 **Hemoglobin Test**: Hemoglobin: 13.2 >= 10.0"
        ],
        blockers=[
            "❌ **Important - ECOG Test**: ECOG performance status assessment needed"
        ],
        missing_data=[
            "📊 Need ECOG performance status assessment"
        ],
        recommendations=[
            "✅ **Recommended**: Patient meets eligibility criteria and should be considered",
            "📊 **Next Steps**: Order the following tests/information:",
            "   • 📊 Need ECOG performance status assessment"
        ]
    )
    
    return explanation

def test_explainer():
    """Test the explainer with sample data"""
    print("🧪 Testing Trial Explainer")
    print("=" * 50)
    
    explainer = TrialExplainer()
    
    # Create sample explanation
    explanation = create_sample_explanation()
    
    print("📋 Sample Trial Match Explanation")
    print("-" * 40)
    print(f"Trial ID: {explanation.trial_id}")
    print(f"Eligible: {explanation.eligible}")
    print(f"Score: {explanation.score:.1f}/100")
    print(f"Summary: {explanation.summary}")
    print()
    
    print("✅ Matched Facts:")
    for fact in explanation.matched_facts:
        print(f"  {fact}")
    print()
    
    print("❌ Blockers:")
    for blocker in explanation.blockers:
        print(f"  {blocker}")
    print()
    
    print("📋 Missing Data:")
    for data in explanation.missing_data:
        print(f"  {data}")
    print()
    
    print("🎯 Recommendations:")
    for rec in explanation.recommendations:
        print(f"  {rec}")
    print()
    
    # Test markdown formatting
    print("📄 Markdown Format:")
    print("-" * 20)
    markdown = explainer.format_markdown(explanation)
    print(markdown)
    print()
    
    # Test text formatting
    print("📄 Text Format:")
    print("-" * 20)
    text = explainer.format_text(explanation)
    print(text)
    
    print("\n✅ Explainer test completed!")

if __name__ == "__main__":
    test_explainer()
