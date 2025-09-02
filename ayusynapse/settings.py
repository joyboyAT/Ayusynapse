"""
Configuration settings for Clinical Trials Analytics & AI Platform
"""

import os
from typing import List, Dict

# API Configuration
API_HOST = "0.0.0.0" #listen on all network interfaces.
API_PORT = 8000 #default port for the API
API_DEBUG = True #enable debug mode for development

# Data Collection Settings  
CLINICAL_TRIALS_GOV_API_URL = "https://clinicaltrials.gov/api/query/study_fields"
MAX_TRIALS_PER_CONDITION = 50
COLLECTION_DELAY = 1  # seconds gap between requests

# Oncology Conditions
ONCOLOGY_CONDITIONS = [
    'breast cancer',
    'lung cancer', 
    'colorectal cancer',
    'prostate cancer',
    'pancreatic cancer',
    'ovarian cancer',
    'melanoma',
    'leukemia',
    'lymphoma',
    'multiple myeloma'
]

# Neurology Conditions
NEUROLOGY_CONDITIONS = [
    'Alzheimer disease',
    'Parkinson disease',
    'multiple sclerosis',
    'epilepsy',
    'stroke',
    'migraine',
    'dementia',
    'amyotrophic lateral sclerosis'
]

# Medical Terminology Categories
MEDICAL_CATEGORIES = {
    'demographics': [
        'age', 'gender', 'sex', 'race', 'ethnicity', 'weight', 'height', 'bmi',
        'pregnancy', 'lactation', 'menopausal', 'postmenopausal'
    ],
    'clinical': [
        'ecog', 'karnofsky', 'performance status', 'vital signs', 'blood pressure',
        'heart rate', 'temperature', 'respiratory rate', 'oxygen saturation',
        'pain score', 'quality of life', 'adl', 'iadl'
    ],
    'laboratory': [
        'hemoglobin', 'hgb', 'wbc', 'platelets', 'creatinine', 'bilirubin',
        'alt', 'ast', 'alkaline phosphatase', 'albumin', 'sodium', 'potassium',
        'calcium', 'magnesium', 'phosphate', 'glucose', 'hba1c', 'cholesterol',
        'triglycerides', 'ldl', 'hdl', 'pt', 'inr', 'aptt', 'd-dimer'
    ],
    'imaging': [
        'ct scan', 'mri', 'pet scan', 'x-ray', 'ultrasound', 'echocardiogram',
        'bone scan', 'mammogram', 'colonoscopy', 'endoscopy', 'biopsy'
    ],
    'pathology': [
        'histology', 'grade', 'stage', 'tumor size', 'lymph nodes',
        'metastasis', 'molecular markers', 'her2', 'er', 'pr', 'ki67',
        'p53', 'egfr', 'alk', 'ros1', 'braf', 'kras', 'nras'
    ],
    'medications': [
        'chemotherapy', 'radiation', 'immunotherapy', 'targeted therapy',
        'hormone therapy', 'bisphosphonates', 'anticoagulants', 'antibiotics',
        'steroids', 'pain medications', 'anti-emetics'
    ],
    'comorbidities': [
        'diabetes', 'hypertension', 'heart disease', 'kidney disease',
        'liver disease', 'lung disease', 'autoimmune disease', 'hiv',
        'hepatitis', 'tuberculosis', 'cancer history'
    ]
}

# NLP Model Settings
BIOBERT_MODEL_NAME = "dmis-lab/biobert-v1.1"
SPACY_MODEL_NAME = "en_core_sci_sm"
FALLBACK_SPACY_MODEL = "en_core_web_sm"

# LLM Settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
OPENAI_MODEL = "gpt-4"
OPENAI_TEMPERATURE = 0.3
OPENAI_MAX_TOKENS = 1000

# FHIR Settings
FHIR_RESOURCES = {
    'demographics': {
        'Patient': ['birthDate', 'gender', 'race', 'ethnicity'],
        'Observation': ['bodyMassIndex', 'height', 'weight']
    },
    'laboratory': {
        'Observation': ['laboratory', 'labResults'],
        'DiagnosticReport': ['laboratory', 'pathology']
    },
    
    'clinical': {
        'Observation': ['vitalSigns', 'performanceStatus'],
        'Condition': ['clinicalStatus', 'severity']
    },
    'pathology': {
        'Observation': ['pathology', 'tumorMarkers'],
        'DiagnosticReport': ['pathology', 'histology']
    },
    'imaging': {
        'DiagnosticReport': ['radiology', 'imaging'],
        'ImagingStudy': ['modality', 'bodySite']
    },
    'medications': {
        'MedicationRequest': ['medication', 'dosage'],
        'MedicationAdministration': ['medication', 'timing']
    }
}

#FHIR = Fast Healthcare Interoperability Resources (a standard for medical data).

#Maps medical categories (demographics, labs, imaging, etc.) to FHIR resource types.

# Standard Medical Codes
STANDARD_CODES = {
    'LOINC': 'http://loinc.org',
    'SNOMED': 'http://snomed.info/sct',
    'ICD10': 'http://hl7.org/fhir/sid/icd-10-cm',
    'RxNorm': 'http://www.nlm.nih.gov/research/umls/rxnorm',
    'UCUM': 'http://unitsofmeasure.org'
}

# Analytics Settings
CHART_COLORS = {
    'oncology': '#FF6B6B',
    'neurology': '#4ECDC4',
    'demographics': '#45B7D1',
    'clinical': '#96CEB4',
    'laboratory': '#FFEAA7',
    'pathology': '#DDA0DD',
    'imaging': '#98D8C8',
    'medications': '#F7DC6F'
}

# File Paths
DATA_DIR = "data"
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
MODELS_DIR = os.path.join(DATA_DIR, "models")
REPORTS_DIR = "reports"
NOTEBOOKS_DIR = "notebooks"

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Performance Settings
MAX_WORKERS = 4
BATCH_SIZE = 32
CACHE_RESULTS = True

# Security Settings
CORS_ORIGINS = ["*"]
API_RATE_LIMIT = 100  # requests per minute 