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
