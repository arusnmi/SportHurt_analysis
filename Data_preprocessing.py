import pandas as pd

df = pd.read_csv('player_injuries_impact.csv')

# 1. Convert "N.A." to actual missing values
df = df.replace(['N.A.', 'N.A'], pd.NA)

# 2. Detect Match1 and Match2 columns automatically
match1_cols = [col for col in df.columns if col.startswith("Match1_")]
match2_cols = [col for col in df.columns if col.startswith("Match2_")]

# 3. Drop rows only if ALL Match1 AND ALL Match2 values are missing
df = df.dropna(subset = match1_cols + match2_cols, how='all')


# 4. Unify all the player ratings to be float values 

rating_cols = [col for col in df.columns if 'rating' in col.lower()]

for col in rating_cols:
    df[col] = (
        df[col]
        .astype(str)
        .str.extract(r'(\d+\.?\d*)')  
        .astype(float)                
    )


# 5. Save the cleaned DataFrame to a new CSV file
df.to_csv('cleaned_nuked_player_injuries_impact.csv', index=False)




