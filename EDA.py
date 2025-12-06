import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("INJURY IMPACT STATISTICAL ANALYSIS")
print("="*80)

# Load datasets (using the CSVs you attached)
df_detailed = pd.read_csv("cleaned_with_metrics.csv")
df_summary = pd.read_csv("player_injury_phase_summary.csv")

# Ensure numeric columns exist and coerce if necessary
for col in ["Player_Avg_Rating_Before_Injury", "Player_Avg_Rating_After_Injury", "Team_Performance_Drop_Index", "Age"]:
    if col in df_detailed.columns:
        df_detailed[col] = pd.to_numeric(df_detailed[col], errors="coerce")

for col in ["Player_Avg_Rating_Before_Injury", "Player_Avg_Rating_After_Injury", "Team_Performance_Drop"]:
    if col in df_summary.columns:
        df_summary[col] = pd.to_numeric(df_summary[col], errors="coerce")

# Merge position/team info into the summary (summary lacks Position/Team)
if "Position" not in df_summary.columns or "Team Name" not in df_summary.columns:
    meta = df_detailed[["Name", "Position", "Team Name"]].drop_duplicates(subset=["Name"], keep="first")
    df_summary = df_summary.merge(meta, on="Name", how="left")

# Defensive: sanitize Position column so it cannot be a list/tuple (unhashable)
if "Position" in df_detailed.columns:
    def sanitize_pos(x):
        if isinstance(x, (list, tuple)):
            return x[0] if len(x) > 0 else np.nan
        return x
    df_detailed["Position"] = df_detailed["Position"].apply(sanitize_pos)
    # convert to string for safe grouping; keep NaN as real NaN
    df_detailed["Position"] = df_detailed["Position"].astype(object).where(pd.notnull(df_detailed["Position"]), np.nan)
    df_detailed["Position"] = df_detailed["Position"].astype(str).replace({"nan": np.nan})

# ---------- 1) Player injury frequency ----------
player_injury_freq = df_detailed.groupby("Name").agg(
    Injury_Count=("Name", "count"),
    Avg_Rating_Before=("Player_Avg_Rating_Before_Injury", "mean"),
    Avg_Rating_After=("Player_Avg_Rating_After_Injury", "mean"),
    Avg_Team_Perf_Drop=("Team_Performance_Drop_Index", "mean"),
    Age=("Age", "first"),
    Position=("Position", "first"),
    Team_Name=("Team Name", "first")
).sort_values("Injury_Count", ascending=False)

print("\nTop 10 Most Frequently Injured Players:")
print(player_injury_freq.head(10).to_string())

# ---------- 2) Injury-prone clubs ----------
club_injury_stats = df_detailed.groupby("Team Name").agg(
    Total_Injuries=("Name", "count"),
    Avg_Performance_Drop=("Team_Performance_Drop_Index", "mean"),
    Std_Performance_Drop=("Team_Performance_Drop_Index", "std"),
    Avg_Rating_Before=("Player_Avg_Rating_Before_Injury", "mean"),
    Avg_Rating_After=("Player_Avg_Rating_After_Injury", "mean"),
    Avg_Player_Age=("Age", "mean")
).round(3).sort_values("Total_Injuries", ascending=False)

print("\nClub-Level Injury Summary (top rows):")
print(club_injury_stats.head(15).to_string())

# ---------- 3) Performance improvement / decline ----------
# use df_summary which already has Player_Rating_Delta (if present)
if "Player_Rating_Delta" not in df_summary.columns:
    # compute from available cols as fallback
    if "Player_Avg_Rating_Before_Injury" in df_summary.columns and "Player_Avg_Rating_After_Injury" in df_summary.columns:
        df_summary["Player_Rating_Delta"] = df_summary["Player_Avg_Rating_After_Injury"] - df_summary["Player_Avg_Rating_Before_Injury"]

df_summary_clean = df_summary.dropna(subset=["Player_Avg_Rating_Before_Injury", "Player_Avg_Rating_After_Injury"], how="any")

performance_change = df_summary_clean[["Name", "Player_Avg_Rating_Before_Injury", "Player_Avg_Rating_After_Injury", "Player_Rating_Delta", "Position", "Team Name"]].copy()
performance_change["Performance_Change_%"] = ((performance_change["Player_Rating_Delta"] / performance_change["Player_Avg_Rating_Before_Injury"]) * 100).round(2)

print("\nTop 10 Most Improved Players (by absolute delta):")
print(performance_change.nlargest(10, "Player_Rating_Delta")[["Name","Position","Team Name","Player_Avg_Rating_Before_Injury","Player_Avg_Rating_After_Injury","Player_Rating_Delta","Performance_Change_%"]].to_string())

print("\nTop 10 Largest Declines (by absolute delta):")
print(performance_change.nsmallest(10, "Player_Rating_Delta")[["Name","Position","Team Name","Player_Avg_Rating_Before_Injury","Player_Avg_Rating_After_Injury","Player_Rating_Delta","Performance_Change_%"]].to_string())

