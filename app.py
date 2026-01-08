import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tech Job Salary Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("data/tech_jobs.csv")

df = load_data()

# --- Quick cleanup / polish ---
df = df.drop(columns=["Unnamed: 0"], errors="ignore")
df = df.dropna(subset=["salary_in_usd"])
df["salary_in_usd"] = pd.to_numeric(df["salary_in_usd"], errors="coerce")
df = df.dropna(subset=["salary_in_usd"])

st.title("💼 Tech Job Salary Dashboard")
st.caption("Interactive dashboard exploring tech job salaries by role, experience, and remote work.")

# --- Sidebar filters ---
st.sidebar.header("Filters")

top_titles = df["job_title"].value_counts().head(10).index.tolist()

job_titles = st.sidebar.multiselect(
    "Job Title",
    options=sorted(df["job_title"].unique()),
    default=top_titles
)

experience_levels = st.sidebar.multiselect(
    "Experience Level",
    options=sorted(df["experience_level"].dropna().unique()),
    default=sorted(df["experience_level"].dropna().unique())
)

remote_ratios = st.sidebar.multiselect(
    "Remote Ratio",
    options=sorted(df["remote_ratio"].dropna().unique()),
    default=sorted(df["remote_ratio"].dropna().unique())
)

filtered_df = df[
    (df["job_title"].isin(job_titles)) &
    (df["experience_level"].isin(experience_levels)) &
    (df["remote_ratio"].isin(remote_ratios))
].copy()

if filtered_df.empty:
    st.warning("No results for those filters. Try selecting more job titles or experience levels.")
    st.stop()

# --- Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Jobs", len(filtered_df))
col2.metric("Average Salary (USD)", f"${int(filtered_df['salary_in_usd'].mean()):,}")
col3.metric("Max Salary (USD)", f"${int(filtered_df['salary_in_usd'].max()):,}")

# --- Charts ---
avg_salary = (
    filtered_df
    .groupby("job_title")["salary_in_usd"]
    .mean()
    .reset_index()
    .sort_values("salary_in_usd", ascending=False)
)

fig1 = px.bar(
    avg_salary,
    x="job_title",
    y="salary_in_usd",
    title="Average Salary by Job Title",
)
st.plotly_chart(fig1, use_container_width=True)

colA, colB = st.columns(2)

with colA:
    fig2 = px.box(
        filtered_df,
        x="experience_level",
        y="salary_in_usd",
        title="Salary Distribution by Experience Level"
    )
    st.plotly_chart(fig2, use_container_width=True)

with colB:
    fig3 = px.box(
        filtered_df,
        x="remote_ratio",
        y="salary_in_usd",
        title="Salary Distribution by Remote Ratio"
    )
    st.plotly_chart(fig3, use_container_width=True)

# --- Insights section ---
st.subheader("📌 Key Insights (based on current filters)")

avg_by_exp = filtered_df.groupby("experience_level")["salary_in_usd"].mean().sort_values(ascending=False)
top_exp = avg_by_exp.index[0]
top_exp_salary = int(avg_by_exp.iloc[0])

remote_avg = filtered_df.groupby("remote_ratio")["salary_in_usd"].mean().sort_values(ascending=False)
top_remote = int(remote_avg.index[0])
top_remote_salary = int(remote_avg.iloc[0])

st.write(
    f"""
- Highest average pay (experience): **{top_exp}** (~${top_exp_salary:,})
- Best-paying remote ratio in this view: **{top_remote}% remote** (~${top_remote_salary:,})
- Use the filters on the left to explore different roles and patterns.
"""
)

# --- Data table ---
with st.expander("📄 View filtered data table"):
    st.dataframe(
        filtered_df.sort_values("salary_in_usd", ascending=False),
        use_container_width=True
    )
