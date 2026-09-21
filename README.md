# IBM-Bob-Project
HR Employee Attrition &amp; Workforce Descriptive Analytics — Analyzes employee attrition patterns across satisfaction, workload, salary, department, performance, promotions, and experience. Uses Python, Pandas, and data visualization to uncover key workforce trends and HR insights.

👥 HR Employee Analytics Dashboard
Author: Priya Sahu
Project Type: Descriptive Analytics — HR Domain
Tool Stack: Python · Streamlit · Pandas · Plotly

📌 Project Description
A complete, end-to-end Descriptive Analytics project built on an HR Employee dataset of 14,999 records across 10 departments. The project follows the full analytics workflow:

Data Understanding → Data Cleaning → Data Transformation →
KPI Calculation → Descriptive Analytics → Visualization → Insights
The result is a professional, interactive Streamlit dashboard with:

📊 6 KPI Cards (Attrition Rate, Satisfaction, Hours, Tenure, Promotions)
🔍 5 Interactive Sidebar Filters (Department, Salary, Status, Satisfaction, Tenure)
📉 Attrition Analysis (donut, grouped bar, scatter, horizontal bar)
🏢 Department Analysis (radar chart, summary table, comparison bars)
💰 Salary Analysis (distribution, attrition by salary, satisfaction vs salary)
😊 Satisfaction & Workload (histogram, boxplot, heatmap, workload classification)
📈 Experience & Promotion (tenure trends, promotion impact, dual-axis project chart)
💡 Business Insights & Recommendations (dynamic, data-driven priority matrix)
📂 Dataset
Property	Value
File	HR_Employee_Data.csv
Source	Kaggle – HR Analytics Employee Attrition
Records	14,999
Features	11
Target	left (1 = employee left, 0 = stayed)
Columns
Column	Type	Description
Emp_Id	String	Unique employee ID
satisfaction_level	Float%	Self-reported satisfaction (0–100%)
last_evaluation	Float%	Last performance evaluation score
number_project	Integer	Number of active projects
average_montly_hours	Integer	Avg monthly hours worked
time_spend_company	Integer	Years at the company
Work_accident	Binary	Had workplace accident (1=Yes)
left	Binary	Target — employee left (1=Left)
promotion_last_5years	Binary	Promoted in last 5 years
Department	String	Department name
salary	Ordinal	low / medium / high
🚀 Setup & Run Instructions
Prerequisites
Python 3.9+ installed
pip available in your terminal
Step 1 — Clone / Download the project
Ensure these files are in the same directory:

Hr_employee_Analytics.py
HR_Employee_Data.csv
requirements.txt
Step 2 — Install dependencies
pip install -r requirements.txt
Step 3 — Launch the dashboard
streamlit run Hr_employee_Analytics.py
Step 4 — Open in browser
The dashboard will open automatically, or navigate to:

http://localhost:8501
📁 Project Files
IBMProject/
├── Hr_employee_Analytics.py        # Main application (frontend + backend)
├── HR_Employee_Data.csv            # Source dataset
├── requirements.txt                # Python dependencies
├── PriyaSahu_ProjectReport.docx  # Full project documentation
└── README.md                       # This file
🛠️ Technologies Used
Technology	Version	Purpose
Python	3.9+	Core language
Streamlit	≥ 1.32.0	Interactive web dashboard
Pandas	≥ 2.0.0	Data loading, cleaning, transformation
Plotly	≥ 5.18.0	Interactive visualizations
NumPy	≥ 1.24.0	Numerical operations
📊 Analytics Workflow
1. Data Understanding
14,999 employee records, 11 features
Mix of percentage strings, binary flags, ordinal text, and numeric columns
Target variable: left (binary attrition flag)
2. Data Cleaning
Strip whitespace from column names and string values
Convert percentage strings ("38%") to floats (0.38)
Explicit type casting with pd.to_numeric() + error coercion
Remove duplicates with drop_duplicates()
Impute missing values: median for numeric, mode for categorical
3. Data Transformation
Feature	Transformation
salary	Ordinal encoding: low=1, medium=2, high=3
left	Label: "Left" / "Stayed"
satisfaction_level	Binned: Low / Medium / High
time_spend_company	Grouped: Junior / Mid / Senior / Veteran
average_montly_hours	Categorised: Normal / High / Overloaded
Department	Title-case standardisation
promotion_last_5years	Label: "Promoted" / "Not Promoted"
4. KPI Calculation
KPI	Full-Dataset Value
Total Employees	14,999
Attrition Rate	23.8%
Avg Satisfaction	61.3%
Avg Monthly Hours	201 h
Avg Tenure	3.5 years
Promotion Rate	2.1%
💡 Key Findings
High attrition — 23.8% vs ~15% industry benchmark
Satisfaction is the strongest predictor — employees below 30% satisfaction leave at dramatically higher rates
Salary gap — low-salary employees leave at 30%+ vs ~7% for high-salary
Overwork drives burnout — overloaded employees (>220 h/month) are a major at-risk cohort
Promotions halve attrition — promoted employees leave at far lower rates; only 2.1% were promoted
Year-3 tenure spike — attrition peaks at the 3-year mark, a critical intervention window
🏢 HR Recommendations (Summary)
Priority	Action
🔴 Critical	Salary review & retention bonuses for low-salary cohort
🔴 Critical	Targeted engagement in highest-attrition department
🟠 High	Structured career paths & transparent promotion criteria
🟠 High	Workload caps & mental health support
🟡 Medium	Stay interviews at 2–3 year tenure mark
🟡 Medium	Improved onboarding & 6-month check-ins
🟢 Ongoing	Quarterly employee pulse surveys
📸 Dashboard Preview
Launch the app with streamlit run Hr_employee_Analytics.py to see the full interactive dashboard including:

KPI cards row (6 metrics)
Attrition analysis with donut + scatter charts
Department radar chart
Salary-satisfaction line chart
Workload heatmap
Business insights priority table
Project by Priya Sahu — HR Descriptive Analytics · 2024
