import os
import pandas as pd
import numpy as np
import re
from collections import Counter
import nltk
import warnings

warnings.filterwarnings('ignore')

nltk_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data')
if os.path.exists(nltk_data_dir):
    nltk.data.path.insert(0, nltk_data_dir)

# Add default NLTK path to try first
nltk_default_path = os.path.expanduser('~/nltk_data')
if nltk_default_path not in nltk.data.path:
    nltk.data.path.insert(0, nltk_default_path)

def ensure_nltk_resource(resource_name):
    """Safely ensure NLTK resource is available with timeout"""
    try:
        nltk.data.find(resource_name)
        return True
    except LookupError:
        try:
            nltk.download(resource_name, quiet=True, raise_errors=False)
            return True
        except Exception as e:
            print(f"Warning: Could not download {resource_name}: {str(e)}")
            return False

# Initialize NLTK resources
ensure_nltk_resource('corpora/stopwords')
ensure_nltk_resource('tokenizers/punkt_tab')
ensure_nltk_resource('corpora/wordnet')

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

SKILL_TAXONOMY = {
    "Programming Languages": ["python", "java", "javascript", "c++", "r", "scala", "rust", "swift", "kotlin", "typescript", "solidity", "bash", "powershell", "go", "ruby"],
    "Web Development": ["react", "angular", "vue.js", "node.js", "html", "css", "redux", "webpack", "rest api", "django", "flask", "spring boot", "express"],
    "Cloud & Infrastructure": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "serverless", "cloudformation", "vmware", "ansible"],
    "Data & Analytics": ["sql", "pandas", "numpy", "tableau", "power bi", "excel", "data visualization", "data warehousing", "snowflake", "etl", "apache spark", "hadoop", "kafka", "airflow", "dax"],
    "AI & Machine Learning": ["machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "nlp", "computer vision", "openai", "langchain", "transformers", "mlops", "statistics"],
    "DevOps & Tools": ["ci/cd", "jenkins", "git", "jira", "monitoring", "prometheus", "grafana", "selenium", "agile", "scrum"],
    "Security": ["network security", "siem", "penetration testing", "firewalls", "incident response", "encryption", "compliance", "vulnerability assessment", "cryptography", "security"],
    "Database": ["postgresql", "mysql", "mongodb", "oracle", "redis", "rabbitmq", "database tuning", "backup recovery", "data modeling", "firebase"],
    "Mobile Development": ["react native", "flutter", "ios", "android", "mobile"],
    "Blockchain": ["ethereum", "smart contracts", "web3", "defi", "blockchain"]
}

SKILL_TAXONOMY_LOOKUP = {}
for category, skills in SKILL_TAXONOMY.items():
    for skill in skills:
        SKILL_TAXONOMY_LOOKUP[skill] = category

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s\.\+\#\/\-]', ' ', text)
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words and len(t) > 1]
    return " ".join(tokens)

def extract_skills_from_text(text, all_known_skills):
    if pd.isna(text) or text == "":
        return []
    text_lower = str(text).lower()
    found = []
    for skill in all_known_skills:
        if skill.lower() in text_lower:
            found.append(skill)
    return found

def get_all_known_skills():
    skills = set()
    for cat_skills in SKILL_TAXONOMY.values():
        for s in cat_skills:
            skills.add(s)
    return list(skills)

def compute_tfidf(texts, max_features=100):
    vectorizer = TfidfVectorizer(max_features=max_features, ngram_range=(1, 2), stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.sum(axis=0).A1
    tfidf_scores = dict(zip(feature_names, scores))
    return dict(sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True))

def clean_dataset(df):
    df = df.drop_duplicates(subset=["Job_ID"], keep="first")
    df["Posting_Date"] = pd.to_datetime(df["Posting_Date"], errors="coerce")
    df["Year"] = df["Posting_Date"].dt.year
    df["Month"] = df["Posting_Date"].dt.month
    df["Skills"] = df["Skills"].fillna("")
    df["Job_Description"] = df["Job_Description"].fillna("")
    df["Salary_INR"] = pd.to_numeric(df["Salary_INR"], errors="coerce")
    median_salary = df.groupby("Experience_Level")["Salary_INR"].transform("median")
    df["Salary_INR"] = df["Salary_INR"].fillna(median_salary)
    df["Salary_INR"] = df["Salary_INR"].fillna(df["Salary_INR"].median())
    df["Processed_Description"] = df["Job_Description"].apply(preprocess_text)
    df["Skills_List"] = df["Skills"].apply(lambda x: [s.strip() for s in str(x).split(",") if s.strip()] if pd.notna(x) and x != "" else [])
    return df

def get_skill_frequencies(df):
    all_skills = []
    for skills_list in df["Skills_List"]:
        all_skills.extend([s.lower() for s in skills_list])
    return Counter(all_skills)

def categorize_skill(skill_name):
    skill_lower = skill_name.lower().strip()
    return SKILL_TAXONOMY_LOOKUP.get(skill_lower, "Other")

def get_skill_category_counts(df):
    category_counts = Counter()
    for skills_list in df["Skills_List"]:
        for skill in skills_list:
            cat = categorize_skill(skill)
            category_counts[cat] += 1
    return category_counts

