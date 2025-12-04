import pandas as pd

# Read from the user-provided file
df = pd.read_csv("cleaned_with_metrics.csv")

# ---------------------------------------------------------
# Helper: Convert match results to numeric values
# ---------------------------------------------------------
result_map = {
    "win": 3,
    "draw": 1,
    "lose": 0,
    "Missing": None,
    "N.A": None,
    "N.A.": None
}

def map_results(series):
    return series.map(result_map)

# ---------------------------------------------------------
# Identify columns by phase automatically
# ---------------------------------------------------------
before_rating_cols = [c for c in df.columns if "before_injury_Player_rating" in c]
before_gd_cols     = [c for c in df.columns if "before_injury_GD" in c]
before_result_cols = [c for c in df.columns if "before_injury_Result" in c]

missed_gd_cols     = [c for c in df.columns if "missed_match_GD" in c]
missed_result_cols = [c for c in df.columns if "missed_match_Result" in c]

after_rating_cols  = [c for c in df.columns if "after_injury_Player_rating" in c]
after_gd_cols      = [c for c in df.columns if "after_injury_GD" in c]
after_result_cols  = [c for c in df.columns if "after_injury_Result" in c]

# ---------------------------------------------------------
# Convert match results
# ---------------------------------------------------------
df[before_result_cols] = df[before_result_cols].apply(map_results)
df[missed_result_cols] = df[missed_result_cols].apply(map_results)
df[after_result_cols]  = df[after_result_cols].apply(map_results)

# ---------------------------------------------------------
# Group by Player Name and compute averages
# ---------------------------------------------------------
grouped = pd.DataFrame()

grouped["Player_Avg_Rating_Before_Injury"] = df.groupby("Name")[before_rating_cols].mean().mean(axis=1)
grouped["Team_Avg_GD_Before_Injury"]       = df.groupby("Name")[before_gd_cols].mean().mean(axis=1)
grouped["Team_Avg_Result_Before_Injury"]   = df.groupby("Name")[before_result_cols].mean().mean(axis=1)

grouped["Team_Avg_GD_Missed"]              = df.groupby("Name")[missed_gd_cols].mean().mean(axis=1)
grouped["Team_Avg_Result_Missed"]          = df.groupby("Name")[missed_result_cols].mean().mean(axis=1)

grouped["Player_Avg_Rating_After_Injury"]  = df.groupby("Name")[after_rating_cols].mean().mean(axis=1)
grouped["Team_Avg_GD_After"]               = df.groupby("Name")[after_gd_cols].mean().mean(axis=1)
grouped["Team_Avg_Result_After"]           = df.groupby("Name")[after_result_cols].mean().mean(axis=1)

# ---------------------------------------------------------
# Performance metrics
# ---------------------------------------------------------
grouped["Player_Rating_Delta"] = (
    grouped["Player_Avg_Rating_After_Injury"] -
    grouped["Player_Avg_Rating_Before_Injury"]
)

grouped["Team_Performance_Drop"] = (
    grouped["Team_Avg_GD_Before_Injury"] -
    grouped["Team_Avg_GD_Missed"]
)

grouped["Team_Rebound_Index"] = (
    grouped["Team_Avg_GD_After"] -
    grouped["Team_Avg_GD_Missed"]
)

# ---------------------------------------------------------
# Save the grouped summary
# ---------------------------------------------------------
grouped.reset_index(inplace=True)
grouped.to_csv("player_injury_phase_summary.csv", index=False)

print("Player injury phase summary generated successfully!")