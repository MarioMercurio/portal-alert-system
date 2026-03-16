import pandas as pd

def load_players():
    try:
        df = pd.read_excel("SuperFile.xlsx")
        return df
    except Exception as e:
        print("Error loading SuperFile:", e)
        return None

def find_player(name, df):
    if df is None:
        return None
    
    matches = df[df["Player"].str.contains(name, case=False, na=False)]
    
    if len(matches) > 0:
        return matches.iloc[0]
    
    return None

def get_hdi(player_row):
    if player_row is None:
        return None
    
    try:
        return round(player_row["HDI"])
    except:
        return None
