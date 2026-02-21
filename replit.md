# IT Skill Demand Analysis Framework

## Overview
An NLP and Business Intelligence Framework for IT Skill Demand Analysis from Job Postings. Built with Streamlit, this app analyzes IT job posting data using NLP techniques and visualizes insights through interactive dashboards.

## Project Architecture
- `app.py` - Main Streamlit dashboard application (runs on port 8501)
- `nlp_processor.py` - NLP processing module (text preprocessing, TF-IDF, skill extraction, taxonomies, trend analysis)
- `pdf_report.py` - PDF report generator (creates multi-page report with all charts and tables)
- `generate_dataset.py` - Synthetic dataset generator (5000 IT job postings)
- `data/it_job_postings.csv` - Generated dataset
- `.streamlit/config.toml` - Streamlit server configuration

## Key Features
- Data cleaning & preprocessing pipeline
- NLP: tokenization, lemmatization, TF-IDF vectorization, skill extraction
- Structured skill taxonomy (Programming, Cloud, AI, DevOps, etc.)
- 9 interactive dashboard tabs: Skill Trends, Word Cloud, Role vs Skills Matrix, Experience Analysis, Location Analysis, Salary Correlation, Declining Skills, Skill Taxonomy, Raw Data
- Sidebar filters (year range, roles, locations, experience level)
- CSV export for Power BI integration
- Individual chart download (PNG) for each visualization
- Full PDF report download with all charts, tables, and analysis sections
- Clean light theme (default Streamlit styling)
- PDF report regenerates when filters change (reflects filtered data, not just full dataset)

## Tech Stack
- Python 3.11, Streamlit, Pandas, NLTK, Scikit-learn, Plotly, Matplotlib, WordCloud, FPDF2, Kaleido

## Running
```
streamlit run app.py --server.port 8501
```