# ---------- 4) Top 5 injuries by team performance impact ----------
if "Team_Performance_Drop_Index" in df_detailed.columns:
    top_impact = df_detailed.nlargest(5, "Team_Performance_Drop_Index")[["Name","Team Name","Position","Injury","Player_Avg_Rating_Before_Injury","Player_Avg_Rating_After_Injury","Team_Performance_Drop_Index","Age","Season"]]
    print("\nTop 5 injuries with highest Team Performance Drop Index:")
    for i, row in top_impact.iterrows():
        print(f"- {row['Name']} ({row['Team Name']}), {row['Position']}, Injury: {row['Injury']}, Drop: {row['Team_Performance_Drop_Index']:.3f}, Age: {row['Age']}, Season: {row['Season']}")
else:
    print("\nTeam_Performance_Drop_Index not available in detailed CSV.")

# ---------- 5) Pivot / pre-post comparison ----------
# Avoid using nested list aggregation that caused the previous error.
if "Position" in df_detailed.columns:
    # compute parts separately and concat to form the same multi-column result
    parts = []
    if "Player_Avg_Rating_Before_Injury" in df_detailed.columns:
        pos_before = df_detailed.groupby("Position")["Player_Avg_Rating_Before_Injury"].agg(["mean","std","count"])
        pos_before.columns = [f"Before_{c}" for c in pos_before.columns]
        parts.append(pos_before)
    if "Player_Avg_Rating_After_Injury" in df_detailed.columns:
        pos_after = df_detailed.groupby("Position")["Player_Avg_Rating_After_Injury"].agg(["mean","std"])
        pos_after.columns = [f"After_{c}" for c in pos_after.columns]
        parts.append(pos_after)
    if "Team_Performance_Drop_Index" in df_detailed.columns:
        pos_drop = df_detailed.groupby("Position")["Team_Performance_Drop_Index"].agg(["mean","std"])
        pos_drop.columns = [f"Drop_{c}" for c in pos_drop.columns]
        parts.append(pos_drop)

    if parts:
        pos_pivot = pd.concat(parts, axis=1).round(3)
        print("\nPerformance by Position (sample):")
        # print top 10 positions by count if available
        if "Before_count" in pos_pivot.columns:
            print(pos_pivot.sort_values("Before_count", ascending=False).head(10).to_string())
        else:
            print(pos_pivot.head(10).to_string())
    else:
        print("\nNo appropriate numeric columns found for position pivot.")
else:
    print("\nPosition column not found in detailed CSV for pivot analysis.")

# ---------- 6) Recovery trends (age groups) ----------
if "Age" in df_detailed.columns:
    df_detailed["Age_Group"] = pd.cut(df_detailed["Age"], bins=[16,23,28,32,45], labels=["Young (17-23)","Prime (24-28)","Veteran (29-32)","Late Career (33+)"])
    recovery_by_age = df_detailed.groupby("Age_Group").agg(
        Avg_Rating_Before = ("Player_Avg_Rating_Before_Injury", "mean"),
        Avg_Rating_After = ("Player_Avg_Rating_After_Injury", "mean"),
        Avg_Perf_Drop = ("Team_Performance_Drop_Index", "mean"),
        Std_Perf_Drop = ("Team_Performance_Drop_Index", "std"),
        Injury_Count = ("Name", "count")
    ).round(3)
    print("\nRecovery trends by age group:")
    print(recovery_by_age.to_string())
else:
    print("\nAge column not present; skipping recovery-by-age analysis.")

# ---------- 7) Injury type analysis ----------
if "Injury" in df_detailed.columns:
    inj_stats = df_detailed.groupby("Injury").agg(
        Count=("Name", "count"),
        Avg_Perf_Drop=("Team_Performance_Drop_Index", "mean"),
        Std_Perf_Drop=("Team_Performance_Drop_Index", "std"),
        Avg_Rating_Before=("Player_Avg_Rating_Before_Injury", "mean"),
        Avg_Rating_After=("Player_Avg_Rating_After_Injury", "mean")
    ).sort_values("Count", ascending=False).round(3)
    print("\nTop 15 injuries by frequency:")
    print(inj_stats.head(15).to_string())
else:
    print("\nNo Injury column present in detailed CSV.")

# ---------- 8) Summary stats & correlations ----------
numeric_cols = [c for c in ["Age","Player_Avg_Rating_Before_Injury","Player_Avg_Rating_After_Injury","Team_Performance_Drop_Index"] if c in df_detailed.columns]
if numeric_cols:
    print("\nSummary statistics for numeric metrics:")
    print(df_detailed[numeric_cols].describe().round(3).to_string())
    print("\nCorrelation matrix:")
    print(df_detailed[numeric_cols].corr().round(3).to_string())

