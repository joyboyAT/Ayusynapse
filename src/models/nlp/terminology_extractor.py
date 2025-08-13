"""
Medical Terminology Extractor using BioBERT and medical NLP techniques.
Identifies and categorizes medical terminologies from clinical trial criteria.
"""

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import spacy
import re
from typing import List, Dict, Set, Tuple, Any
import pandas as pd
from collections import Counter, defaultdict
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

logger = logging.getLogger(__name__)

class MedicalTerminologyExtractor:
    """Extracts and categorizes medical terminologies from clinical trial text."""
    
    def __init__(self):
        """Initialize the medical terminology extractor with BioBERT and spaCy."""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize spaCy
        try:
            self.nlp = spacy.load("en_core_sci_sm")
        except OSError:
            logger.warning("en_core_sci_sm not found, using en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize BioBERT with error handling
        self.model = None
        self.tokenizer = None
        self.biobert_available = False
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-v1.1")
            self.model = AutoModelForTokenClassification.from_pretrained("dmis-lab/biobert-v1.1")
            self.model.to(self.device)
            self.biobert_available = True
            logger.info("BioBERT model loaded successfully")
        except Exception as e:
            logger.warning(f"BioBERT model failed to load: {e}. Using fallback mode.")
            self.biobert_available = False
        
        # Medical terminology patterns
        self.medical_patterns = {
            'demographics': [
                r'\b(?:age|years?|old|young|adult|pediatric)\b',
                r'\b(?:male|female|gender|sex)\b',
                r'\b(?:weight|height|bmi|body mass index)\b'
            ],
            'clinical': [
                r'\b(?:ECOG|performance status|ps)\b',
                r'\b(?:stage|grade|tumor grade)\b',
                r'\b(?:metastasis|metastatic|mets)\b',
                r'\b(?:symptoms?|symptomatic)\b'
            ],
            'biomarkers': [
                r'\b(?:EGFR|ALK|ROS1|BRAF|KRAS|TP53)\b',
                r'\b(?:mutation|positive|negative|wild type)\b',
                r'\b(?:biomarker|marker|expression)\b',
                r'\b(?:PD-L1|HER2|BRCA)\b'
            ],
            'pathology': [
                r'\b(?:adenocarcinoma|squamous|small cell|large cell)\b',
                r'\b(?:cancer|carcinoma|tumor|neoplasm)\b',
                r'\b(?:biopsy|pathology|histology)\b',
                r'\b(?:lymph node|lymphatic)\b'
            ],
            'treatments': [
                r'\b(?:chemotherapy|chemo|radiation|radiotherapy)\b',
                r'\b(?:surgery|surgical|resection)\b',
                r'\b(?:immunotherapy|targeted therapy)\b',
                r'\b(?:hormone therapy|endocrine therapy)\b'
            ]
        }
    
    def extract_terminologies(self, text: str) -> Dict[str, Any]:
        """
        Extract medical terminologies from text using multiple methods.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing extracted terminologies and analysis
        """
        if not isinstance(text, str):
            return {"terminologies": [], "frequency_analysis": {}, "categorized_terms": {}}
        
        # Preprocess text
        processed_text = self._preprocess_text(text)
        
        # Extract terms using different methods
        rule_based_terms = self._extract_rule_based_terms(processed_text)
        spacy_terms = self._extract_spacy_terms(processed_text)
        
        # Combine all terms
        all_terms = rule_based_terms + spacy_terms
        
        # Add BioBERT terms if available
        if self.biobert_available:
            try:
                biobert_terms = self._extract_biobert_terms(processed_text)
                all_terms.extend(biobert_terms)
            except Exception as e:
                logger.warning(f"BioBERT extraction failed: {e}")
        
        # Remove duplicates and clean
        unique_terms = list(set([term.lower() for term in all_terms if term.strip()]))
        
        # Categorize terms
        categorized_terms = self._categorize_terms(unique_terms)
        
        # Frequency analysis
        frequency_analysis = self._analyze_frequency(unique_terms)
        
        return {
            "terminologies": unique_terms,
            "frequency_analysis": frequency_analysis,
            "categorized_terms": categorized_terms
        }
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis."""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    def _extract_rule_based_terms(self, text: str) -> List[str]:
        """Extract terms using rule-based patterns."""
        terms = []
        for category, patterns in self.medical_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                terms.extend(matches)
        return terms
    
    def _extract_biobert_terms(self, text: str) -> List[str]:
        """Extract terms using BioBERT model."""
        if not self.biobert_available or not self.model or not self.tokenizer:
            return []
        
        try:
            # Tokenize text
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.argmax(outputs.logits, dim=2)
            
            # Extract tokens
            tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
            entities = []
            
            for token, pred in zip(tokens, predictions[0]):
                if pred.item() > 0 and token not in ['[CLS]', '[SEP]', '[PAD]']:
                    clean_token = token.replace('##', '')
                    if isinstance(clean_token, str) and len(clean_token) > 1:
                        entities.append(clean_token)
            
            return entities
        except Exception as e:
            logger.error(f"BioBERT extraction error: {e}")
            return []
    
    def _extract_spacy_terms(self, text: str) -> List[str]:
        """Extract terms using spaCy NER."""
        try:
            doc = self.nlp(text)
            entities = []
            
            for ent in doc.ents:
                if ent.label_ in ['DISEASE', 'CONDITION', 'CHEMICAL', 'PROCEDURE']:
                    entities.append(ent.text)
            
            return entities
        except Exception as e:
            logger.error(f"spaCy extraction error: {e}")
            return []
    
    def _categorize_terms(self, terms: List[str]) -> Dict[str, List[str]]:
        """Categorize terms into medical categories."""
        categorized = {
            'demographics': [],
            'clinical': [],
            'biomarkers': [],
            'pathology': [],
            'treatments': []
        }
        
        for term in terms:
            if not isinstance(term, str):
                continue
                
            term_lower = term.lower()
            
            # Check each category
            for category, patterns in self.medical_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, term_lower):
                        if term not in categorized[category]:
                            categorized[category].append(term)
                        break
        
        return categorized
    
    def _analyze_frequency(self, terms: List[str]) -> Dict[str, Any]:
        """Analyze frequency of terms."""
        if not terms:
            return {"term_frequencies": {}, "top_terms": []}
        
        counter = Counter(terms)
        sorted_terms = sorted(counter.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "term_frequencies": dict(counter),
            "top_terms": [term for term, _ in sorted_terms[:10]]
        }
    
    def analyze_trial_criteria(self, trial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze clinical trial criteria and extract key indicators."""
        all_terminologies = []
        
        for condition, trials in trial_data.items():
            for trial in trials:
                # Extract from inclusion criteria
                for criterion in trial.get('inclusion_criteria', []):
                    result = self.extract_terminologies(criterion)
                    all_terminologies.extend(result['terminologies'])
                
                # Extract from exclusion criteria
                for criterion in trial.get('exclusion_criteria', []):
                    result = self.extract_terminologies(criterion)
                    all_terminologies.extend(result['terminologies'])
        
        # Analyze overall frequency
        counter = Counter(all_terminologies)
        top_indicators = [term for term, _ in counter.most_common(20)]
        
        return {
            "total_terminologies": len(all_terminologies),
            "unique_terminologies": len(set(all_terminologies)),
            "top_indicators": top_indicators,
            "frequency_analysis": dict(counter)
        }
    
    def get_top_indicators(self, trial_data: Dict[str, Any], top_n: int = 5) -> Dict[str, List[str]]:
        """Get top indicators for each category."""
        analysis = self.analyze_trial_criteria(trial_data)
        
        # Categorize top indicators
        categorized_indicators = {
            'demographics': [],
            'clinical': [],
            'biomarkers': [],
            'pathology': [],
            'treatments': []
        }
        
        for indicator in analysis['top_indicators']:
            for category, patterns in self.medical_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, indicator.lower()):
                        if len(categorized_indicators[category]) < top_n:
                            categorized_indicators[category].append(indicator)
                        break
        
        return categorized_indicators


def main():
    """Demo function to test terminology extraction."""
    extractor = MedicalTerminologyExtractor()
    
    # Sample trial criteria
    sample_criteria = """
    Inclusion Criteria:
    - Age >= 18 years
    - ECOG performance status 0-2
    - Hemoglobin >= 10 g/dL
    - Platelets >= 100,000/μL
    - Creatinine <= 1.5 mg/dL
    - Bilirubin <= 1.5 mg/dL
    - ALT/AST <= 2.5 x ULN
    - HER2 positive breast cancer
    - Stage I-III disease
    
    Exclusion Criteria:
    - Pregnant or lactating women
    - History of heart disease
    - Diabetes mellitus
    - HIV positive
    - Active infection
    """
    
    # Extract terminologies
    terms = extractor.extract_terminologies(sample_criteria)
    
    print("Extracted Terminologies:")
    for category, term_list in terms.items():
        print(f"\n{category.upper()}:")
        for term in term_list:
            print(f"  - {term}")


if __name__ == "__main__":
    main() 