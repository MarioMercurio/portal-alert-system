import pandas as pd
from rapidfuzz import process

def load_superfile():
    try:
        df = pd.read_excel("SuperFile.xlsx")
        df["Player_clean"] = df["Player"].str.lower()
        return df
    except Exception as e:
        print("Error loading SuperFile:", e)
        return None


def match_player(name, df):
    if df is None:
        return None

    name = name.lower()

    # Exact match first
    exact = df[df["Player_clean"] == name]
    if len(exact) > 0:
        return exact.iloc[0]

    # Fuzzy match
    players = df["Player_clean"].tolist()
    match = process.extractOne(name, players)

    if match and match[1] > 85:
        matched_name = match[0]
        row = df[df["Player_clean"] == matched_name]
        return row.iloc[0]

    return None


def get_player_info(player_row):
    if player_row is None:
        return None

    player = player_row["Player"]
    school = player_row["School"]

    try:
        hdi = round(player_row["HDI"])
    except:
        hdi = None

    return {
        "player": player,
        "school": school,
        "hdi": hdi
    }
