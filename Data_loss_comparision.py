import pandas as pd

# Load datasets
df_original = pd.read_csv("player_injuries_impact.csv")
df_cleaned = pd.read_csv("cleaned_player_injuries_impact.csv")
df_nuked = pd.read_csv("cleaned_nuked_player_injuries_impact.csv")

# Row counts
orig_rows = len(df_original)
cleaned_rows = len(df_cleaned)
nuked_rows = len(df_nuked)

# Data loss calculations
cleaned_loss = orig_rows - cleaned_rows
cleaned_loss_pct = (cleaned_loss / orig_rows) * 100

nuked_loss = orig_rows - nuked_rows
nuked_loss_pct = (nuked_loss / orig_rows) * 100

# Print results
print("===== DATA LOSS COMPARISON =====")
print(f"Original dataset rows: {orig_rows}\n")

print("---- Cleaned Dataset (Critical Method) ----")
print(f"Rows kept: {cleaned_rows}")
print(f"Rows removed: {cleaned_loss}")
print(f"Data loss: {cleaned_loss_pct:.2f}%\n")

print("---- Cleaned Nuked Dataset (Match1+Match2 Method) ----")
print(f"Rows kept: {nuked_rows}")
print(f"Rows removed: {nuked_loss}")
print(f"Data loss: {nuked_loss_pct:.2f}%\n")

print("============================================")
