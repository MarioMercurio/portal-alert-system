import pandas as pd
import os
import re


def normalize_name(name):
    if name is None:
        return ""
    name = str(name).lower()
    name = re.sub(r"[^a-z\s]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()


def load_superfile():
    try:
        base_path = os.path.dirname(__file__)
        file_path = os.path.join(base_path, "SuperFile.xlsx")

        df = pd.read_excel(file_path)

        if "FULL NAME" not in df.columns:
            print("Columns detected:", df.columns.tolist())
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
