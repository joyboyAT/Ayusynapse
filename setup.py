#!/usr/bin/env python3
"""
Setup script for Clinical Trials Analytics & AI Platform
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = [
        'data/raw',
        'data/processed',
        'data/models',
        'reports',
        'notebooks'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing Python dependencies...")
    
    # Install from requirements.txt
    if not run_command("pip install -r requirements.txt", "Installing requirements"):
        return False
    
    # Install spaCy models
    if not run_command("python -m spacy download en_core_web_sm", "Installing spaCy web model"):
        return False
    
    try:
        if not run_command("python -m spacy download en_core_sci_sm", "Installing spaCy scientific model"):
            print("⚠️  Scientific model not available, using web model")
    except:
        print("⚠️  Scientific model not available, using web model")
    
    return True

def download_models():
    """Download pre-trained models."""
    print("🤖 Downloading pre-trained models...")
    
    # This will be handled by the transformers library when first used
    print("✅ Models will be downloaded automatically on first use")
    return True

def test_installation():
    """Test the installation."""
    print("🧪 Testing installation...")
    
    try:
        # Test imports
        import torch
        import transformers
        import spacy
        import pandas as pd
        import plotly
        import fastapi
        
        print("✅ All core dependencies imported successfully")
        
        # Test platform initialization
        from src.main import ClinicalTrialsPlatform
        platform = ClinicalTrialsPlatform()
        print("✅ Platform initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Clinical Trials Analytics & AI Platform")
    print("=" * 60)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Download models
    if not download_models():
        print("❌ Failed to download models")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run the main application: python src/main.py")
    print("2. Start the web API: uvicorn src.api.main:app --reload")
    print("3. Open Jupyter notebooks: jupyter notebook notebooks/")
    print("4. View documentation: http://localhost:8000/docs")
    print("\n🔧 Configuration:")
    print("- Set OPENAI_API_KEY environment variable for LLM features")
    print("- Modify config files in src/config/ for customization")
    print("\n📚 Documentation:")
    print("- README.md: Project overview and usage")
    print("- notebooks/: Interactive analysis examples")
    print("- reports/: Generated analytics and visualizations")

if __name__ == "__main__":
    main() 