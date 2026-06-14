import streamlit as st
import os

st.set_page_config(
    page_title="IT Skill Demand Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1f2937;
        text-align: center;
        padding: 0.5rem 0 0.2rem 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748b;
        text-align: center;
        padding-bottom: 1rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📊 IT Skill Demand Analysis Framework</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">NLP & Business Intelligence for Job Market Insights</div>', unsafe_allow_html=True)

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

@st.cache_data
def load_and_process_data(filepath, _mtime=None):
    from nlp_processor import clean_dataset
    df = pd.read_csv(filepath)
    df = clean_dataset(df)
    return df

@st.cache_resource
def get_nlp_module():
    import nlp_processor
    return nlp_processor

def download_plotly_chart(fig, filename, label="Download Chart as PNG", width=1200, height=600, key=None):
    try:
        fig_copy = go.Figure(fig)
        fig_copy.update_layout(width=width, height=height)
        img_bytes = fig_copy.to_image(format="png", scale=2)
        st.download_button(
            label=f"📥 {label}",
            data=img_bytes,
            file_name=filename,
            mime="image/png",
            key=key
        )
    except Exception:
        html_str = fig.to_html(include_plotlyjs="cdn", full_html=True)
        st.download_button(
            label=f"📥 {label} (HTML)",
            data=html_str.encode("utf-8"),
            file_name=filename.replace(".png", ".html"),
            mime="text/html",
            key=key
        )

def download_matplotlib_fig(fig, filename, label="Download Chart as PNG", key=None):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight", facecolor="white")
    buf.seek(0)
    st.download_button(
        label=f"📥 {label}",
        data=buf.getvalue(),
        file_name=filename,
        mime="image/png",
        key=key
    )

def render_metric(label, value, color="#667eea"):
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {color} 0%, #764ba2 100%);
                padding: 1.2rem; border-radius: 0.8rem; color: white; text-align: center; margin-bottom: 0.5rem;">
        <div style="font-size: 1.8rem; font-weight: 700;">{value}</div>
        <div style="font-size: 0.85rem; opacity: 0.9;">{label}</div>
    </div>
    """, unsafe_allow_html=True)

DATA_PATH = "data/it_job_postings.csv"

if not os.path.exists(DATA_PATH):
    st.error("Dataset not found. Generating sample dataset...")
    from generate_dataset import generate_dataset
    os.makedirs("data", exist_ok=True)
    generate_dataset()

df = load_and_process_data(DATA_PATH, _mtime=os.path.getmtime(DATA_PATH))
nlp = get_nlp_module()

with st.sidebar:
    st.header("🔧 Filters")

    years = sorted(df["Year"].dropna().unique().astype(int))
    year_range = st.slider("Year Range", min_value=min(years), max_value=max(years),
                           value=(min(years), max(years)))

    all_roles = sorted(df["Job_Title"].unique())
    selected_roles = st.multiselect("Job Roles", all_roles, default=[])

    all_locations = sorted(df["Location"].unique())
    selected_locations = st.multiselect("Locations", all_locations, default=[])

    all_exp = df["Experience_Level"].unique().tolist()
    selected_exp = st.multiselect("Experience Level", all_exp, default=[])

    st.divider()
    st.header("📥 Export")
    export_placeholder = st.container()

filtered_df = df[
    (df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])
]
if selected_roles:
    filtered_df = filtered_df[filtered_df["Job_Title"].isin(selected_roles)]
if selected_locations:
    filtered_df = filtered_df[filtered_df["Location"].isin(selected_locations)]
if selected_exp:
    filtered_df = filtered_df[filtered_df["Experience_Level"].isin(selected_exp)]

with export_placeholder:
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Cleaned CSV",
        data=csv,
        file_name="cleaned_it_job_postings.csv",
        mime="text/csv",
        key="dl_csv_sidebar"
    )

    filter_key = f"{year_range}_{sorted(selected_roles)}_{sorted(selected_locations)}_{sorted(selected_exp)}"
    if st.button("📥 Generate PDF Report", key="gen_pdf_sidebar"):
        with st.spinner("Preparing PDF report..."):
            from pdf_report import generate_pdf_report
            st.session_state["pdf_data"] = generate_pdf_report(filtered_df)
            st.session_state["pdf_filter_key"] = filter_key

    if "pdf_data" in st.session_state and st.session_state.get("pdf_filter_key") == filter_key:
        st.download_button(
            label="📥 Download PDF Report",
            data=st.session_state["pdf_data"],
            file_name="IT_Skill_Demand_Analysis_Report.pdf",
            mime="application/pdf",
            key="dl_pdf_sidebar"
        )
    elif "pdf_data" in st.session_state:
        st.info("Filters changed. Click 'Generate PDF Report' to update.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric("Total Job Postings", f"{len(filtered_df):,}", "#1f77b4")
with col2:
    unique_skills = set()
    for sl in filtered_df["Skills_List"]:
        unique_skills.update([s.lower() for s in sl])
    render_metric("Unique Skills", f"{len(unique_skills)}", "#ff7f0e")
with col3:
    render_metric("Job Roles", f"{filtered_df['Job_Title'].nunique()}", "#2ca02c")
with col4:
    avg_sal = filtered_df["Salary_INR"].mean()
    render_metric("Avg Salary (INR)", f"₹{avg_sal:,.0f}", "#d62728")

tabs = st.tabs([
    "📈 Skill Trends",
    "☁️ Word Cloud",
    "🎯 Role vs Skills",
    "👔 Experience Analysis",
    "🌍 Location Analysis",
    "💰 Salary Correlation",
    "📉 Declining Skills",
    "🏷️ Skill Taxonomy",
    "📋 Raw Data"
])

with tabs[0]:
    st.subheader("Skill Demand Trends Over Time")
    top_n_trends = st.slider("Number of top skills to show", 5, 20, 10, key="trend_n")
    trend_df = nlp.get_yearly_skill_trends(filtered_df, top_n=top_n_trends)

    if not trend_df.empty:
        fig = px.line(trend_df, x="Year", y="Percentage", color="Skill",
                      title="Top Skill Demand Trends (% of Job Postings)",
                      markers=True,
                      labels={"Percentage": "% of Postings", "Year": "Year"})
        fig.update_layout(height=500, hovermode="x unified",
                          legend=dict(orientation="h", yanchor="bottom", y=-0.4))
        st.plotly_chart(fig, use_container_width=True)
        download_plotly_chart(fig, "skill_demand_trends.png", "Download Trend Line Chart", key="dl_trend1")

        fig2 = px.area(trend_df, x="Year", y="Count", color="Skill",
                       title="Absolute Skill Mention Counts Over Time")
        fig2.update_layout(height=450, legend=dict(orientation="h", yanchor="bottom", y=-0.4))
        st.plotly_chart(fig2, use_container_width=True)
        download_plotly_chart(fig2, "skill_counts_area.png", "Download Area Chart", key="dl_trend2")
    else:
        st.info("No trend data available for the selected filters.")

with tabs[1]:
    st.subheader("Skills Word Cloud")
    skill_freq = nlp.get_skill_frequencies(filtered_df)
    if skill_freq:
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt
        wc = WordCloud(width=1000, height=500, background_color="white",
                       colormap="viridis", max_words=80, prefer_horizontal=0.7,
                       min_font_size=10).generate_from_frequencies(skill_freq)
        fig_wc, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig_wc)
        download_matplotlib_fig(fig_wc, "skills_word_cloud.png", "Download Word Cloud", key="dl_wc")
        plt.close(fig_wc)

        st.subheader("Top Skills by Frequency")
        top_skills_df = pd.DataFrame(skill_freq.most_common(20), columns=["Skill", "Count"])
        fig_bar = px.bar(top_skills_df, x="Count", y="Skill", orientation="h",
                         title="Top 20 Most In-Demand Skills",
                         color="Count", color_continuous_scale="viridis")
        fig_bar.update_layout(height=500, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_bar, use_container_width=True)
        download_plotly_chart(fig_bar, "top_skills_frequency.png", "Download Top Skills Chart", key="dl_topskills")

        st.subheader("TF-IDF Top Keywords from Job Descriptions")
        valid_texts = filtered_df["Processed_Description"][filtered_df["Processed_Description"] != ""]
        if len(valid_texts) > 0:
            tfidf_scores = nlp.compute_tfidf(valid_texts.tolist(), max_features=30)
            tfidf_df = pd.DataFrame(list(tfidf_scores.items()), columns=["Keyword", "TF-IDF Score"])
            fig_tfidf = px.bar(tfidf_df.head(20), x="TF-IDF Score", y="Keyword", orientation="h",
                               title="Top TF-IDF Keywords from Job Descriptions",
                               color="TF-IDF Score", color_continuous_scale="plasma")
            fig_tfidf.update_layout(height=500, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_tfidf, use_container_width=True)
            download_plotly_chart(fig_tfidf, "tfidf_keywords.png", "Download TF-IDF Chart", key="dl_tfidf")
    else:
        st.info("No skill data available.")

with tabs[2]:
    st.subheader("Role vs Skills Matrix")
    n_skills_matrix = st.slider("Number of skills in matrix", 8, 25, 15, key="matrix_n")
    matrix_df = nlp.get_role_skill_matrix(filtered_df, top_n_skills=n_skills_matrix)

    if not matrix_df.empty:
        roles = matrix_df["Role"].tolist()
        skills_cols = [c for c in matrix_df.columns if c != "Role"]
        z_values = matrix_df[skills_cols].values

        fig_heat = go.Figure(data=go.Heatmap(
            z=z_values, x=skills_cols, y=roles,
            colorscale="YlOrRd", text=z_values,
            texttemplate="%{text:.0f}%", textfont={"size": 10},
            hovertemplate="Role: %{y}<br>Skill: %{x}<br>Demand: %{z:.1f}%<extra></extra>"
        ))
        fig_heat.update_layout(
            title="Skill Demand by Job Role (% of postings mentioning each skill)",
            height=600, xaxis_tickangle=-45
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        download_plotly_chart(fig_heat, "role_vs_skills_heatmap.png", "Download Role vs Skills Heatmap", width=1400, height=700, key="dl_heatmap")
    else:
        st.info("No data available for the matrix.")

with tabs[3]:
    st.subheader("Experience Level vs Skill Demand")
    exp_data = nlp.get_experience_skill_data(filtered_df, top_n=12)

    if not exp_data.empty:
        exp_order = ["Fresher (0-1 yrs)", "Junior (1-3 yrs)", "Mid (3-5 yrs)",
                     "Senior (5-8 yrs)", "Lead (8-12 yrs)", "Principal (12+ yrs)"]
        exp_data["Experience"] = pd.Categorical(exp_data["Experience"], categories=exp_order, ordered=True)
        exp_data = exp_data.sort_values("Experience")

        fig_exp = px.bar(exp_data, x="Experience", y="Percentage", color="Skill",
                         barmode="group",
                         title="Skill Demand by Experience Level",
                         labels={"Percentage": "% of Postings"})
        fig_exp.update_layout(height=500, legend=dict(orientation="h", yanchor="bottom", y=-0.5))
        st.plotly_chart(fig_exp, use_container_width=True)
        download_plotly_chart(fig_exp, "experience_skill_demand.png", "Download Experience Chart", key="dl_exp")

        st.subheader("Fresher vs Senior Skill Comparison")
        fresher_df = filtered_df[filtered_df["Experience_Level"] == "Fresher (0-1 yrs)"]
        senior_df = filtered_df[filtered_df["Experience_Level"].isin(["Senior (5-8 yrs)", "Lead (8-12 yrs)", "Principal (12+ yrs)"])]

        fresher_skills = []
        for sl in fresher_df["Skills_List"]:
            fresher_skills.extend([s.lower() for s in sl])
        senior_skills = []
        for sl in senior_df["Skills_List"]:
            senior_skills.extend([s.lower() for s in sl])

        from collections import Counter
        f_counter = Counter(fresher_skills)
        s_counter = Counter(senior_skills)
        all_skills_set = set(list(f_counter.keys())[:15] + list(s_counter.keys())[:15])

        comparison = []
        for skill in all_skills_set:
            comparison.append({"Skill": skill.title(),
                               "Fresher %": round(f_counter.get(skill, 0) / max(len(fresher_df), 1) * 100, 1),
                               "Senior %": round(s_counter.get(skill, 0) / max(len(senior_df), 1) * 100, 1)})
        comp_df = pd.DataFrame(comparison).sort_values("Fresher %", ascending=False).head(15)

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(name="Fresher", x=comp_df["Skill"], y=comp_df["Fresher %"], marker_color="#1f77b4"))
        fig_comp.add_trace(go.Bar(name="Senior+", x=comp_df["Skill"], y=comp_df["Senior %"], marker_color="#ff7f0e"))
        fig_comp.update_layout(barmode="group", title="Fresher vs Senior+ Skill Requirements",
                               height=450, yaxis_title="% of Postings")
        st.plotly_chart(fig_comp, use_container_width=True)
        download_plotly_chart(fig_comp, "fresher_vs_senior.png", "Download Fresher vs Senior Chart", key="dl_comp")
    else:
        st.info("No experience data available.")

with tabs[4]:
    st.subheader("Location-Based Skill Demand")
    loc_data = nlp.get_location_skill_data(filtered_df, top_n=10)

    if not loc_data.empty:
        loc_job_counts = filtered_df["Location"].value_counts().reset_index()
        loc_job_counts.columns = ["Location", "Job_Count"]
        fig_loc_bar = px.bar(loc_job_counts, x="Location", y="Job_Count",
                             title="Job Postings by Location",
                             color="Job_Count", color_continuous_scale="blues")
        fig_loc_bar.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_loc_bar, use_container_width=True)
        download_plotly_chart(fig_loc_bar, "jobs_by_location.png", "Download Location Bar Chart", key="dl_locbar")

        selected_loc = st.selectbox("Select a location to see top skills",
                                    sorted(filtered_df["Location"].unique()))
        loc_specific = loc_data[loc_data["Location"] == selected_loc].sort_values("Percentage", ascending=False)
        if not loc_specific.empty:
            fig_loc_skill = px.bar(loc_specific, x="Percentage", y="Skill", orientation="h",
                                   title=f"Top Skills in {selected_loc}",
                                   color="Percentage", color_continuous_scale="teal")
            fig_loc_skill.update_layout(height=400, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_loc_skill, use_container_width=True)
            download_plotly_chart(fig_loc_skill, "location_top_skills.png", "Download Location Skills Chart", key="dl_locskill")

        st.subheader("Location vs Skill Heatmap")
        loc_pivot = loc_data.pivot_table(values="Percentage", index="Location", columns="Skill", fill_value=0)
        fig_loc_heat = go.Figure(data=go.Heatmap(
            z=loc_pivot.values, x=loc_pivot.columns.tolist(), y=loc_pivot.index.tolist(),
            colorscale="Teal",
            hovertemplate="Location: %{y}<br>Skill: %{x}<br>Demand: %{z:.1f}%<extra></extra>"
        ))
        fig_loc_heat.update_layout(title="Skill Demand Across Locations", height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig_loc_heat, use_container_width=True)
        download_plotly_chart(fig_loc_heat, "location_skill_heatmap.png", "Download Location Heatmap", width=1400, height=600, key="dl_locheat")
    else:
        st.info("No location data available.")

with tabs[5]:
    st.subheader("Salary vs Skill Correlation")
    salary_data = nlp.get_salary_skill_correlation(filtered_df, top_n=20)

    if not salary_data.empty:
        fig_sal = px.bar(salary_data, x="Skill", y="Avg_Salary",
                         title="Average Salary by Skill (INR)",
                         color="Avg_Salary", color_continuous_scale="reds",
                         hover_data=["Median_Salary", "Job_Count"])
        fig_sal.update_layout(height=500, xaxis_tickangle=-45,
                              yaxis_title="Average Salary (INR)")
        st.plotly_chart(fig_sal, use_container_width=True)
        download_plotly_chart(fig_sal, "salary_by_skill.png", "Download Salary Bar Chart", key="dl_sal")

        fig_bubble = px.scatter(salary_data, x="Job_Count", y="Avg_Salary",
                                size="Job_Count", color="Skill",
                                title="Skill Demand vs Salary (Bubble Chart)",
                                hover_data=["Median_Salary"],
                                labels={"Job_Count": "Number of Jobs", "Avg_Salary": "Avg Salary (INR)"})
        fig_bubble.update_layout(height=500)
        st.plotly_chart(fig_bubble, use_container_width=True)
        download_plotly_chart(fig_bubble, "salary_vs_demand_bubble.png", "Download Bubble Chart", key="dl_bubble")
    else:
        st.info("No salary data available.")

with tabs[6]:
    st.subheader("Declining & Rising Technologies")
    decline_df = nlp.detect_declining_skills(filtered_df)

    if not decline_df.empty:
        st.markdown("**Top Declining Skills** (comparing earlier years to recent years)")
        declining = decline_df.head(10)
        fig_dec = px.bar(declining, x="Skill", y="Change_%",
                         title="Most Declining Skills (Negative = Declining)",
                         color="Change_%", color_continuous_scale="RdYlGn")
        fig_dec.update_layout(height=400, yaxis_title="Change in Demand (%)")
        st.plotly_chart(fig_dec, use_container_width=True)
        download_plotly_chart(fig_dec, "declining_skills.png", "Download Declining Skills Chart", key="dl_dec")

        st.markdown("**Top Rising Skills**")
        rising = decline_df.tail(10).sort_values("Change_%", ascending=False)
        fig_rise = px.bar(rising, x="Skill", y="Change_%",
                          title="Most Rising Skills (Positive = Growing)",
                          color="Change_%", color_continuous_scale="RdYlGn")
        fig_rise.update_layout(height=400, yaxis_title="Change in Demand (%)")
        st.plotly_chart(fig_rise, use_container_width=True)
        download_plotly_chart(fig_rise, "rising_skills.png", "Download Rising Skills Chart", key="dl_rise")

        st.dataframe(decline_df.style.background_gradient(subset=["Change_%"], cmap="RdYlGn"), use_container_width=True)
    else:
        st.info("Not enough data to detect trends.")

with tabs[7]:
    st.subheader("Structured Skill Taxonomy")
    cat_counts = nlp.get_skill_category_counts(filtered_df)

    if cat_counts:
        cat_df = pd.DataFrame(list(cat_counts.items()), columns=["Category", "Count"]).sort_values("Count", ascending=False)
        fig_cat = px.pie(cat_df, values="Count", names="Category",
                         title="Skill Distribution by Category",
                         color_discrete_sequence=px.colors.qualitative.Set3)
        fig_cat.update_traces(textposition='inside', textinfo='percent+label')
        fig_cat.update_layout(height=500)
        st.plotly_chart(fig_cat, use_container_width=True)
        download_plotly_chart(fig_cat, "skill_taxonomy_pie.png", "Download Taxonomy Pie Chart", key="dl_catpie")

        fig_cat_bar = px.bar(cat_df, x="Category", y="Count",
                             title="Skill Category Frequency",
                             color="Category", color_discrete_sequence=px.colors.qualitative.Set2)
        fig_cat_bar.update_layout(height=400, xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig_cat_bar, use_container_width=True)
        download_plotly_chart(fig_cat_bar, "skill_category_frequency.png", "Download Category Bar Chart", key="dl_catbar")

        st.subheader("Taxonomy Details")
        for category, skills in nlp.SKILL_TAXONOMY.items():
            with st.expander(f"📂 {category} ({len(skills)} skills)"):
                st.write(", ".join([s.title() for s in skills]))
    else:
        st.info("No taxonomy data available.")

with tabs[8]:
    st.subheader("Raw Dataset Explorer")
    st.dataframe(filtered_df[["Job_ID", "Job_Title", "Skills", "Experience_Level",
                               "Location", "Salary_INR", "Posting_Date"]].head(500),
                 use_container_width=True, height=500)

    st.subheader("Dataset Statistics")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Job Title Distribution**")
        title_counts = filtered_df["Job_Title"].value_counts()
        st.dataframe(title_counts, use_container_width=True)
    with col_b:
        st.markdown("**Experience Level Distribution**")
        exp_counts = filtered_df["Experience_Level"].value_counts()
        st.dataframe(exp_counts, use_container_width=True)
