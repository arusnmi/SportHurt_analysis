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
# VISUAL 1 — Bar Chart: Top 10 Injuries With Highest Average Team Performance Drop
# -------------------------------------------------------

st.header("1️⃣ Top 10 Injuries With Highest Average Team Performance Drop")

# 1. Calculate Performance Drop for each incident: (GD Before) - (GD During Absence)
# Positive value means the team performed WORSE without the player.
# We use the correct column names from cleaned_with_metrics.csv.
df["Injury_Performance_Drop"] = df["Avg_GD_Before_Injury"] - df["Avg_GD_Missed_Matches"]

# 2. Aggregate the drop by the Injury type and calculate the average drop
# This step calculates the average performance drop for each unique injury type, regardless of player or team.
injury_drop_summary = df.groupby("Injury", dropna=True)["Injury_Performance_Drop"].mean().reset_index()

# 3. Sort descending to get the 'Highest' average drops at the top and select Top 10
top10_injury_types = injury_drop_summary.sort_values(
    by="Injury_Performance_Drop",
    ascending=False
).head(10)

# 4. Create the Bar Chart using the aggregated data
fig1 = px.bar(
    top10_injury_types,
    x="Injury",  # Use injury type as the X-axis
    y="Injury_Performance_Drop",
    color="Injury_Performance_Drop", # Use color scale based on the drop value
    title="Top 10 Injuries With Highest Average Team Performance Drop",
    labels={"Injury_Performance_Drop": "Average Performance Drop (GD Decrease)", "Injury": "Injury Type"},
)

# Remove the legend as requested
fig1.update_layout(showlegend=False)

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
# VISUAL 4 — Scatter Plot: Player Age vs Player Performance Drop
# -------------------------------------------------------

st.header("4️⃣ Player Age vs Player Performance Drop Index")

# Clean data for plotting
df_scatter = df_summary.copy()

# FIX: The 'Age' column is in the 'df' (cleaned_with_metrics.csv) file, not 'df_summary'.
# We extract unique Name and Age pairs from 'df' and merge them into 'df_scatter'.
age_data = df[["Name", "Age"]].drop_duplicates()
df_scatter = df_scatter.merge(age_data, on="Name", how="left")

# The 'Age' column is now available via the merge.
df_scatter["Age"] = pd.to_numeric(df_scatter["Age"], errors="coerce")


# --- NEW LOGIC: Use Player_Rating_Delta for Y-axis and Size ---
# The metric for player performance drop is 'Player_Rating_Delta' (After - Before).
# Negative Delta means a drop in player rating.
df_scatter["Size_Positive"] = df_scatter["Player_Rating_Delta"].abs()

# Replace NaN values with 0 to avoid Plotly errors
df_scatter["Size_Positive"] = df_scatter["Size_Positive"].fillna(0)

# Drop NaN Age and Player_Rating_Delta values for plotting
df_scatter = df_scatter.dropna(subset=["Age", "Player_Rating_Delta"]) 

fig4 = px.scatter(
    df_scatter,
    x="Age",
    y="Player_Rating_Delta", # Changed from Team_Performance_Drop
    color="Player_Rating_Delta", # Changed from Team_Performance_Drop
    size="Size_Positive",       # Changed to Player_Rating_Delta.abs()
    hover_name="Name",
    title="Age vs Player Rating Delta (Bubble size = magnitude of change)",
    labels={"Player_Rating_Delta": "Player Rating Delta (After - Before)"} # Updated Label
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
