import pandas as pd
import re


def normalize_name(name):
    if name is None:
        return ""
    name = str(name).lower()
    name = re.sub(r'[^a-z\s]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name.strip()


def load_superfile(path="SuperFile.xlsx"):
    try:
        # try loading the excel file
        df = pd.read_excel(path)

        # show the columns in the console logs
        print("Columns found:", df.columns.tolist())

        if "FULL NAME" not in df.columns:
            print("FULL NAME column not found")
            return None

        df["name_clean"] = df["FULL NAME"].apply(normalize_name)

        return df

    except Exception as e:
        print("Error loading SuperFile:", e)
        return None


def find_player(player_name, df):
    if df is None:
        return None

    try:
        player_clean = normalize_name(player_name)

        matches = df[df["name_clean"].str.contains(player_clean, na=False)]

        if len(matches) > 0:
            return matches.iloc[0]

    except Exception as e:
        print("Error finding player:", e)

    return None
