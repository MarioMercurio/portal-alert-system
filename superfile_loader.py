import pandas as pd


def load_superfile(path="SuperFile.xlsx"):
    try:
        df = pd.read_excel(path)
        return df
    except Exception as e:
        print("Error loading SuperFile:", e)
        return None


def find_player(player_name, df):
    if df is None:
        return None

    try:
        matches = df[df["FULL NAME"].astype(str).str.contains(player_name, case=False, na=False)]

        if len(matches) > 0:
            return matches.iloc[0]

    except Exception as e:
        print("Error finding player:", e)

    return None
