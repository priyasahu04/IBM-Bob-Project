"""
HR Employee Analytics Dashboard
Author: Priya Sahu
Description: Complete descriptive analytics dashboard for HR Employee Data
             including data understanding, cleaning, transformation, KPI calculation,
             visualizations, and business insights.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="HR Employee Analytics",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #f4f6fb; }

    /* KPI card */
    .kpi-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        border-left: 5px solid #3b82f6;
        margin-bottom: 8px;
    }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #1e3a5f; }
    .kpi-label { font-size: 0.85rem; color: #64748b; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }

    /* Accent colours for KPI borders */
    .kpi-red   { border-left-color: #ef4444 !important; }
    .kpi-green { border-left-color: #22c55e !important; }
    .kpi-amber { border-left-color: #f59e0b !important; }
    .kpi-blue  { border-left-color: #3b82f6 !important; }
    .kpi-purple{ border-left-color: #8b5cf6 !important; }
    .kpi-teal  { border-left-color: #14b8a6 !important; }

    /* Section header */
    .section-header {
        font-size: 1.15rem; font-weight: 600; color: #1e3a5f;
        margin: 18px 0 8px 0; padding-bottom: 6px;
        border-bottom: 2px solid #e2e8f0;
    }

    /* Insight box */
    .insight-box {
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 10px;
        color: #1e40af;
        font-size: 0.9rem;
    }
    .warning-box {
        background: #fff7ed;
        border-left: 4px solid #f59e0b;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 10px;
        color: #92400e;
        font-size: 0.9rem;
    }
    .success-box {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 10px;
        color: #14532d;
        font-size: 0.9rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #1e3a5f; }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label { color: #94a3b8 !important; font-size: 0.78rem; }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 1. DATA LOADING & UNDERSTANDING
# ─────────────────────────────────────────────
@st.cache_data
def load_and_clean_data():
    """Load, clean, and transform HR Employee data."""
    df = pd.read_csv("HR_Employee_Data.csv")

    # ── Data Understanding ──────────────────
    # Columns: Emp_Id, satisfaction_level, last_evaluation, number_project,
    #          average_montly_hours, time_spend_company, Work_accident,
    #          left, promotion_last_5years, Department, salary

    # ── Data Cleaning ───────────────────────
    # Strip whitespace from string columns
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # Convert percentage strings to float (0-1)
    for col in ["satisfaction_level", "last_evaluation"]:
        if df[col].dtype == object:
            df[col] = df[col].str.replace("%", "", regex=False).astype(float) / 100

    # Ensure numeric types
    numeric_cols = ["number_project", "average_montly_hours",
                    "time_spend_company", "Work_accident", "left",
                    "promotion_last_5years"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop duplicates
    df = df.drop_duplicates()

    # Fill missing with median / mode
    for col in ["satisfaction_level", "last_evaluation",
                "number_project", "average_montly_hours", "time_spend_company"]:
        df[col] = df[col].fillna(df[col].median())

    df["Department"] = df["Department"].fillna(df["Department"].mode()[0])
    df["salary"] = df["salary"].fillna(df["salary"].mode()[0])

    # ── Data Transformation ─────────────────
    # Salary ordinal encoding
    salary_map = {"low": 1, "medium": 2, "high": 3}
    df["salary_encoded"] = df["salary"].str.lower().map(salary_map)

    # Attrition label
    df["Attrition"] = df["left"].map({1: "Left", 0: "Stayed"})

    # Satisfaction buckets
    df["Satisfaction_Group"] = pd.cut(
        df["satisfaction_level"],
        bins=[0, 0.30, 0.60, 1.0],
        labels=["Low (0-30%)", "Medium (30-60%)", "High (60-100%)"],
    )

    # Experience buckets
    df["Experience_Group"] = pd.cut(
        df["time_spend_company"],
        bins=[0, 2, 4, 6, 100],
        labels=["Junior (≤2 yr)", "Mid (3-4 yr)", "Senior (5-6 yr)", "Veteran (>6 yr)"],
    )

    # Workload category based on monthly hours
    df["Workload"] = pd.cut(
        df["average_montly_hours"],
        bins=[0, 160, 220, 320],
        labels=["Normal", "High", "Overloaded"],
    )

    # Department title-case
    df["Department"] = df["Department"].str.title()

    # Promotion flag
    df["Promoted"] = df["promotion_last_5years"].map({1: "Promoted", 0: "Not Promoted"})

    # Work accident flag
    df["Accident"] = df["Work_accident"].map({1: "Had Accident", 0: "No Accident"})

    return df


df_raw = load_and_clean_data()

# ─────────────────────────────────────────────
# SIDEBAR — FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 👥 HR Analytics")
    st.markdown("---")
    st.markdown("### 🔍 Filters")

    departments = sorted(df_raw["Department"].unique())
    sel_dept = st.multiselect("Department", departments, default=departments,
                               help="Filter by department")

    salary_levels = ["low", "medium", "high"]
    sel_salary = st.multiselect("Salary Level", salary_levels, default=salary_levels)

    attrition_opts = ["Left", "Stayed"]
    sel_attr = st.multiselect("Attrition Status", attrition_opts, default=attrition_opts)

    satisfaction_range = st.slider(
        "Satisfaction Level (%)",
        min_value=0, max_value=100, value=(0, 100), step=5
    )

    experience_range = st.slider(
        "Years at Company",
        min_value=int(df_raw["time_spend_company"].min()),
        max_value=int(df_raw["time_spend_company"].max()),
        value=(int(df_raw["time_spend_company"].min()),
               int(df_raw["time_spend_company"].max()))
    )

    st.markdown("---")
    st.markdown("**Dataset:** HR Employee Data")
    st.markdown("**Records:** 14,999")
    st.markdown("**Features:** 11")
    st.markdown("---")
    st.caption("© 2024 Priya Sahu · HR Analytics")

# ── Apply filters ───────────────────────────
df = df_raw[
    (df_raw["Department"].isin(sel_dept)) &
    (df_raw["salary"].str.lower().isin(sel_salary)) &
    (df_raw["Attrition"].isin(sel_attr)) &
    (df_raw["satisfaction_level"] >= satisfaction_range[0] / 100) &
    (df_raw["satisfaction_level"] <= satisfaction_range[1] / 100) &
    (df_raw["time_spend_company"] >= experience_range[0]) &
    (df_raw["time_spend_company"] <= experience_range[1])
].copy()

# ─────────────────────────────────────────────
# TITLE
# ─────────────────────────────────────────────
st.markdown("""
<div style='background:#1e3a5f;padding:24px 30px 18px 30px;border-radius:14px;margin-bottom:20px;'>
  <h1 style='color:#ffffff;margin:0;font-size:1.9rem;'>👥 HR Employee Analytics Dashboard</h1>
  <p style='color:#93c5fd;margin:6px 0 0 0;font-size:0.95rem;'>
    Descriptive Analytics · Attrition · Satisfaction · Workload · Promotions
  </p>
