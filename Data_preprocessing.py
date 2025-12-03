import pandas as pd

df=pd.read_csv('player_injuries_impact.csv')




df=df.replace('N.A.',pd.NA)

df.dropna(inplace=True)



df.to_csv('player_injuries_impact_NO-na.csv', index=False)