def get_yearly_skill_trends(df, top_n=10):
    skill_freq = get_skill_frequencies(df)
    top_skills = [s for s, _ in skill_freq.most_common(top_n)]

    yearly_data = []
    for year in sorted(df["Year"].dropna().unique()):
        year_df = df[df["Year"] == year]
        year_skills = []
        for sl in year_df["Skills_List"]:
            year_skills.extend([s.lower() for s in sl])
        year_counter = Counter(year_skills)
        total = len(year_df)
        for skill in top_skills:
            yearly_data.append({
                "Year": int(year),
                "Skill": skill.title(),
                "Count": year_counter.get(skill, 0),
                "Percentage": round(year_counter.get(skill, 0) / max(total, 1) * 100, 2)
            })
    return pd.DataFrame(yearly_data)

def get_role_skill_matrix(df, top_n_skills=15):
    skill_freq = get_skill_frequencies(df)
    top_skills = [s for s, _ in skill_freq.most_common(top_n_skills)]

    roles = df["Job_Title"].unique()
    matrix_data = []
    for role in roles:
        role_df = df[df["Job_Title"] == role]
        role_skills = []
        for sl in role_df["Skills_List"]:
            role_skills.extend([s.lower() for s in sl])
        role_counter = Counter(role_skills)
        total = len(role_df)
        row = {"Role": role}
        for skill in top_skills:
            row[skill.title()] = round(role_counter.get(skill, 0) / max(total, 1) * 100, 1)
        matrix_data.append(row)
    return pd.DataFrame(matrix_data)

def get_experience_skill_data(df, top_n=10):
    skill_freq = get_skill_frequencies(df)
    top_skills = [s for s, _ in skill_freq.most_common(top_n)]

    data = []
    for level in df["Experience_Level"].unique():
        level_df = df[df["Experience_Level"] == level]
        level_skills = []
        for sl in level_df["Skills_List"]:
            level_skills.extend([s.lower() for s in sl])
        level_counter = Counter(level_skills)
        total = len(level_df)
        for skill in top_skills:
            data.append({
                "Experience": level,
                "Skill": skill.title(),
                "Percentage": round(level_counter.get(skill, 0) / max(total, 1) * 100, 2)
            })
    return pd.DataFrame(data)

def get_location_skill_data(df, top_n=10):
    skill_freq = get_skill_frequencies(df)
    top_skills = [s for s, _ in skill_freq.most_common(top_n)]

    data = []
    for loc in df["Location"].unique():
        loc_df = df[df["Location"] == loc]
        loc_skills = []
        for sl in loc_df["Skills_List"]:
            loc_skills.extend([s.lower() for s in sl])
        loc_counter = Counter(loc_skills)
        total = len(loc_df)
        for skill in top_skills:
            data.append({
                "Location": loc,
                "Skill": skill.title(),
                "Count": loc_counter.get(skill, 0),
                "Percentage": round(loc_counter.get(skill, 0) / max(total, 1) * 100, 2)
            })
    return pd.DataFrame(data)

def get_salary_skill_correlation(df, top_n=15):
    skill_freq = get_skill_frequencies(df)
    top_skills = [s for s, _ in skill_freq.most_common(top_n)]

    data = []
    for skill in top_skills:
        mask = df["Skills_List"].apply(lambda sl: skill in [s.lower() for s in sl])
        skill_df = df[mask]
        if len(skill_df) > 0:
            avg_salary = skill_df["Salary_INR"].mean()
            median_salary = skill_df["Salary_INR"].median()
            count = len(skill_df)
            data.append({
                "Skill": skill.title(),
                "Avg_Salary": round(avg_salary),
                "Median_Salary": round(median_salary),
                "Job_Count": count
            })
    return pd.DataFrame(data).sort_values("Avg_Salary", ascending=False)

def detect_declining_skills(df, recent_years=2):
    years = sorted(df["Year"].dropna().unique())
    if len(years) < 3:
        return pd.DataFrame()

    recent = years[-recent_years:]
    earlier = years[:-recent_years]

    early_df = df[df["Year"].isin(earlier)]
    recent_df = df[df["Year"].isin(recent)]

    early_skills = []
    for sl in early_df["Skills_List"]:
        early_skills.extend([s.lower() for s in sl])
    early_counter = Counter(early_skills)
    early_total = max(len(early_df), 1)

    recent_skills = []
    for sl in recent_df["Skills_List"]:
        recent_skills.extend([s.lower() for s in sl])
    recent_counter = Counter(recent_skills)
    recent_total = max(len(recent_df), 1)

    changes = []
    all_skills = set(list(early_counter.keys()) + list(recent_counter.keys()))
    for skill in all_skills:
        early_pct = early_counter.get(skill, 0) / early_total * 100
        recent_pct = recent_counter.get(skill, 0) / recent_total * 100
        if early_pct > 0.5:
            change = recent_pct - early_pct
            changes.append({
                "Skill": skill.title(),
                "Early_Period_%": round(early_pct, 2),
                "Recent_Period_%": round(recent_pct, 2),
                "Change_%": round(change, 2)
            })

    return pd.DataFrame(changes).sort_values("Change_%")