</div>
""", unsafe_allow_html=True)

if len(df) == 0:
    st.warning("No records match the current filter selection. Please adjust the filters.")
    st.stop()

# ─────────────────────────────────────────────
# 2. KPI CARDS
# ─────────────────────────────────────────────
st.markdown('<p class="section-header">📊 Key Performance Indicators</p>', unsafe_allow_html=True)

total_emp      = len(df)
left_emp       = (df["left"] == 1).sum()
attrition_rate = round(left_emp / total_emp * 100, 1)
avg_satisfaction = round(df["satisfaction_level"].mean() * 100, 1)
avg_evaluation   = round(df["last_evaluation"].mean() * 100, 1)
avg_hours        = round(df["average_montly_hours"].mean(), 0)
avg_tenure       = round(df["time_spend_company"].mean(), 1)
promotion_rate   = round((df["promotion_last_5years"] == 1).sum() / total_emp * 100, 1)
accident_rate    = round((df["Work_accident"] == 1).sum() / total_emp * 100, 1)

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(f"""
    <div class="kpi-card kpi-blue">
        <div class="kpi-value">{total_emp:,}</div>
        <div class="kpi-label">Total Employees</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card kpi-red">
        <div class="kpi-value">{attrition_rate}%</div>
        <div class="kpi-label">Attrition Rate</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card kpi-green">
        <div class="kpi-value">{avg_satisfaction}%</div>
        <div class="kpi-label">Avg Satisfaction</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card kpi-amber">
        <div class="kpi-value">{avg_hours:.0f}h</div>
        <div class="kpi-label">Avg Monthly Hours</div>
    </div>""", unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="kpi-card kpi-purple">
        <div class="kpi-value">{avg_tenure}yr</div>
        <div class="kpi-label">Avg Tenure</div>
    </div>""", unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div class="kpi-card kpi-teal">
        <div class="kpi-value">{promotion_rate}%</div>
        <div class="kpi-label">Promotion Rate</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 3. TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📉 Attrition Analysis",
    "🏢 Department Analysis",
    "💰 Salary Analysis",
    "😊 Satisfaction & Workload",
    "📈 Experience & Promotion",
    "💡 Business Insights",
])

