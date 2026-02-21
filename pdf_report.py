import os
import tempfile
from datetime import datetime
from collections import Counter

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from wordcloud import WordCloud
from fpdf import FPDF

from nlp_processor import (
    get_skill_frequencies, get_skill_category_counts,
    get_yearly_skill_trends, get_role_skill_matrix, get_experience_skill_data,
    get_location_skill_data, get_salary_skill_correlation, detect_declining_skills,
    compute_tfidf, SKILL_TAXONOMY
)


class ReportPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_fill_color(67, 56, 202)
        self.rect(0, 0, 210, 18, 'F')
        self.set_fill_color(99, 102, 241)
        self.rect(0, 18, 210, 3, 'F')
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(255, 255, 255)
        self.set_y(5)
        self.cell(0, 8, 'IT Skill Demand Analysis Report', align='C')
        self.set_text_color(0, 0, 0)
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

    def add_cover_page(self, total_jobs, unique_skills, job_roles, avg_salary):
        self.add_page()
        self.ln(30)
        self.set_fill_color(67, 56, 202)
        self.rect(30, 50, 150, 60, 'F')
        self.set_fill_color(99, 102, 241)
        self.rect(30, 110, 150, 2, 'F')
        self.set_y(58)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 14, 'IT Skill Demand Analysis', align='C')
        self.ln(14)
        self.set_font('Helvetica', '', 14)
        self.cell(0, 10, 'NLP & Business Intelligence Framework', align='C')
        self.ln(10)
        self.set_font('Helvetica', 'I', 11)
        self.cell(0, 10, 'Comprehensive Job Market Insights Report', align='C')
        self.set_text_color(0, 0, 0)
        self.ln(30)
        self.set_y(125)
        self.set_font('Helvetica', '', 11)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, f'Generated on: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}', align='C')
        self.ln(20)
        metrics = [
            ("Total Job Postings", f"{total_jobs:,}"),
            ("Unique Skills", f"{unique_skills}"),
            ("Job Roles", f"{job_roles}"),
            ("Avg Salary (INR)", f"{avg_salary:,.0f}")
        ]
        col_w = 42
        start_x = (210 - col_w * 4 - 6) / 2
        self.set_x(start_x)
        for i, (label, val) in enumerate(metrics):
            x = start_x + i * (col_w + 2)
            self.set_fill_color(238, 242, 255)
            self.rect(x, self.get_y(), col_w, 28, 'DF')
            self.set_fill_color(99, 102, 241)
            self.rect(x, self.get_y(), col_w, 4, 'F')
            self.set_xy(x, self.get_y() + 6)
            self.set_font('Helvetica', 'B', 13)
            self.set_text_color(67, 56, 202)
            self.cell(col_w, 8, val, align='C')
            self.set_xy(x, self.get_y() + 8)
            self.set_font('Helvetica', '', 7)
            self.set_text_color(100, 100, 100)
            self.cell(col_w, 6, label, align='C')
        self.set_text_color(0, 0, 0)

    def add_section_title(self, title):
        self.ln(6)
        self.set_fill_color(238, 242, 255)
        self.rect(10, self.get_y(), 190, 12, 'F')
        self.set_fill_color(99, 102, 241)
        self.rect(10, self.get_y(), 4, 12, 'F')
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(67, 56, 202)
        self.set_x(18)
        self.cell(0, 12, title)
        self.set_text_color(0, 0, 0)
        self.ln(16)

    def add_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 6, text)
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def add_chart_image(self, img_path, w=180):
        if os.path.exists(img_path):
            x = (210 - w) / 2
            if self.get_y() + 90 > 270:
                self.add_page()
            self.image(img_path, x=x, w=w)
            self.ln(8)

    def add_table(self, headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)
        if self.get_y() + 10 + len(rows) * 7 > 270:
            self.add_page()
        self.set_font('Helvetica', 'B', 9)
        self.set_fill_color(67, 56, 202)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 8, str(h), border=1, fill=True, align='C')
        self.ln()
        self.set_font('Helvetica', '', 8)
        self.set_text_color(40, 40, 40)
        for j, row in enumerate(rows):
            if j % 2 == 0:
                self.set_fill_color(245, 245, 255)
            else:
                self.set_fill_color(255, 255, 255)
            for i, val in enumerate(row):
                self.cell(col_widths[i], 7, str(val), border=1, fill=True, align='C')
            self.ln()
        self.set_text_color(0, 0, 0)
        self.ln(5)


def save_fig(fig, path):
    fig.savefig(path, format='png', dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)


