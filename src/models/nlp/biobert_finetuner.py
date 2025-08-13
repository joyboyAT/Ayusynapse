"""
BioBERT Fine-tuning Module for Clinical Trial Terminology Extraction
"""

import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer, 
    AutoModelForTokenClassification,
    TrainingArguments, 
    Trainer,
    DataCollatorForTokenClassification
)
from datasets import Dataset
import numpy as np
from typing import List, Dict, Tuple, Optional
import json
import os
from sklearn.model_selection import train_test_split
import logging

logger = logging.getLogger(__name__)

class BioBERTFineTuner:
    """
    Fine-tune BioBERT for clinical trial terminology extraction
    """
    
    def __init__(self, model_name: str = "dmis-lab/biobert-base-cased-v1.2"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.label2id = {
            'O': 0,
            'B-DEMOGRAPHIC': 1,
            'I-DEMOGRAPHIC': 2,
            'B-CLINICAL': 3,
            'I-CLINICAL': 4,
            'B-PATHOLOGY': 5,
            'I-PATHOLOGY': 6,
            'B-BIOMARKER': 7,
            'I-BIOMARKER': 8,
            'B-MEDICATION': 9,
            'I-MEDICATION': 10,
            'B-ELIGIBILITY': 11,
            'I-ELIGIBILITY': 12
        }
        self.id2label = {v: k for k, v in self.label2id.items()}
        
    def prepare_training_data(self, clinical_texts: List[str], 
                            annotations: List[List[Tuple[str, str, str]]]) -> Dataset:
        """
        Prepare training data for fine-tuning
        
        Args:
            clinical_texts: List of clinical trial texts
            annotations: List of annotations [(start, end, label), ...]
        """
        tokenized_data = []
        
        for text, text_annotations in zip(clinical_texts, annotations):
            # Tokenize text
            tokens = self.tokenizer.tokenize(text)
            
            # Initialize labels as 'O'
            labels = ['O'] * len(tokens)
            
            # Apply annotations
            for start, end, label in text_annotations:
                start_token = self.tokenizer.char_to_token(start)
                end_token = self.tokenizer.char_to_token(end)
                
                if start_token is not None and end_token is not None:
                    # Mark beginning and inside tokens
                    labels[start_token] = f'B-{label}'
                    for i in range(start_token + 1, end_token + 1):
                        if i < len(labels):
                            labels[i] = f'I-{label}'
            
            # Convert labels to IDs
            label_ids = [self.label2id.get(label, 0) for label in labels]
            
            # Tokenize with special tokens
            encoding = self.tokenizer(
                text,
                truncation=True,
                max_length=512,
                padding='max_length',
                return_tensors='pt'
            )
            
            tokenized_data.append({
                'input_ids': encoding['input_ids'].squeeze(),
                'attention_mask': encoding['attention_mask'].squeeze(),
                'labels': torch.tensor(label_ids[:512])  # Truncate to max_length
            })
        
        return Dataset.from_list(tokenized_data)
    
    def create_sample_training_data(self) -> Tuple[List[str], List[List[Tuple[str, str, str]]]:
        """
        Create sample training data for demonstration
        """
        sample_texts = [
            "Patients must be 18 years or older with ECOG performance status 0-1 and measurable disease.",
            "Exclusion criteria: pregnant women, patients with Grade 3-4 toxicities, or those taking warfarin.",
            "Required biomarkers: EGFR mutation positive, ALK rearrangement negative, and normal liver function tests.",
            "Inclusion: Age 21-75, Karnofsky Performance Status ≥70%, and adequate organ function.",
            "Exclude patients with brain metastases, uncontrolled diabetes, or recent chemotherapy within 4 weeks."
        ]
        
        sample_annotations = [
            [(0, 6, "DEMOGRAPHIC"), (25, 28, "DEMOGRAPHIC"), (34, 37, "CLINICAL"), (41, 49, "CLINICAL")],
            [(0, 15, "ELIGIBILITY"), (25, 32, "DEMOGRAPHIC"), (45, 50, "PATHOLOGY"), (70, 77, "MEDICATION")],
            [(0, 8, "ELIGIBILITY"), (10, 23, "BIOMARKER"), (25, 38, "BIOMARKER"), (44, 47, "BIOMARKER")],
            [(0, 8, "ELIGIBILITY"), (10, 13, "DEMOGRAPHIC"), (15, 17, "DEMOGRAPHIC"), (19, 42, "CLINICAL")],
            [(0, 7, "ELIGIBILITY"), (9, 16, "DEMOGRAPHIC"), (18, 32, "PATHOLOGY"), (34, 50, "CLINICAL")]
        ]
        
        return sample_texts, sample_annotations
    
    def initialize_model(self):
        """Initialize tokenizer and model"""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(
            self.model_name,
            num_labels=len(self.label2id),
            id2label=self.id2label,
            label2id=self.label2id
        )
    
    def train(self, 
              train_dataset: Dataset,
              eval_dataset: Optional[Dataset] = None,
              output_dir: str = "./fine_tuned_biobert",
              num_epochs: int = 3,
              batch_size: int = 8,
              learning_rate: float = 2e-5):
        """
        Fine-tune the BioBERT model
        """
        if self.model is None:
            self.initialize_model()
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            weight_decay=0.01,
            warmup_steps=500,
            logging_dir=f"{output_dir}/logs",
            logging_steps=10,
            evaluation_strategy="epoch" if eval_dataset else "no",
            save_strategy="epoch",
            load_best_model_at_end=True if eval_dataset else False,
            metric_for_best_model="eval_loss" if eval_dataset else None,
        )
        
        data_collator = DataCollatorForTokenClassification(self.tokenizer)
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
            tokenizer=self.tokenizer,
        )
        
        logger.info("Starting fine-tuning...")
        trainer.train()
        
        # Save the fine-tuned model
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        logger.info(f"Fine-tuned model saved to {output_dir}")
        return trainer
    
    def load_fine_tuned_model(self, model_path: str):
        """Load a fine-tuned model"""
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.model.eval()
    
    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """
        Extract entities from text using fine-tuned model
        """
        if self.model is None:
            raise ValueError("Model not initialized. Call initialize_model() or load_fine_tuned_model() first.")
        
        # Tokenize input
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=2)
        
        # Convert predictions to labels
        predicted_labels = [self.id2label[pred.item()] for pred in predictions[0]]
        
        # Extract entities
        entities = []
        current_entity = None
        
        for i, (token, label) in enumerate(zip(inputs['input_ids'][0], predicted_labels)):
            if label.startswith('B-'):
                # Start of new entity
                if current_entity:
                    entities.append(current_entity)
                current_entity = {
                    'text': self.tokenizer.decode([token]),
                    'label': label[2:],  # Remove 'B-' prefix
                    'start': i
                }
            elif label.startswith('I-') and current_entity and label[2:] == current_entity['label']:
                # Continue current entity
                current_entity['text'] += ' ' + self.tokenizer.decode([token])
            else:
                # End of entity
                if current_entity:
                    entities.append(current_entity)
                    current_entity = None
        
        if current_entity:
            entities.append(current_entity)
        
        return entities

def create_fine_tuning_demo():
    """Demo function to show fine-tuning process"""
    print("=== BioBERT Fine-tuning Demo ===")
    
    # Initialize fine-tuner
    fine_tuner = BioBERTFineTuner()
    fine_tuner.initialize_model()
    
    # Create sample training data
    texts, annotations = fine_tuner.create_sample_training_data()
    
    print(f"Created {len(texts)} sample training texts")
    print("Sample text:", texts[0])
    print("Sample annotations:", annotations[0])
    
    # Prepare training dataset
    train_dataset = fine_tuner.prepare_training_data(texts, annotations)
    
    print(f"Prepared training dataset with {len(train_dataset)} samples")
    
    # Note: In a real scenario, you would:
    # 1. Collect more training data from clinical trials
    # 2. Split into train/eval sets
    # 3. Fine-tune the model
    # 4. Evaluate performance
    
    print("\nTo actually fine-tune the model, you would:")
    print("1. Collect more clinical trial texts")
    print("2. Annotate them with entity labels")
    print("3. Call fine_tuner.train(train_dataset, eval_dataset)")
    print("4. Use fine_tuner.extract_entities() for inference")
    
    return fine_tuner

if __name__ == "__main__":
    create_fine_tuning_demo() 