#!/usr/bin/env python3
"""
Synthetic Clinical Report Generator for NER Training
Generates synthetic clinical reports with disease entities and BIO labeling
"""

import random
import json
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class ClinicalEntity:
    """Clinical entity with its type and modifiers"""
    text: str
    entity_type: str
    modifiers: List[str] = None
    
    def __post_init__(self):
        if self.modifiers is None:
            self.modifiers = []

class SyntheticReportGenerator:
    """Generate synthetic clinical reports with NER annotations"""
    
    def __init__(self):
        # Disease categories
        self.neurology_diseases = [
            "Glioblastoma", "Epilepsy", "Parkinson's disease", "Multiple sclerosis",
            "Alzheimer's disease", "Huntington's disease", "Amyotrophic lateral sclerosis",
            "Meningioma", "Astrocytoma", "Oligodendroglioma", "Medulloblastoma",
            "Neurofibromatosis", "Tuberous sclerosis", "Sturge-Weber syndrome"
        ]
        
        self.oncology_diseases = [
            "Breast Cancer", "Lung Carcinoma", "Leukemia", "Lymphoma", "Melanoma",
            "Colon Cancer", "Prostate Cancer", "Ovarian Cancer", "Pancreatic Cancer",
            "Liver Cancer", "Kidney Cancer", "Bladder Cancer", "Thyroid Cancer",
            "Bone Cancer", "Brain Cancer", "Stomach Cancer", "Esophageal Cancer"
        ]
        
        self.cardiovascular_diseases = [
            "Coronary artery disease", "Heart failure", "Hypertension", "Arrhythmia",
            "Atrial fibrillation", "Myocardial infarction", "Cardiomyopathy",
            "Valvular heart disease", "Pericarditis", "Endocarditis"
        ]
        
        # Modifiers
        self.severity_modifiers = [
            "mild", "moderate", "severe", "critical", "acute", "chronic",
            "progressive", "stable", "worsening", "improving"
        ]
        
        self.stage_modifiers = [
            "stage I", "stage II", "stage III", "stage IV", "early stage",
            "advanced stage", "metastatic", "localized", "regional"
        ]
        
        self.temporal_modifiers = [
            "recurrent", "relapsed", "newly diagnosed", "long-standing",
            "recent", "persistent", "intermittent", "episodic"
        ]
        
        # Clinical contexts
        self.clinical_contexts = [
            "The patient was diagnosed with {disease}.",
            "Clinical examination revealed {disease}.",
            "The patient presents with {disease}.",
            "Medical history shows {disease}.",
            "Laboratory results indicate {disease}.",
            "Imaging studies confirm {disease}.",
            "The patient has been treated for {disease}.",
            "Family history is positive for {disease}."
        ]
        
        # Additional clinical information
        self.additional_info = [
            "The condition has been stable for the past 6 months.",
            "Patient reports improvement in symptoms.",
            "No significant changes in clinical status.",
            "Treatment response has been favorable.",
            "Patient is currently asymptomatic.",
            "Regular monitoring is recommended.",
            "Follow-up appointment scheduled.",
            "Patient is compliant with treatment regimen."
        ]
        
        # Entity type mapping
        self.entity_types = {
            'neurology': 'DiseaseClass',
            'oncology': 'DiseaseClass', 
            'cardiovascular': 'DiseaseClass',
            'severity': 'Modifier',
            'stage': 'Modifier',
            'temporal': 'Modifier'
        }
    
    def tokenize_text(self, text: str) -> List[str]:
        """Tokenize text into words while preserving punctuation"""
        # Split on whitespace but keep punctuation attached
        tokens = re.findall(r'\S+', text)
        return tokens
    
    def clean_tokenize_text(self, text: str) -> List[str]:
        """Tokenize text and clean punctuation for matching"""
        # Remove punctuation for matching
        cleaned_text = re.sub(r'[^\w\s]', '', text)
        tokens = cleaned_text.split()
        return tokens
    
    def create_bio_labels(self, tokens: List[str], entities: List[ClinicalEntity]) -> List[str]:
        """Create BIO labels for tokens based on entities"""
        labels = ['O'] * len(tokens)
        
        # Join tokens back to text for easier matching
        text = " ".join(tokens)
        
        for entity in entities:
            # Find entity in the text
            start_pos = text.find(entity.text)
            if start_pos != -1:
                # Count tokens up to the start position
                token_count = 0
                char_count = 0
                entity_start_token = 0
                
                for i, token in enumerate(tokens):
                    if char_count <= start_pos < char_count + len(token) + 1:  # +1 for space
                        entity_start_token = i
                        break
                    char_count += len(token) + 1  # +1 for space
                
                # Count tokens in the entity
                entity_tokens = self.tokenize_text(entity.text)
                entity_end_token = entity_start_token + len(entity_tokens)
                
                # Apply BIO labels
                if entity_start_token < len(labels):
                    labels[entity_start_token] = f"B-{entity.entity_type}"
                    for i in range(entity_start_token + 1, min(entity_end_token, len(labels))):
                        labels[i] = f"I-{entity.entity_type}"
        
        return labels
    
    def generate_entity(self) -> ClinicalEntity:
        """Generate a random clinical entity with modifiers"""
        # Choose disease category
        category = random.choice(['neurology', 'oncology', 'cardiovascular'])
        
        if category == 'neurology':
            disease = random.choice(self.neurology_diseases)
        elif category == 'oncology':
            disease = random.choice(self.oncology_diseases)
        else:
            disease = random.choice(self.cardiovascular_diseases)
        
        # Add modifiers
        modifiers = []
        if random.random() < 0.7:  # 70% chance of severity modifier
            modifiers.append(random.choice(self.severity_modifiers))
        
        if random.random() < 0.5:  # 50% chance of stage modifier
            modifiers.append(random.choice(self.stage_modifiers))
        
        if random.random() < 0.4:  # 40% chance of temporal modifier
            modifiers.append(random.choice(self.temporal_modifiers))
        
        # Combine disease and modifiers
        full_text = disease
        if modifiers:
            full_text = " ".join(modifiers + [disease])
        
        return ClinicalEntity(
            text=full_text,
            entity_type=self.entity_types[category],
            modifiers=modifiers
        )
    
    def find_entity_in_tokens(self, tokens: List[str], entity_text: str) -> List[int]:
        """Find the token indices for an entity in the tokenized text"""
        # Clean tokens for matching (remove punctuation)
        clean_tokens = []
        for token in tokens:
            clean_token = re.sub(r'[^\w\s]', '', token)
            if clean_token:
                clean_tokens.append(clean_token)
        
        # Clean entity text for matching
        entity_tokens = self.clean_tokenize_text(entity_text)
        entity_indices = []
        
        for i in range(len(clean_tokens)):
            if i + len(entity_tokens) <= len(clean_tokens):
                if clean_tokens[i:i+len(entity_tokens)] == entity_tokens:
                    # Map back to original token indices
                    entity_indices = list(range(i, i + len(entity_tokens)))
                    break
        
        return entity_indices
    
    def generate_report(self) -> Dict:
        """Generate a single clinical report with NER annotations"""
        # Generate 1-2 entities for this report
        num_entities = random.randint(1, 2)
        entities = [self.generate_entity() for _ in range(num_entities)]
        
        # Create report text
        report_sentences = []
        
        # Add entity-containing sentences
        for entity in entities:
            context = random.choice(self.clinical_contexts)
            sentence = context.format(disease=entity.text)
            report_sentences.append(sentence)
        
        # Add additional clinical information
        if random.random() < 0.8:  # 80% chance of additional info
            report_sentences.append(random.choice(self.additional_info))
        
        # Combine into full report
        report_text = " ".join(report_sentences)
        
        # Tokenize
        tokens = self.tokenize_text(report_text)
        
        # Create BIO labels
        labels = self.create_bio_labels(tokens, entities)
        
        return {
            "text": report_text,
            "tokens": tokens,
            "labels": labels,
            "entities": [
                {
                    "text": entity.text,
                    "entity_type": entity.entity_type,
                    "modifiers": entity.modifiers
                }
                for entity in entities
            ]
        }
    
    def generate_dataset(self, num_reports: int = 15) -> List[Dict]:
        """Generate a dataset of synthetic reports"""
        dataset = []
        
        for i in range(num_reports):
            report = self.generate_report()
            report['id'] = f"report_{i+1:03d}"
            dataset.append(report)
        
        return dataset
    
    def save_jsonl(self, dataset: List[Dict], filename: str = "synthetic_reports.jsonl"):
        """Save dataset in JSONL format"""
        with open(filename, 'w', encoding='utf-8') as f:
            for report in dataset:
                f.write(json.dumps(report, ensure_ascii=False) + '\n')
        
        print(f"✅ Saved {len(dataset)} reports to {filename}")
    
    def save_json(self, dataset: List[Dict], filename: str = "synthetic_reports.json"):
        """Save dataset in JSON format"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "dataset": dataset,
                "metadata": {
                    "num_reports": len(dataset),
                    "entity_types": list(set(self.entity_types.values())),
                    "disease_categories": ["neurology", "oncology", "cardiovascular"]
                }
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(dataset)} reports to {filename}")
    
    def print_sample_report(self, report: Dict):
        """Print a sample report with token-label alignment"""
        print(f"\n📋 Report ID: {report['id']}")
        print(f"📄 Text: {report['text']}")
        print(f"🏷️  Entities: {len(report['entities'])}")
        
        for entity in report['entities']:
            print(f"   • {entity['text']} ({entity['entity_type']})")
        
        print("\n🔤 Token-Label Alignment:")
        print("Token".ljust(15) + "Label")
        print("-" * 30)
        
        for token, label in zip(report['tokens'], report['labels']):
            print(f"{token.ljust(15)} {label}")

def test_dataset_loading():
    """Test loading the generated dataset into HuggingFace format"""
    try:
        from datasets import Dataset
        
        # Load JSONL file
        dataset = Dataset.from_json("synthetic_reports.jsonl")
        
        print(f"\n✅ Successfully loaded dataset into HuggingFace format!")
        print(f"📊 Dataset info:")
        print(f"   • Number of examples: {len(dataset)}")
        print(f"   • Features: {list(dataset.features.keys())}")
        print(f"   • Sample features: {dataset.features}")
        
        # Show first example
        print(f"\n📋 First example:")
        first_example = dataset[0]
        print(f"   • ID: {first_example['id']}")
        print(f"   • Text: {first_example['text']}")
        print(f"   • Tokens: {first_example['tokens'][:10]}...")
        print(f"   • Labels: {first_example['labels'][:10]}...")
        
        return True
        
    except ImportError:
        print("⚠️  HuggingFace datasets not installed. Skipping dataset loading test.")
        return False
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return False

def main():
    """Main function to generate synthetic reports"""
    print("🧪 Synthetic Clinical Report Generator")
    print("=" * 50)
    
    # Initialize generator
    generator = SyntheticReportGenerator()
    
    # Generate dataset
    print("📝 Generating synthetic reports...")
    dataset = generator.generate_dataset(num_reports=15)
    
    # Print sample reports
    print(f"\n📊 Generated {len(dataset)} reports")
    print("\n" + "=" * 50)
    
    # Show first 3 reports
    for i in range(min(3, len(dataset))):
        generator.print_sample_report(dataset[i])
        print()
    
    # Save in multiple formats
    print("💾 Saving dataset...")
    generator.save_jsonl(dataset, "synthetic_reports.jsonl")
    generator.save_json(dataset, "synthetic_reports.json")
    
    # Test HuggingFace loading
    print("\n🧪 Testing HuggingFace dataset loading...")
    test_dataset_loading()
    
    # Summary statistics
    print(f"\n📈 Dataset Statistics:")
    print(f"   • Total reports: {len(dataset)}")
    
    # Count entity types
    entity_counts = {}
    for report in dataset:
        for entity in report['entities']:
            entity_type = entity['entity_type']
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
    
    print(f"   • Entity types: {entity_counts}")
    
    # Count BIO labels
    label_counts = {}
    for report in dataset:
        for label in report['labels']:
            label_counts[label] = label_counts.get(label, 0) + 1
    
    print(f"   • BIO labels: {label_counts}")
    
    print(f"\n🎉 Synthetic report generation completed successfully!")

if __name__ == "__main__":
    main()
