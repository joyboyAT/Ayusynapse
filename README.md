# Clinical Trials Analytics & AI Platform

## Problem Statement
Clinical trials have complex inclusion/exclusion criteria containing vast medical terminologies. This platform identifies top-occurring terminologies and maps them to EMR data structures using AI/LLM techniques.

## Features
- **Clinical Trial Analysis**: Extract and analyze inclusion/exclusion criteria
- **Terminology Identification**: Identify top-occurring medical terminologies
- **EMR Mapping**: Map terminologies to FHIR structures and report formats
- **Analytics Dashboard**: Visualize terminology frequency and patterns
- **AI-Powered Matching**: Improve patient-trial matching accuracy

## Project Structure
```
Ayusynapse/
├── src/
│   ├── data/
│   │   ├── collectors/          # Data collection modules
│   │   ├── processors/          # Data processing pipelines
│   │   └── datasets/            # Sample datasets
│   ├── models/
│   │   ├── nlp/                # NLP models (BioBERT, etc.)
│   │   ├── llm/                # LLM integration
│   │   └── analytics/          # Analytics models
│   ├── api/
│   │   ├── endpoints/          # FastAPI endpoints
│   │   └── schemas/            # Pydantic schemas
│   └── utils/
│       ├── fhir_utils.py       # FHIR utilities
│       ├── medical_terms.py    # Medical terminology processing
│       └── visualization.py    # Plotting utilities
├── notebooks/
│   ├── trial_analysis.ipynb    # Trial data analysis
│   ├── terminology_extraction.ipynb  # Terminology identification
│   └── emr_mapping.ipynb      # EMR mapping analysis
├── tests/
├── config/
├── docs/
└── data/
    ├── raw/                    # Raw trial data
    ├── processed/              # Processed datasets
    └── models/                 # Trained models
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment
```bash
python -m spacy download en_core_web_sm
python -m spacy download en_core_sci_sm
```

### 3. Run the Application
```bash
# Start the API server
uvicorn src.api.main:app --reload

# Run analysis notebooks
jupyter notebook notebooks/
```

## Key Components

### 1. Clinical Trial Data Collector
- Scrapes trial data from public sources
- Extracts inclusion/exclusion criteria
- Categorizes by cancer type/neurology disorders

### 2. Terminology Extractor
- Uses BioBERT for medical NER
- Identifies top-occurring terminologies
- Categorizes by: Demographics, Clinical, Pathology, Imaging

### 3. EMR Mapping Engine
- Maps terminologies to FHIR resources
- Identifies structured vs unstructured data
- Generates mapping recommendations

### 4. Analytics Dashboard
- Terminology frequency analysis
- Trial coverage statistics
- Matching accuracy metrics

## Cancer Types & Neurology Disorders Focus
- **Oncology**: Breast, Lung, Colorectal, Prostate Cancer
- **Neurology**: Alzheimer's, Parkinson's, Multiple Sclerosis, Epilepsy

## Technology Stack
- **NLP**: BioBERT, spaCy, Transformers
- **LLM**: OpenAI GPT, Local models
- **Analytics**: Pandas, Plotly, scikit-learn
- **API**: FastAPI, SQLAlchemy
- **Healthcare**: FHIR, HL7 standards

## Contributing
1. Fork the repository
2. Create feature branch
3. Add tests
4. Submit pull request

## License
MIT License # Ayusynapse
