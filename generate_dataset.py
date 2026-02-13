import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

JOB_TITLES = [
    "Data Scientist", "Data Analyst", "Machine Learning Engineer",
    "Full Stack Developer", "Backend Developer", "Frontend Developer",
    "DevOps Engineer", "Cloud Architect", "Data Engineer",
    "Software Engineer", "AI Engineer", "Cybersecurity Analyst",
    "Business Intelligence Analyst", "Product Manager (Tech)",
    "Site Reliability Engineer", "Mobile App Developer",
    "Blockchain Developer", "QA Engineer", "Systems Administrator",
    "Database Administrator"
]

SKILLS_BY_ROLE = {
    "Data Scientist": ["Python", "R", "SQL", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Statistics", "NLP", "Data Visualization", "Scikit-learn", "Jupyter"],
    "Data Analyst": ["SQL", "Excel", "Python", "Tableau", "Power BI", "Statistics", "Data Visualization", "Pandas", "R", "Google Analytics"],
    "Machine Learning Engineer": ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "Deep Learning", "MLOps", "Docker", "Kubernetes", "AWS", "Machine Learning", "NLP", "Computer Vision"],
    "Full Stack Developer": ["JavaScript", "React", "Node.js", "HTML", "CSS", "MongoDB", "SQL", "TypeScript", "REST API", "Git", "Docker", "Angular", "Vue.js"],
    "Backend Developer": ["Java", "Python", "Node.js", "SQL", "REST API", "Microservices", "Docker", "Kubernetes", "Spring Boot", "PostgreSQL", "Redis", "RabbitMQ"],
    "Frontend Developer": ["JavaScript", "React", "HTML", "CSS", "TypeScript", "Angular", "Vue.js", "Redux", "Webpack", "REST API", "Git", "Figma"],
    "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "CI/CD", "Jenkins", "Terraform", "Ansible", "Linux", "Git", "Python", "Bash", "Monitoring", "Azure", "GCP"],
    "Cloud Architect": ["AWS", "Azure", "GCP", "Terraform", "Docker", "Kubernetes", "Microservices", "Networking", "Security", "Serverless", "CloudFormation", "Linux"],
    "Data Engineer": ["Python", "SQL", "Apache Spark", "Hadoop", "ETL", "Airflow", "AWS", "Kafka", "Data Warehousing", "Snowflake", "Docker", "Scala"],
    "Software Engineer": ["Java", "Python", "C++", "JavaScript", "SQL", "Git", "Docker", "REST API", "Agile", "Data Structures", "Algorithms", "Linux"],
    "AI Engineer": ["Python", "TensorFlow", "PyTorch", "Deep Learning", "NLP", "Computer Vision", "Machine Learning", "OpenAI", "LangChain", "Transformers", "MLOps", "Docker"],
    "Cybersecurity Analyst": ["Network Security", "SIEM", "Penetration Testing", "Firewalls", "Incident Response", "Linux", "Python", "Encryption", "Compliance", "Vulnerability Assessment"],
    "Business Intelligence Analyst": ["Power BI", "Tableau", "SQL", "Excel", "Data Visualization", "Python", "ETL", "Data Warehousing", "Statistics", "DAX"],
    "Product Manager (Tech)": ["Agile", "Scrum", "JIRA", "SQL", "Data Analysis", "Product Strategy", "A/B Testing", "User Research", "Roadmapping", "Stakeholder Management"],
    "Site Reliability Engineer": ["Linux", "Docker", "Kubernetes", "AWS", "Python", "Monitoring", "Prometheus", "Grafana", "CI/CD", "Terraform", "Bash", "Incident Management"],
    "Mobile App Developer": ["Swift", "Kotlin", "React Native", "Flutter", "JavaScript", "REST API", "Git", "Firebase", "iOS", "Android", "TypeScript"],
    "Blockchain Developer": ["Solidity", "Ethereum", "Smart Contracts", "JavaScript", "Web3", "Rust", "Cryptography", "DeFi", "Node.js", "Python"],
    "QA Engineer": ["Selenium", "Python", "Java", "Test Automation", "JIRA", "Agile", "API Testing", "Manual Testing", "CI/CD", "Performance Testing"],
    "Systems Administrator": ["Linux", "Windows Server", "Networking", "Bash", "PowerShell", "Active Directory", "VMware", "Security", "Monitoring", "DNS"],
    "Database Administrator": ["SQL", "PostgreSQL", "MySQL", "Oracle", "MongoDB", "Database Tuning", "Backup Recovery", "Linux", "Python", "Data Modeling"]
}

LOCATIONS = [
    "Bangalore", "Hyderabad", "Mumbai", "Pune", "Chennai",
    "Delhi NCR", "Kolkata", "Ahmedabad", "Jaipur", "Kochi",
    "New York", "San Francisco", "London", "Berlin", "Singapore",
    "Toronto", "Sydney", "Dublin", "Austin", "Seattle"
]

EXPERIENCE_LEVELS = ["Fresher (0-1 yrs)", "Junior (1-3 yrs)", "Mid (3-5 yrs)", "Senior (5-8 yrs)", "Lead (8-12 yrs)", "Principal (12+ yrs)"]

