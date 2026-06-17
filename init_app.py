#!/usr/bin/env python
"""
Initialization script for Streamlit Cloud deployment.
Run this to ensure all necessary data files and resources are available.
"""

import os
import sys

def init_nltk_resources():
    """Initialize NLTK resources"""
    print("Initializing NLTK resources...")
    try:
        from nlp_processor import ensure_nltk_resource
        ensure_nltk_resource('corpora/stopwords')
        ensure_nltk_resource('tokenizers/punkt_tab')
        ensure_nltk_resource('corpora/wordnet')
        print("✓ NLTK resources initialized")
        return True
    except Exception as e:
        print(f"⚠ Warning: Could not initialize NLTK resources: {e}")
        return False

def init_dataset():
    """Initialize the dataset if it doesn't exist"""
    print("Initializing dataset...")
    data_path = "data/it_job_postings.csv"
    
    if os.path.exists(data_path):
        print(f"✓ Dataset already exists at {data_path}")
        return True
    
    try:
        os.makedirs("data", exist_ok=True)
        from generate_dataset import generate_dataset
        print("Generating dataset (this may take a moment)...")
        generate_dataset()
        print(f"✓ Dataset generated at {data_path}")
        return True
    except Exception as e:
        print(f"⚠ Warning: Could not generate dataset: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Streamlit App Initialization")
    print("=" * 50)
    
    nltk_ok = init_nltk_resources()
    dataset_ok = init_dataset()
    
    print("=" * 50)
    if nltk_ok and dataset_ok:
        print("✓ Initialization complete. App is ready to run!")
        sys.exit(0)
    else:
        print("⚠ Initialization completed with warnings. App may still work.")
        sys.exit(0)
