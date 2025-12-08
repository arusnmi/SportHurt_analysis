import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# -------------------------------------------------------
# Load Data
# -------------------------------------------------------
df = pd.read_csv("cleaned_with_metrics.csv")
df_summary = pd.read_csv("player_injury_phase_summary.csv")

st.title("⚽ Injury Impact Analytics Dashboard")
st.write("Interactive analytics using player injury metrics and recovery data.")

# -------------------------------------------------------
# PATCH: Add Age into df_summary
# -------------------------------------------------------
df_age = df[["Name", "Age"]].drop_duplicates()   # extract player ages
df_summary = df_summary.merge(df_age, on="Name", how="left")

# -------------------------------------------------------
# VISUAL 1 — Bar Chart: Top 10 Injuries With Highest Team Performance Drop
# -------------------------------------------------------

st.header("1️⃣ Top 10 Injuries With Highest Team Performance Drop")

top10_drop = df_summary.nlargest(10, "Team_Performance_Drop")

fig1 = px.bar(
    top10_drop,
    x="Name",
    y="Team_Performance_Drop",
    color="Team_Performance_Drop",
    title="Top 10 Team Performance Drops Due to Injury",
)
st.plotly_chart(fig1, use_container_width=True)

# -------------------------------------------------------
# VISUAL 2 — Line Chart: Player Performance Timeline
# -------------------------------------------------------

st.header("2️⃣ Player Performance Timeline (Before → After Injury)")

player_selected = st.selectbox(
    "Select a Player:",
    df_summary["Name"].unique()
)

ft = df_summary[df_summary["Name"] == player_selected].iloc[0]

timeline_df = pd.DataFrame({
    "Phase": ["Before Injury", "After Injury"],
    "Average Rating": [
        ft["Player_Avg_Rating_Before_Injury"],
        ft["Player_Avg_Rating_After_Injury"]
    ]
})

fig2 = px.line(
    timeline_df,
    x="Phase",
    y="Average Rating",
    markers=True,
    title=f"Performance Timeline for {player_selected}"
)

st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------------
# VISUAL 3 — Heatmap: Injury Frequency Across Months and Clubs
# -------------------------------------------------------

st.header("3️⃣ Injury Frequency Heatmap (Month × Club)")

df["Date of Injury"] = pd.to_datetime(df["Date of Injury"], errors="coerce")
df["Injury_Month"] = df["Date of Injury"].dt.month
df["Injury_Month"] = df["Injury_Month"].fillna(0).astype(int)

pivot = df.pivot_table(
    index="Team Name",
    columns="Injury_Month",
    values="Name",
    aggfunc="count"
).fillna(0)

fig3, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(pivot, cmap="Reds", annot=True, fmt="g", ax=ax)
st.pyplot(fig3)

# -------------------------------------------------------
# VISUAL 4 — Scatter Plot: Player Age vs Performance Drop
# -------------------------------------------------------

st.header("4️⃣ Player Age vs Performance Drop Index")

fig4 = px.scatter(
    df_summary,
    x="Age",
    y="Team_Performance_Drop",
    color="Team_Performance_Drop",
    size="Team_Performance_Drop",
    hover_name="Name",
    title="Age vs Team Performance Drop",
)
st.plotly_chart(fig4, use_container_width=True)

# -------------------------------------------------------
# VISUAL 5 — Leaderboard: Comeback Rating Improvement
# -------------------------------------------------------

st.header("5️⃣ Comeback Leaderboard (Rating Improvement After Injury)")

leaderboard = df_summary.sort_values(
    by="Player_Rating_Delta", ascending=False
)[["Name", "Player_Rating_Delta",
   "Player_Avg_Rating_Before_Injury",
   "Player_Avg_Rating_After_Injury"]]

st.dataframe(leaderboard, use_container_width=True)