SALARY_RANGES = {
    "Fresher (0-1 yrs)": (300000, 600000),
    "Junior (1-3 yrs)": (500000, 1000000),
    "Mid (3-5 yrs)": (800000, 1600000),
    "Senior (5-8 yrs)": (1400000, 2500000),
    "Lead (8-12 yrs)": (2200000, 3800000),
    "Principal (12+ yrs)": (3500000, 5500000),
}

DESCRIPTION_TEMPLATES = [
    "We are looking for a skilled {title} to join our team. The ideal candidate should have experience with {skills_str}. You will be responsible for {resp}.",
    "Join our growing team as a {title}. Required skills: {skills_str}. This role involves {resp} and collaborating with cross-functional teams.",
    "Exciting opportunity for a {title}! Must be proficient in {skills_str}. Key responsibilities include {resp}.",
    "Hiring a {title} with strong expertise in {skills_str}. You will {resp} and drive innovation in our technology stack.",
    "We need an experienced {title} who can work with {skills_str}. The role focuses on {resp} and delivering high-quality solutions."
]

RESPONSIBILITIES = {
    "Data Scientist": ["building predictive models", "analyzing large datasets", "creating data pipelines", "presenting insights to stakeholders"],
    "Data Analyst": ["generating reports", "analyzing business metrics", "creating dashboards", "data quality assurance"],
    "Machine Learning Engineer": ["deploying ML models to production", "optimizing model performance", "building ML pipelines", "feature engineering"],
    "Full Stack Developer": ["building web applications", "designing RESTful APIs", "database management", "frontend UI development"],
    "Backend Developer": ["designing scalable backend systems", "API development", "database optimization", "microservices architecture"],
    "Frontend Developer": ["building responsive user interfaces", "optimizing web performance", "implementing design systems", "cross-browser compatibility"],
    "DevOps Engineer": ["managing CI/CD pipelines", "infrastructure automation", "monitoring and alerting", "container orchestration"],
    "Cloud Architect": ["designing cloud infrastructure", "cost optimization", "security architecture", "migration planning"],
    "Data Engineer": ["building data pipelines", "data warehousing", "ETL processes", "data quality management"],
    "Software Engineer": ["writing clean code", "software design", "code reviews", "technical documentation"],
    "AI Engineer": ["developing AI solutions", "training deep learning models", "integrating AI into products", "research and prototyping"],
    "Cybersecurity Analyst": ["threat detection", "vulnerability assessment", "security audits", "incident response"],
    "Business Intelligence Analyst": ["building BI dashboards", "data modeling", "report automation", "business requirements analysis"],
    "Product Manager (Tech)": ["product roadmap planning", "stakeholder management", "feature prioritization", "user research"],
    "Site Reliability Engineer": ["ensuring system reliability", "incident management", "capacity planning", "performance optimization"],
    "Mobile App Developer": ["building mobile applications", "UI/UX implementation", "app store deployment", "performance optimization"],
    "Blockchain Developer": ["smart contract development", "DApp building", "blockchain architecture", "security auditing"],
    "QA Engineer": ["test automation", "quality assurance", "bug tracking", "performance testing"],
    "Systems Administrator": ["server management", "network administration", "system monitoring", "security patching"],
    "Database Administrator": ["database management", "performance tuning", "backup and recovery", "data migration"]
}

def generate_dataset(n=5000):
    rows = []
    start_date = datetime(2018, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range_days = (end_date - start_date).days

    year_weights = {2018: 0.08, 2019: 0.10, 2020: 0.12, 2021: 0.14, 2022: 0.16, 2023: 0.16, 2024: 0.14, 2025: 0.10}

    for i in range(n):
        title = random.choice(JOB_TITLES)
        skills_pool = SKILLS_BY_ROLE[title]
        num_skills = random.randint(3, min(8, len(skills_pool)))
        skills = random.sample(skills_pool, num_skills)

        year = random.choices(list(year_weights.keys()), weights=list(year_weights.values()), k=1)[0]
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        posting_date = datetime(year, month, day)

        exp = random.choice(EXPERIENCE_LEVELS)
        salary_min, salary_max = SALARY_RANGES[exp]
        salary = round(random.uniform(salary_min, salary_max), -3)

        location = random.choice(LOCATIONS)

        resps = random.sample(RESPONSIBILITIES[title], min(2, len(RESPONSIBILITIES[title])))
        resp_str = " and ".join(resps)
        skills_str = ", ".join(skills)
        desc = random.choice(DESCRIPTION_TEMPLATES).format(title=title, skills_str=skills_str, resp=resp_str)

        if random.random() < 0.03:
            skills_str = np.nan
        if random.random() < 0.02:
            salary = np.nan
        if random.random() < 0.01:
            desc = np.nan

        rows.append({
            "Job_ID": f"JOB-{i+1:05d}",
            "Job_Title": title,
            "Job_Description": desc,
            "Skills": skills_str,
            "Experience_Level": exp,
            "Location": location,
            "Salary_INR": salary,
            "Posting_Date": posting_date.strftime("%Y-%m-%d")
        })

    df = pd.DataFrame(rows)
    df.to_csv("data/it_job_postings.csv", index=False)
    print(f"Generated {len(df)} job postings -> data/it_job_postings.csv")
    return df

if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    generate_dataset()