def generate_pdf_report(filtered_df):
    tmpdir = tempfile.mkdtemp()

    unique_skills = set()
    for sl in filtered_df["Skills_List"]:
        unique_skills.update([s.lower() for s in sl])

    total_jobs = len(filtered_df)
    n_unique = len(unique_skills)
    n_roles = filtered_df["Job_Title"].nunique()
    avg_salary = filtered_df["Salary_INR"].mean()

    pdf = ReportPDF()
    pdf.alias_nb_pages()
    pdf.add_cover_page(total_jobs, n_unique, n_roles, avg_salary)

    pdf.add_page()
    pdf.add_section_title("1. Skill Demand Trends Over Time")
    pdf.add_text("This section shows how the demand for top IT skills has changed year over year, helping identify emerging and fading technologies in the job market.")
    trend_df = get_yearly_skill_trends(filtered_df, top_n=10)
    if not trend_df.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        for skill in trend_df["Skill"].unique():
            sdf = trend_df[trend_df["Skill"] == skill]
            ax.plot(sdf["Year"], sdf["Percentage"], marker='o', label=skill, linewidth=2, markersize=5)
        ax.set_xlabel("Year", fontsize=11)
        ax.set_ylabel("% of Job Postings", fontsize=11)
        ax.set_title("Top Skill Demand Trends (% of Job Postings)", fontsize=13, fontweight='bold')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=5, fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_xticks(sorted(trend_df["Year"].unique()))
        path = os.path.join(tmpdir, "trends.png")
        save_fig(fig, path)
        pdf.add_chart_image(path, w=175)

    pdf.add_page()
    pdf.add_section_title("2. Skills Word Cloud & Top Skills")
    pdf.add_text("The word cloud visualizes the most frequently mentioned skills across all job postings. Larger words indicate higher frequency of demand in the IT job market.")
    skill_freq = get_skill_frequencies(filtered_df)
    if skill_freq:
        wc = WordCloud(width=1000, height=500, background_color="white",
                       colormap="viridis", max_words=80).generate_from_frequencies(skill_freq)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        wc_path = os.path.join(tmpdir, "wordcloud.png")
        save_fig(fig, wc_path)
        pdf.add_chart_image(wc_path, w=170)

        top20 = skill_freq.most_common(20)
        fig, ax = plt.subplots(figsize=(10, 6))
        skills_names = [s.title() for s, _ in top20]
        skills_counts = [c for _, c in top20]
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(skills_names)))
        ax.barh(range(len(skills_names)), skills_counts, color=colors)
        ax.set_yticks(range(len(skills_names)))
        ax.set_yticklabels(skills_names, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel("Frequency", fontsize=11)
        ax.set_title("Top 20 Most In-Demand Skills", fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        path = os.path.join(tmpdir, "top_skills.png")
        save_fig(fig, path)
        pdf.add_chart_image(path, w=170)

    pdf.add_page()
    pdf.add_section_title("3. Role vs Skills Matrix")
    pdf.add_text("This heatmap shows the percentage of job postings for each role that mention specific skills. It reveals which skills are most critical for different IT positions.")
    matrix_df = get_role_skill_matrix(filtered_df, top_n_skills=12)
    if not matrix_df.empty:
        roles = matrix_df["Role"].tolist()
        skills_cols = [c for c in matrix_df.columns if c != "Role"]
        z_values = matrix_df[skills_cols].values
        fig, ax = plt.subplots(figsize=(12, 7))
        im = ax.imshow(z_values, cmap='YlOrRd', aspect='auto')
        ax.set_xticks(range(len(skills_cols)))
        ax.set_xticklabels(skills_cols, rotation=45, ha='right', fontsize=8)
        ax.set_yticks(range(len(roles)))
        ax.set_yticklabels(roles, fontsize=8)
        for i in range(len(roles)):
            for j in range(len(skills_cols)):
                ax.text(j, i, f"{z_values[i, j]:.0f}%", ha='center', va='center', fontsize=6)
        ax.set_title("Skill Demand by Job Role (%)", fontsize=13, fontweight='bold')
        plt.colorbar(im, ax=ax, shrink=0.8)
        path = os.path.join(tmpdir, "heatmap.png")
        save_fig(fig, path)
        pdf.add_chart_image(path, w=180)

    pdf.add_page()
    pdf.add_section_title("4. Experience Level Analysis")
    pdf.add_text("This analysis compares skill requirements across experience levels, from freshers to senior professionals. It helps identify which skills are entry-level versus those requiring years of expertise.")
    exp_data = get_experience_skill_data(filtered_df, top_n=8)
    if not exp_data.empty:
        exp_order = ["Fresher (0-1 yrs)", "Junior (1-3 yrs)", "Mid (3-5 yrs)",
                     "Senior (5-8 yrs)", "Lead (8-12 yrs)", "Principal (12+ yrs)"]
        exp_data["Experience"] = pd.Categorical(exp_data["Experience"], categories=exp_order, ordered=True)
        pivot = exp_data.pivot_table(values="Percentage", index="Experience", columns="Skill", fill_value=0)
        pivot = pivot.reindex(exp_order)
        fig, ax = plt.subplots(figsize=(12, 6))
        pivot.plot(kind='bar', ax=ax, width=0.8)
        ax.set_xlabel("Experience Level", fontsize=11)
        ax.set_ylabel("% of Postings", fontsize=11)
        ax.set_title("Skill Demand by Experience Level", fontsize=13, fontweight='bold')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=4, fontsize=8)
        ax.set_xticklabels([e.split(' ')[0] for e in exp_order], rotation=30, ha='right', fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')
        path = os.path.join(tmpdir, "experience.png")
        save_fig(fig, path)
        pdf.add_chart_image(path, w=175)

    pdf.add_page()
    pdf.add_section_title("5. Location-Based Skill Demand")
    pdf.add_text("Geographic analysis of skill demand across major IT hubs worldwide. This helps professionals understand regional job markets and plan career moves accordingly.")
    loc_data = get_location_skill_data(filtered_df, top_n=8)
    if not loc_data.empty:
        loc_counts = filtered_df["Location"].value_counts().head(15)
        fig, ax = plt.subplots(figsize=(10, 5))
        colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(loc_counts)))
        ax.bar(range(len(loc_counts)), loc_counts.values, color=colors)
        ax.set_xticks(range(len(loc_counts)))
        ax.set_xticklabels(loc_counts.index, rotation=45, ha='right', fontsize=9)
        ax.set_ylabel("Job Count", fontsize=11)
        ax.set_title("Job Postings by Location", fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        path = os.path.join(tmpdir, "location.png")
        save_fig(fig, path)
        pdf.add_chart_image(path, w=170)

        loc_pivot = loc_data.pivot_table(values="Percentage", index="Location", columns="Skill", fill_value=0)
        fig, ax = plt.subplots(figsize=(12, 7))
        im = ax.imshow(loc_pivot.values, cmap='GnBu', aspect='auto')
        ax.set_xticks(range(len(loc_pivot.columns)))
        ax.set_xticklabels(loc_pivot.columns, rotation=45, ha='right', fontsize=8)
        ax.set_yticks(range(len(loc_pivot.index)))
        ax.set_yticklabels(loc_pivot.index, fontsize=8)
        ax.set_title("Skill Demand Across Locations", fontsize=13, fontweight='bold')
        plt.colorbar(im, ax=ax, shrink=0.8, label="% of Postings")
        path2 = os.path.join(tmpdir, "location_heat.png")
        save_fig(fig, path2)
        pdf.add_chart_image(path2, w=180)

    pdf.add_page()
    pdf.add_section_title("6. Salary vs Skill Correlation")
    pdf.add_text("This analysis reveals which skills command the highest salaries in the IT market. Understanding salary-skill correlation helps both job seekers and employers make informed decisions.")
    salary_data = get_salary_skill_correlation(filtered_df, top_n=15)
    if not salary_data.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(salary_data)))
        ax.bar(range(len(salary_data)), salary_data["Avg_Salary"].values, color=colors)
        ax.set_xticks(range(len(salary_data)))
        ax.set_xticklabels(salary_data["Skill"].values, rotation=45, ha='right', fontsize=9)
        ax.set_ylabel("Average Salary (INR)", fontsize=11)
        ax.set_title("Average Salary by Skill (INR)", fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x/100000:.1f}L'))
        path = os.path.join(tmpdir, "salary.png")
        save_fig(fig, path)
        pdf.add_chart_image(path, w=170)

        headers = ["Skill", "Avg Salary (INR)", "Median Salary (INR)", "Job Count"]
        rows = [[r["Skill"], f"{r['Avg_Salary']:,.0f}", f"{r['Median_Salary']:,.0f}", str(r["Job_Count"])]
                for _, r in salary_data.head(15).iterrows()]
        pdf.add_table(headers, rows, col_widths=[50, 50, 50, 40])

    pdf.add_page()
    pdf.add_section_title("7. Declining & Rising Technologies")
    pdf.add_text("Tracking technology trends helps professionals stay relevant. This section identifies skills gaining momentum and those losing market demand by comparing recent years to earlier periods.")
    decline_df = detect_declining_skills(filtered_df)
    if not decline_df.empty:
        declining = decline_df.head(10)
        rising = decline_df.tail(10).sort_values("Change_%", ascending=False)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        colors_dec = ['#d32f2f' if v < 0 else '#388e3c' for v in declining["Change_%"]]
        ax1.barh(range(len(declining)), declining["Change_%"].values, color=colors_dec)
        ax1.set_yticks(range(len(declining)))
        ax1.set_yticklabels(declining["Skill"].values, fontsize=9)
        ax1.set_xlabel("Change in Demand (%)")
        ax1.set_title("Most Declining Skills", fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        ax1.invert_yaxis()

        colors_rise = ['#388e3c' if v > 0 else '#d32f2f' for v in rising["Change_%"]]
        ax2.barh(range(len(rising)), rising["Change_%"].values, color=colors_rise)
        ax2.set_yticks(range(len(rising)))
        ax2.set_yticklabels(rising["Skill"].values, fontsize=9)
        ax2.set_xlabel("Change in Demand (%)")
        ax2.set_title("Most Rising Skills", fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        ax2.invert_yaxis()

        plt.tight_layout()
        path = os.path.join(tmpdir, "trends_change.png")
        save_fig(fig, path)
        pdf.add_chart_image(path, w=180)

    pdf.add_page()
    pdf.add_section_title("8. Skill Taxonomy")
    pdf.add_text("Skills are organized into structured categories for better analysis. This taxonomy groups related technologies, helping identify which domains are most in demand.")
    cat_counts = get_skill_category_counts(filtered_df)
    if cat_counts:
        cat_df = pd.DataFrame(list(cat_counts.items()), columns=["Category", "Count"]).sort_values("Count", ascending=False)
        fig, ax = plt.subplots(figsize=(8, 8))
        colors = plt.cm.Set3(np.linspace(0, 1, len(cat_df)))
        wedges, texts, autotexts = ax.pie(cat_df["Count"], labels=cat_df["Category"],
                                           autopct='%1.1f%%', colors=colors, pctdistance=0.85,
                                           textprops={'fontsize': 9})
        for t in autotexts:
            t.set_fontsize(8)
        ax.set_title("Skill Distribution by Category", fontsize=13, fontweight='bold')
        path = os.path.join(tmpdir, "taxonomy.png")
        save_fig(fig, path)
        pdf.add_chart_image(path, w=150)

        headers = ["Category", "Total Mentions", "Skills Included"]
        rows = []
        for _, row in cat_df.iterrows():
            cat = row["Category"]
            count = str(row["Count"])
            skills = SKILL_TAXONOMY.get(cat, [])
            skills_str = ", ".join([s.title() for s in skills[:6]])
            if len(skills) > 6:
                skills_str += f" (+{len(skills)-6} more)"
            rows.append([cat, count, skills_str])
        pdf.add_table(headers, rows, col_widths=[45, 35, 110])

    pdf.add_page()
    pdf.add_section_title("9. TF-IDF Keyword Analysis")
    pdf.add_text("TF-IDF (Term Frequency-Inverse Document Frequency) analysis extracts the most significant keywords from job descriptions, revealing hidden patterns beyond explicit skill listings.")
    valid_texts = filtered_df["Processed_Description"][filtered_df["Processed_Description"] != ""]
    if len(valid_texts) > 0:
        tfidf_scores = compute_tfidf(valid_texts.tolist(), max_features=20)
        tfidf_items = list(tfidf_scores.items())[:20]
        fig, ax = plt.subplots(figsize=(10, 6))
        keywords = [k for k, _ in tfidf_items]
        scores = [v for _, v in tfidf_items]
        colors = plt.cm.plasma(np.linspace(0.2, 0.9, len(keywords)))
        ax.barh(range(len(keywords)), scores, color=colors)
        ax.set_yticks(range(len(keywords)))
        ax.set_yticklabels(keywords, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel("TF-IDF Score", fontsize=11)
        ax.set_title("Top TF-IDF Keywords from Job Descriptions", fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        path = os.path.join(tmpdir, "tfidf.png")
        save_fig(fig, path)
        pdf.add_chart_image(path, w=170)

    pdf.add_page()
    pdf.add_section_title("10. Future Scope & Recommendations")
    pdf.add_text(
        "Based on the analysis of IT job market data, the following recommendations and future directions are identified:\n\n"
        "1. Predictive Analytics: The framework can be extended with machine learning models to forecast future skill demand trends.\n\n"
        "2. Real-Time Data Integration: Connecting to live job posting APIs (LinkedIn, Indeed, Naukri) would enable real-time market monitoring.\n\n"
        "3. Workforce Planning: Organizations can use these insights to align training programs with market demands.\n\n"
        "4. Educational Alignment: Universities and bootcamps can update curricula based on identified skill gaps.\n\n"
        "5. Geographic Expansion: Extending location analysis to cover more regions for global workforce insights.\n\n"
        "6. Salary Benchmarking: Deeper salary analysis with experience-adjusted models for fair compensation planning."
    )

    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, "--- End of Report ---", align='C')

    import tempfile as _tmpfile
    tmp_pdf = os.path.join(tmpdir, "report.pdf")
    pdf.output(tmp_pdf, 'F')
    with open(tmp_pdf, 'rb') as _f:
        pdf_bytes = _f.read()

    for f in os.listdir(tmpdir):
        os.remove(os.path.join(tmpdir, f))
    os.rmdir(tmpdir)

    return pdf_bytes