# ---------- 9) Season trends ----------
if "Season" in df_detailed.columns:
    season_stats = df_detailed.groupby("Season").agg(
        Total_Injuries=("Name","count"),
        Avg_Perf_Drop=("Team_Performance_Drop_Index","mean"),
        Avg_Player_Rating=("Player_Avg_Rating_Before_Injury","mean")
    ).round(3).sort_index()
    print("\nSeasonal injury summary:")
    print(season_stats.to_string())

# ---------- 10) Visualizations ----------
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (15,12)

fig, axes = plt.subplots(2,3, figsize=(18,12))
fig.suptitle("SportHurt Injury Analysis Dashboard", fontsize=14, fontweight="bold")

# Top 10 injured players
ax = axes[0,0]
top_players = player_injury_freq.head(10)["Injury_Count"].sort_values()
top_players.plot(kind="barh", ax=ax, color="coral")
ax.set_title("Top 10 Most Frequently Injured Players")
ax.set_xlabel("Injury Count")

# Club injury counts
ax = axes[0,1]
club_counts = df_detailed["Team Name"].value_counts().head(10)
club_counts.plot(kind="bar", ax=ax, color="skyblue")
ax.set_title("Top 10 Injury-Prone Clubs")
ax.set_ylabel("Total Injuries")
ax.tick_params(axis="x", rotation=45)

# Avg perf drop by position
ax = axes[0,2]
if "Position" in df_detailed.columns:
    pos_perf = df_detailed.groupby("Position")["Team_Performance_Drop_Index"].mean().sort_values(ascending=False)
    pos_perf.plot(kind="bar", ax=ax, color="lightgreen")
    ax.set_title("Avg Performance Drop by Position")
    ax.set_ylabel("Avg Performance Drop")
    ax.tick_params(axis="x", rotation=45)
else:
    ax.text(0.5, 0.5, "No Position data", ha="center")
    ax.set_title("Avg Performance Drop by Position")

# Age vs performance drop scatter
ax = axes[1,0]
if "Age" in df_detailed.columns:
    ax.scatter(df_detailed["Age"], df_detailed["Team_Performance_Drop_Index"], alpha=0.6, s=60, color="purple")
    ax.set_xlabel("Age")
    ax.set_ylabel("Team Performance Drop Index")
    ax.set_title("Age vs Performance Impact")
else:
    ax.text(0.5,0.5,"No Age data",ha="center")

# Top injury types
ax = axes[1,1]
if "Injury" in df_detailed.columns:
    top_inj = df_detailed["Injury"].value_counts().head(8)
    ax.barh(top_inj.index, top_inj.values, color="salmon")
    ax.set_title("Top 8 Injury Types")
    ax.set_xlabel("Count")
else:
    ax.text(0.5,0.5,"No Injury column",ha="center")

# Season trend
ax = axes[1,2]
if "Season" in df_detailed.columns:
    season_counts = df_detailed.groupby("Season").size()
    ax.plot(season_counts.index, season_counts.values, marker="o", color="darkblue")
    ax.set_title("Injuries by Season")
    ax.set_xlabel("Season")
    ax.set_ylabel("Total Injuries")
    ax.tick_params(axis="x", rotation=45)
else:
    ax.text(0.5,0.5,"No Season data",ha="center")

plt.tight_layout()
plt.subplots_adjust(top=0.92)
plt.savefig("injury_analysis_dashboard.png", dpi=300, bbox_inches="tight")
print("\nSaved 'injury_analysis_dashboard.png'")

# Before vs After recovery comparison (top 20 by absolute change)
if not performance_change.empty:
    pch = performance_change.dropna().sort_values("Player_Rating_Delta", ascending=False)
    top20 = pd.concat([pch.head(10), pch.tail(10)]) if len(pch) >= 20 else pch.head(20)
    fig2, ax = plt.subplots(figsize=(12,7))
    indices = np.arange(len(top20))
    w = 0.35
    ax.bar(indices - w/2, top20["Player_Avg_Rating_Before_Injury"], width=w, label="Before", color="steelblue")
    ax.bar(indices + w/2, top20["Player_Avg_Rating_After_Injury"], width=w, label="After", color="coral")
    ax.set_xticks(indices)
    ax.set_xticklabels(top20["Name"], rotation=45, ha="right")
    ax.set_ylabel("Avg Rating")
    ax.set_title("Before vs After Injury (sample players)")
    ax.legend()
    plt.tight_layout()
    plt.savefig("before_after_recovery_comparison.png", dpi=300, bbox_inches="tight")
    print("Saved 'before_after_recovery_comparison.png'")

print("\nAnalysis complete.")
print(f"Total Injuries Analyzed: {len(df_detailed)}")
print(f"Unique Players: {df_detailed['Name'].nunique()}")
print(f"Clubs Represented: {df_detailed['Team Name'].nunique() if 'Team Name' in df_detailed.columns else 'N/A'}")
if "Team_Performance_Drop_Index" in df_detailed.columns:
    print(f"Avg Team Performance Drop Index: {df_detailed['Team_Performance_Drop_Index'].mean():.3f}")