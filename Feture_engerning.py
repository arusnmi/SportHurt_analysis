import pandas as pd

# Load cleaned dataset
df = pd.read_csv("cleaned_player_injuries_impact.csv")

# ---------------------------------------------------------
# 1. Player Average Rating Before Injury
# ---------------------------------------------------------
before_rating_cols = [
    col for col in df.columns 
    if "before_injury_Player_rating" in col
]

df["Player_Avg_Rating_Before_Injury"] = df[before_rating_cols].mean(axis=1)


# ---------------------------------------------------------
# 2. Player Average Rating After Injury
# ---------------------------------------------------------
after_rating_cols = [
    col for col in df.columns 
    if "after_injury_Player_rating" in col
]

df["Player_Avg_Rating_After_Injury"] = df[after_rating_cols].mean(axis=1)


# ---------------------------------------------------------
# 3. Team Performance Drop Index
# ---------------------------------------------------------
# Goal difference columns
before_gd_cols = [
    col for col in df.columns 
    if "before_injury_GD" in col
]

missed_gd_cols = [
    col for col in df.columns 
    if "missed_match_GD" in col
]

# Average goal differences
df["Avg_GD_Before_Injury"] = df[before_gd_cols].mean(axis=1)
df["Avg_GD_Missed_Matches"] = df[missed_gd_cols].mean(axis=1)

# Performance Drop = Before - During
df["Team_Performance_Drop_Index"] = (
    df["Avg_GD_Before_Injury"] - df["Avg_GD_Missed_Matches"]
)

# ---------------------------------------------------------
# Save new dataset
# ---------------------------------------------------------
df.to_csv("cleaned_with_metrics.csv", index=False)

print("New columns generated successfully!")
