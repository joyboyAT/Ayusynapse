# 🚀 Quick Start Guide - Clinical Trials Analytics & AI Platform

## ⚡ Get Started in 5 Minutes

### 1. **Install Dependencies**
```bash
# Install Python packages
pip install -r requirements.txt

# Install spaCy model
python -m spacy download en_core_web_sm

# Run setup (creates directories and tests installation)
python setup.py
```

### 2. **Run the Demo**
```bash
# Run complete analysis pipeline
python demo.py
```

This will:
- ✅ Initialize the platform
- ✅ Create sample trial data
- ✅ Extract medical terminologies using BioBERT
- ✅ Map terminologies to EMR structures
- ✅ Generate analytics and visualizations
- ✅ Create comprehensive reports

### 3. **Start the Web API**
```bash
# Start the FastAPI server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Then visit:
- 🌐 **http://localhost:8000** - Platform overview
- 📚 **http://localhost:8000/docs** - Interactive API documentation
- 📊 **http://localhost:8000/reports/** - Generated visualizations

### 4. **Explore with Jupyter**
```bash
# Start Jupyter notebooks
jupyter notebook notebooks/
```

## 🎯 What You'll See

### Demo Output Example
```
🚀 Clinical Trials Analytics & AI Platform Demo
============================================================

📊 ONCOLOGY Analysis Results:
  - Total trials: 2
  - Laboratory: 13 occurrences, 10 unique terms
  - Pathology: 8 occurrences, 6 unique terms
  - Clinical: 4 occurrences, 3 unique terms

TOP INDICATORS:
- ECOG: 2 occurrences
- HER2: 1 occurrence
- Hemoglobin: 1 occurrence
- Age: 2 occurrences

🗺️ EMR Mappings:
- hemoglobin → FHIR Observation, LOINC 789-8
- HER2 → Pathology report, IHC section
- ECOG → Clinical assessment, performance status
```

### Generated Files
```
📁 Project Structure:
├── data/
│   ├── raw/oncology_trials.json          # Sample trial data
│   ├── raw/neurology_trials.json         # Sample trial data
│   └── processed/                        # Analysis results
├── reports/
│   ├── oncology_frequency_chart.html     # Interactive charts
│   ├── neurology_dashboard_chart.html    # Interactive charts
│   └── ... (more visualizations)
└── notebooks/
    └── trial_analysis.ipynb              # Jupyter notebook
```

## 🔧 API Endpoints

### Quick API Tests
```bash
# Check platform status
curl http://localhost:8000/api/status

# Get trial data summary
curl http://localhost:8000/api/trial-data

# Get terminology analysis
curl http://localhost:8000/api/terminology-analysis

# Get analytics results
curl http://localhost:8000/api/analytics
```

### Full API Documentation
Visit **http://localhost:8000/docs** for interactive API documentation with:
- All available endpoints
- Request/response schemas
- Try-it-out functionality
- Authentication details

## 🎯 Key Features to Explore

### 1. **Terminology Extraction**
- BioBERT-powered medical NER
- Multi-category classification
- Frequency analysis
- Coverage metrics

### 2. **EMR Mapping**
- FHIR resource mapping
- Report structure identification
- Standard code integration (LOINC, SNOMED)
- LLM-powered context understanding

### 3. **Analytics Dashboard**
- Interactive visualizations
- Terminology frequency charts
- Category distribution analysis
- Trial coverage heatmaps

### 4. **Web Interface**
- Real-time analysis
- Background task processing
- RESTful API design
- Comprehensive documentation

## 🔧 Configuration

### Environment Variables (Optional)
```bash
# For full LLM functionality
export OPENAI_API_KEY="your-api-key"

# Customize API settings
export API_HOST="0.0.0.0"
export API_PORT="8000"
```

### Configuration Files
- `config/settings.py` - Platform settings
- `requirements.txt` - Dependencies
- `setup.py` - Installation script

## 📊 Sample Results

### Terminology Categories
```
Demographics: age, gender, BMI
Clinical: ECOG, performance status, vital signs
Laboratory: hemoglobin, platelets, creatinine
Pathology: HER2, ER, PR, molecular markers
Imaging: CT, MRI, PET scans
Medications: chemotherapy, immunotherapy
Comorbidities: diabetes, heart disease
```

### EMR Mapping Examples
```
Terminology: hemoglobin
├── FHIR Resource: Observation.valueQuantity
├── LOINC Code: 789-8
├── Report Type: Laboratory
├── Section: Complete Blood Count
└── Confidence: 0.95

Terminology: ECOG
├── FHIR Resource: Observation.valueCodeableConcept
├── SNOMED Code: 424144002
├── Report Type: Clinical
├── Section: Physical Examination
└── Confidence: 0.90
```

## 🚀 Next Steps

### 1. **Customize for Your Use Case**
- Modify `config/settings.py` for your medical domains
- Add new terminology categories
- Customize EMR mapping rules

### 2. **Integrate with Real Data**
- Connect to ClinicalTrials.gov API
- Add your hospital's EMR system
- Implement real-time data collection

### 3. **Scale the Platform**
- Deploy to cloud infrastructure
- Add user authentication
- Implement advanced analytics

### 4. **Extend Functionality**
- Add more medical domains
- Implement predictive analytics
- Create mobile applications

## 🆘 Troubleshooting

### Common Issues
```bash
# If spaCy model not found
python -m spacy download en_core_web_sm

# If BioBERT fails to load
pip install --upgrade transformers torch

# If API won't start
pip install fastapi uvicorn

# If visualizations don't work
pip install plotly
```

### Getting Help
- Check the logs in the terminal
- Visit `/docs` for API documentation
- Review `PROJECT_SUMMARY.md` for detailed information
- Explore the Jupyter notebooks for examples

## 🎉 Success!

You now have a fully functional **Clinical Trials Analytics & AI Platform** that:

✅ **Extracts medical terminologies** from clinical trial criteria  
✅ **Maps to EMR structures** using AI/LLM  
✅ **Generates analytics** and visualizations  
✅ **Provides web API** for integration  
✅ **Supports healthcare standards** (FHIR, LOINC, SNOMED)  

**Ready to improve patient-trial matching and healthcare outcomes!** 🏥✨ 