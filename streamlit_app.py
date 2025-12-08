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
# VISUAL 1 — Bar Chart: Top 10 Injuries With Highest Team Performance Drop
# -------------------------------------------------------

st.header("1️⃣ Top 10 Injuries With Highest Team Performance Drop")

# Compute injury-level drop (per injury event)
# CORRECTED: Using 'Avg_GD_Missed_Matches' and 'Avg_GD_Before_Injury'
df["Injury_Performance_Drop"] = df["Avg_GD_Missed_Matches"] - df["Avg_GD_Before_Injury"]

# Sort and select top 10
top10_injuries = df.sort_values(by="Injury_Performance_Drop", ascending=True).head(10)

fig1 = px.bar(
    top10_injuries,
    x="Name",
    y="Injury_Performance_Drop",
    # CORRECTED: Updated hover data columns to match the dataframe
    hover_data=["Team Name", "Date of Injury", "Avg_GD_Before_Injury", "Avg_GD_Missed_Matches"],
    color="Injury_Performance_Drop",
    title="Top 10 Injuries With Highest Team Performance Drop (Event-Level)",
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

# Clean data for plotting
df_scatter = df_summary.copy()

# Compute positive marker sizes
df_scatter["Size_Positive"] = df_scatter["Team_Performance_Drop"].abs()

# Replace NaN values with 0 to avoid Plotly errors
df_scatter["Size_Positive"] = df_scatter["Size_Positive"].fillna(0)

# Also ensure Age is numeric
df_scatter["Age"] = pd.to_numeric(df_scatter["Age"], errors="coerce")
df_scatter = df_scatter.dropna(subset=["Age"])

fig4 = px.scatter(
    df_scatter,
    x="Age",
    y="Team_Performance_Drop",
    color="Team_Performance_Drop",
    size="Size_Positive",
    hover_name="Name",
    title="Age vs Team Performance Drop (Bubble size = impact magnitude)",
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