COLORS = px.colors.qualitative.Set2
ATTRITION_COLOR = {"Left": "#ef4444", "Stayed": "#22c55e"}

# ─────────────────────────────────────────────
# TAB 1: ATTRITION ANALYSIS
# ─────────────────────────────────────────────
with tab1:
    st.markdown('<p class="section-header">📉 Attrition Analysis</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    # Pie chart
    with c1:
        attr_counts = df["Attrition"].value_counts().reset_index()
        attr_counts.columns = ["Status", "Count"]
        fig = px.pie(attr_counts, names="Status", values="Count",
                     color="Status", color_discrete_map=ATTRITION_COLOR,
                     title="Overall Attrition Distribution",
                     hole=0.45)
        fig.update_traces(textposition="outside", textinfo="percent+label")
        fig.update_layout(showlegend=False, height=350, margin=dict(t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # Attrition by salary
    with c2:
        sal_attr = df.groupby(["salary", "Attrition"]).size().reset_index(name="Count")
        sal_attr["salary"] = sal_attr["salary"].str.capitalize()
        fig2 = px.bar(sal_attr, x="salary", y="Count", color="Attrition",
                      color_discrete_map=ATTRITION_COLOR, barmode="group",
                      title="Attrition by Salary Level",
                      category_orders={"salary": ["Low", "Medium", "High"]},
                      labels={"salary": "Salary Level", "Count": "Employees"})
        fig2.update_layout(height=350, margin=dict(t=50, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)

    # Attrition by department
    with c3:
        dept_attr = df.groupby(["Department", "Attrition"]).size().reset_index(name="Count")
        dept_total = dept_attr.groupby("Department")["Count"].transform("sum")
        dept_attr["Rate"] = (dept_attr["Count"] / dept_total * 100).round(1)
        left_dept = dept_attr[dept_attr["Attrition"] == "Left"].sort_values("Rate", ascending=True)
        fig3 = px.bar(left_dept, x="Rate", y="Department", orientation="h",
                      title="Attrition Rate by Department (%)",
                      color="Rate",
                      color_continuous_scale="Reds",
                      labels={"Rate": "Attrition Rate (%)"})
        fig3.update_layout(height=370, margin=dict(t=50, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    # Attrition by experience group
    with c4:
        exp_attr = df.groupby(["Experience_Group", "Attrition"]).size().reset_index(name="Count")
        fig4 = px.bar(exp_attr, x="Experience_Group", y="Count", color="Attrition",
                      color_discrete_map=ATTRITION_COLOR, barmode="stack",
                      title="Attrition by Experience Group",
                      labels={"Experience_Group": "Experience", "Count": "Employees"})
        fig4.update_layout(height=370, margin=dict(t=50, b=10))
        st.plotly_chart(fig4, use_container_width=True)

    # Satisfaction vs Evaluation scatter
    st.markdown('<p class="section-header">Satisfaction vs. Last Evaluation (by Attrition)</p>', unsafe_allow_html=True)
    sample = df.sample(min(3000, len(df)), random_state=42)
    fig5 = px.scatter(sample, x="satisfaction_level", y="last_evaluation",
                      color="Attrition", color_discrete_map=ATTRITION_COLOR,
                      opacity=0.55,
                      labels={"satisfaction_level": "Satisfaction Level",
                              "last_evaluation": "Last Evaluation Score"},
                      title="Satisfaction vs Evaluation — Attrition Clusters",
                      size_max=5)
    fig5.update_layout(height=400, margin=dict(t=50, b=10))
    st.plotly_chart(fig5, use_container_width=True)


# ─────────────────────────────────────────────
# TAB 2: DEPARTMENT ANALYSIS
# ─────────────────────────────────────────────
with tab2:
    st.markdown('<p class="section-header">🏢 Department Analysis</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        dept_count = df["Department"].value_counts().reset_index()
        dept_count.columns = ["Department", "Count"]
        fig = px.bar(dept_count, x="Count", y="Department", orientation="h",
                     color="Department", title="Employee Count by Department",
                     color_discrete_sequence=COLORS)
        fig.update_layout(height=380, showlegend=False, margin=dict(t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        dept_metrics = df.groupby("Department").agg(
            Avg_Satisfaction=("satisfaction_level", "mean"),
            Avg_Evaluation=("last_evaluation", "mean"),
            Avg_Hours=("average_montly_hours", "mean"),
        ).reset_index()
        dept_metrics["Avg_Satisfaction"] = (dept_metrics["Avg_Satisfaction"] * 100).round(1)
        dept_metrics["Avg_Evaluation"] = (dept_metrics["Avg_Evaluation"] * 100).round(1)
        dept_metrics["Avg_Hours"] = dept_metrics["Avg_Hours"].round(0)

        fig2 = px.bar(dept_metrics, x="Department", y="Avg_Satisfaction",
                      color="Department", title="Avg Satisfaction by Department (%)",
                      color_discrete_sequence=COLORS,
                      labels={"Avg_Satisfaction": "Avg Satisfaction (%)"})
        fig2.update_layout(height=380, showlegend=False, margin=dict(t=50, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    # Radar chart per department
    st.markdown('<p class="section-header">Department Performance Radar</p>', unsafe_allow_html=True)
    dept_metrics_norm = dept_metrics.copy()
    metrics = ["Avg_Satisfaction", "Avg_Evaluation"]
    for m in metrics:
        dept_metrics_norm[m + "_n"] = (dept_metrics_norm[m] - dept_metrics_norm[m].min()) / \
                                       (dept_metrics_norm[m].max() - dept_metrics_norm[m].min() + 1e-9)

    fig3 = go.Figure()
    categories = ["Satisfaction", "Evaluation"]
    for _, row in dept_metrics_norm.iterrows():
        fig3.add_trace(go.Scatterpolar(
            r=[row["Avg_Satisfaction_n"], row["Avg_Evaluation_n"]],
            theta=categories,
            fill="toself",
            name=row["Department"],
        ))
    fig3.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                       showlegend=True, height=420, title="Normalised Dept. Performance")
    st.plotly_chart(fig3, use_container_width=True)

    # Department table
    st.markdown('<p class="section-header">Department Summary Table</p>', unsafe_allow_html=True)
    dept_full = df.groupby("Department").agg(
        Employees=("Emp_Id", "count"),
        Avg_Satisfaction=("satisfaction_level", lambda x: f"{x.mean()*100:.1f}%"),
        Avg_Evaluation=("last_evaluation", lambda x: f"{x.mean()*100:.1f}%"),
        Avg_Monthly_Hours=("average_montly_hours", lambda x: f"{x.mean():.0f}"),
        Attrition_Rate=("left", lambda x: f"{x.mean()*100:.1f}%"),
        Promotion_Rate=("promotion_last_5years", lambda x: f"{x.mean()*100:.1f}%"),
    ).reset_index()
    st.dataframe(dept_full, use_container_width=True)


# ─────────────────────────────────────────────
# TAB 3: SALARY ANALYSIS
# ─────────────────────────────────────────────
with tab3:
    st.markdown('<p class="section-header">💰 Salary Analysis</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        sal_dist = df["salary"].str.capitalize().value_counts().reset_index()
        sal_dist.columns = ["Salary", "Count"]
        order = ["Low", "Medium", "High"]
        sal_dist["Salary"] = pd.Categorical(sal_dist["Salary"], categories=order, ordered=True)
        sal_dist = sal_dist.sort_values("Salary")
        fig = px.bar(sal_dist, x="Salary", y="Count",
                     color="Salary",
                     color_discrete_map={"Low": "#ef4444", "Medium": "#f59e0b", "High": "#22c55e"},
                     title="Employee Distribution by Salary Level",
                     labels={"Count": "Number of Employees"})
        fig.update_layout(height=360, showlegend=False, margin=dict(t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        sal_sat = df.groupby("salary").agg(
            Satisfaction=("satisfaction_level", lambda x: round(x.mean() * 100, 1)),
            Evaluation=("last_evaluation", lambda x: round(x.mean() * 100, 1)),
        ).reset_index()
        sal_sat["salary"] = pd.Categorical(sal_sat["salary"].str.capitalize(),
                                            categories=["Low", "Medium", "High"], ordered=True)
        sal_sat = sal_sat.sort_values("salary")
        fig2 = px.line(sal_sat, x="salary", y=["Satisfaction", "Evaluation"],
                       markers=True, title="Satisfaction & Evaluation vs Salary",
                       labels={"salary": "Salary Level", "value": "Score (%)", "variable": "Metric"})
        fig2.update_layout(height=360, margin=dict(t=50, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        sal_dept = df.groupby(["Department", "salary"]).size().reset_index(name="Count")
        sal_dept["salary"] = sal_dept["salary"].str.capitalize()
        fig3 = px.bar(sal_dept, x="Department", y="Count", color="salary",
                      barmode="stack",
                      color_discrete_map={"Low": "#ef4444", "Medium": "#f59e0b", "High": "#22c55e"},
                      title="Salary Distribution Across Departments",
                      labels={"Count": "Employees", "salary": "Salary"})
        fig3.update_layout(height=380, margin=dict(t=50, b=10),
                           xaxis_tickangle=-35)
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        sal_attr = df.groupby("salary")["left"].mean().reset_index()
        sal_attr["Attrition_Rate"] = (sal_attr["left"] * 100).round(1)
        sal_attr["salary"] = pd.Categorical(sal_attr["salary"].str.capitalize(),
                                             categories=["Low", "Medium", "High"], ordered=True)
        sal_attr = sal_attr.sort_values("salary")
        fig4 = px.bar(sal_attr, x="salary", y="Attrition_Rate",
                      color="Attrition_Rate",
                      color_continuous_scale="Reds",
                      title="Attrition Rate by Salary Level (%)",
                      labels={"salary": "Salary Level", "Attrition_Rate": "Attrition Rate (%)"})
        fig4.update_layout(height=380, margin=dict(t=50, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig4, use_container_width=True)


# ─────────────────────────────────────────────
# TAB 4: SATISFACTION & WORKLOAD
# ─────────────────────────────────────────────
with tab4:
    st.markdown('<p class="section-header">😊 Satisfaction & Workload Analysis</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        fig = px.histogram(df, x="satisfaction_level", nbins=30,
                           color="Attrition", color_discrete_map=ATTRITION_COLOR,
                           barmode="overlay", opacity=0.7,
                           title="Satisfaction Level Distribution",
                           labels={"satisfaction_level": "Satisfaction Level"})
        fig.update_layout(height=360, margin=dict(t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        work_attr = df.groupby(["Workload", "Attrition"]).size().reset_index(name="Count")
        fig2 = px.bar(work_attr, x="Workload", y="Count", color="Attrition",
                      color_discrete_map=ATTRITION_COLOR, barmode="group",
                      title="Workload Category vs Attrition",
                      labels={"Workload": "Workload Level", "Count": "Employees"})
        fig2.update_layout(height=360, margin=dict(t=50, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        sat_grp = df.groupby("Satisfaction_Group")["left"].mean().reset_index()
        sat_grp["Attrition_Rate"] = (sat_grp["left"] * 100).round(1)
        fig3 = px.bar(sat_grp, x="Satisfaction_Group", y="Attrition_Rate",
                      color="Attrition_Rate",
                      color_continuous_scale="RdYlGn_r",
                      title="Attrition Rate by Satisfaction Group (%)",
                      labels={"Satisfaction_Group": "Satisfaction", "Attrition_Rate": "Attrition Rate (%)"})
        fig3.update_layout(height=360, margin=dict(t=50, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        fig4 = px.box(df, x="Attrition", y="average_montly_hours",
                      color="Attrition", color_discrete_map=ATTRITION_COLOR,
                      title="Monthly Hours Distribution by Attrition",
                      labels={"average_montly_hours": "Monthly Hours"})
        fig4.update_layout(height=360, margin=dict(t=50, b=10), showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    # Heatmap: Satisfaction vs Number of Projects
    st.markdown('<p class="section-header">Avg Satisfaction by Projects & Tenure</p>', unsafe_allow_html=True)
    heatmap_data = df.groupby(["number_project", "time_spend_company"])["satisfaction_level"] \
                     .mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index="time_spend_company",
                                        columns="number_project",
                                        values="satisfaction_level")
    fig5 = px.imshow(heatmap_pivot, color_continuous_scale="RdYlGn",
                     title="Avg Satisfaction Level: Tenure (rows) × Projects (cols)",
                     labels=dict(x="Number of Projects", y="Years at Company",
                                 color="Avg Satisfaction"),
                     aspect="auto")
    fig5.update_layout(height=380, margin=dict(t=50, b=10))
    st.plotly_chart(fig5, use_container_width=True)


# ─────────────────────────────────────────────
# TAB 5: EXPERIENCE & PROMOTION
# ─────────────────────────────────────────────
with tab5:
    st.markdown('<p class="section-header">📈 Experience & Promotion Analysis</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        exp_dist = df["Experience_Group"].value_counts().reset_index()
        exp_dist.columns = ["Experience", "Count"]
        fig = px.pie(exp_dist, names="Experience", values="Count",
                     title="Workforce Experience Distribution",
                     color_discrete_sequence=COLORS, hole=0.4)
        fig.update_traces(textposition="outside", textinfo="percent+label")
        fig.update_layout(height=360, showlegend=False, margin=dict(t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        prom_attr = df.groupby(["Promoted", "Attrition"]).size().reset_index(name="Count")
        fig2 = px.bar(prom_attr, x="Promoted", y="Count", color="Attrition",
                      color_discrete_map=ATTRITION_COLOR, barmode="group",
                      title="Attrition by Promotion Status",
                      labels={"Promoted": "Promotion Status", "Count": "Employees"})
        fig2.update_layout(height=360, margin=dict(t=50, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        tenure_attr = df.groupby("time_spend_company")["left"].mean().reset_index()
        tenure_attr["Attrition_Rate"] = (tenure_attr["left"] * 100).round(1)
        fig3 = px.line(tenure_attr, x="time_spend_company", y="Attrition_Rate",
                       markers=True,
                       title="Attrition Rate by Years at Company",
                       labels={"time_spend_company": "Years at Company",
                               "Attrition_Rate": "Attrition Rate (%)"})
        fig3.update_traces(line_color="#ef4444")
        fig3.update_layout(height=360, margin=dict(t=50, b=10))
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        proj_sat = df.groupby("number_project").agg(
            Avg_Satisfaction=("satisfaction_level", lambda x: round(x.mean() * 100, 1)),
            Attrition_Rate=("left", lambda x: round(x.mean() * 100, 1))
        ).reset_index()
        fig4 = make_subplots(specs=[[{"secondary_y": True}]])
        fig4.add_trace(
            go.Bar(x=proj_sat["number_project"], y=proj_sat["Avg_Satisfaction"],
                   name="Avg Satisfaction (%)", marker_color="#3b82f6"),
            secondary_y=False
        )
        fig4.add_trace(
            go.Scatter(x=proj_sat["number_project"], y=proj_sat["Attrition_Rate"],
                       name="Attrition Rate (%)", mode="lines+markers",
                       line=dict(color="#ef4444", width=2)),
            secondary_y=True
        )
        fig4.update_layout(title="Projects: Satisfaction & Attrition", height=360,
                           margin=dict(t=50, b=10))
        fig4.update_xaxes(title_text="Number of Projects")
        fig4.update_yaxes(title_text="Avg Satisfaction (%)", secondary_y=False)
        fig4.update_yaxes(title_text="Attrition Rate (%)", secondary_y=True)
        st.plotly_chart(fig4, use_container_width=True)

    # Promotion rate by department
    st.markdown('<p class="section-header">Promotion Rate by Department</p>', unsafe_allow_html=True)
    prom_dept = df.groupby("Department")["promotion_last_5years"].mean().reset_index()
    prom_dept["Promotion_Rate"] = (prom_dept["promotion_last_5years"] * 100).round(2)
    prom_dept = prom_dept.sort_values("Promotion_Rate", ascending=True)
    fig5 = px.bar(prom_dept, x="Promotion_Rate", y="Department", orientation="h",
                  color="Promotion_Rate", color_continuous_scale="Blues",
                  title="Promotion Rate by Department (%)",
                  labels={"Promotion_Rate": "Promotion Rate (%)"})
    fig5.update_layout(height=380, margin=dict(t=50, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig5, use_container_width=True)


# ─────────────────────────────────────────────
# TAB 6: BUSINESS INSIGHTS
# ─────────────────────────────────────────────
with tab6:
    st.markdown('<p class="section-header">💡 Key Findings & HR Business Insights</p>', unsafe_allow_html=True)

    # Compute dynamic insights
    top_attrition_dept = df.groupby("Department")["left"].mean().idxmax()
    top_attrition_pct  = round(df.groupby("Department")["left"].mean().max() * 100, 1)
    low_sat_pct = round((df["satisfaction_level"] < 0.3).mean() * 100, 1)
    overload_pct = round((df["Workload"] == "Overloaded").mean() * 100, 1)
    low_sal_attr = round(df[df["salary"] == "low"]["left"].mean() * 100, 1)
    high_sal_attr = round(df[df["salary"] == "high"]["left"].mean() * 100, 1)
    promoted_attr = round(df[df["promotion_last_5years"] == 1]["left"].mean() * 100, 1)
    not_promoted_attr = round(df[df["promotion_last_5years"] == 0]["left"].mean() * 100, 1)
    yr3_attr = round(df[df["time_spend_company"] == 3]["left"].mean() * 100, 1)

    st.markdown("### 🔑 Key Findings")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="warning-box">
            <strong>⚠️ High Overall Attrition</strong><br>
            {attrition_rate}% of employees have left — significantly above the industry benchmark of ~15%.
            Immediate retention strategies are required.
        </div>
        <div class="warning-box">
            <strong>⚠️ Low Satisfaction is a Key Driver</strong><br>
            {low_sat_pct}% of employees report satisfaction below 30%. 
            Low satisfaction strongly correlates with attrition across all departments.
        </div>
        <div class="warning-box">
            <strong>⚠️ {top_attrition_dept} Department at Risk</strong><br>
            {top_attrition_dept} has the highest attrition rate at {top_attrition_pct}%.
            Focused interventions in this department are critical.
        </div>
        <div class="warning-box">
            <strong>⚠️ Salary and Retention Strongly Linked</strong><br>
            Low-salary employees leave at {low_sal_attr}% vs {high_sal_attr}% for high-salary employees —
            a {round(low_sal_attr - high_sal_attr, 1)}pp gap indicating compensation is a major lever.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="insight-box">
            <strong>📌 Workload & Burnout Risk</strong><br>
            {overload_pct}% of employees work in "Overloaded" hours (>220 hrs/month).
            High workload clusters strongly with employees who eventually leave.
        </div>
        <div class="insight-box">
            <strong>📌 Promotions Reduce Attrition</strong><br>
            Promoted employees leave at {promoted_attr}% vs {not_promoted_attr}% for non-promoted —
            career growth is a powerful retention factor.
        </div>
        <div class="insight-box">
            <strong>📌 Critical Tenure Risk at Year 3</strong><br>
            Employees at the 3-year mark show an attrition rate of {yr3_attr}%.
            This is the highest-risk tenure point and needs proactive engagement.
        </div>
        <div class="success-box">
            <strong>✅ High Evaluators Can Stay with Right Conditions</strong><br>
            Many highly evaluated employees still leave, suggesting performance alone is 
            insufficient — satisfaction, compensation, and growth must also be addressed.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🏢 HR Business Recommendations")

    rec_data = {
        "Priority": ["🔴 Critical", "🔴 Critical", "🟠 High", "🟠 High",
                     "🟡 Medium", "🟡 Medium", "🟢 Ongoing"],
        "Recommendation": [
            "Implement retention bonuses & compensation review for low-salary employees",
            f"Launch a targeted engagement programme for {top_attrition_dept} department",
            "Introduce structured career development paths and transparent promotion criteria",
            "Address burnout with workload caps and mental health support initiatives",
            "Conduct stay interviews at the 2–3 year tenure mark to pre-empt attrition",
            "Improve onboarding and 6-month check-ins to improve early satisfaction",
            "Build pulse survey cadence (quarterly) to track satisfaction trends in real time",
        ],
        "Expected Impact": [
            "Reduce attrition in low-salary cohort by 15–25%",
            f"Reduce {top_attrition_dept} attrition by 10–20%",
            "Improve promotion satisfaction; reduce attrition by 8–12%",
            "Reduce overloaded employee attrition by 10–15%",
            "Detect and mitigate year-3 attrition spikes early",
            "Improve 1st-year retention and satisfaction scores",
            "Proactive risk detection before attrition event",
        ]
    }
    rec_df = pd.DataFrame(rec_data)
    st.dataframe(rec_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 📊 Descriptive Statistics Summary")
    stats = df[["satisfaction_level", "last_evaluation",
                "number_project", "average_montly_hours", "time_spend_company"]].describe()
    stats.index = ["Count", "Mean", "Std Dev", "Min", "25th %ile", "Median", "75th %ile", "Max"]
    stats.columns = ["Satisfaction", "Evaluation", "Projects", "Monthly Hours", "Tenure (yrs)"]
    stats = stats.applymap(lambda x: f"{x:.2f}")
    st.dataframe(stats, use_container_width=True)
