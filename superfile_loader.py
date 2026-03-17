import pandas as pd
import re


SUPERFILE_PATH = "SuperFile.xlsx"


def normalize_name(name):
    if not name:
        return ""

    name = str(name).lower().strip()
    name = name.replace(".", "")
    name = name.replace("'", "")
    name = name.replace("-", " ")
    name = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", name)
    name = re.sub(r"[^a-z0-9\s]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def load_superfile():
    return pd.read_excel(SUPERFILE_PATH)


def find_player(df, player_name):
    if not player_name:
        return None

    target = normalize_name(player_name)
    if not target:
        return None

    target_parts = target.split()
    target_last = target_parts[-1] if target_parts else ""

    # 1) Exact normalized full-name match
    for _, row in df.iterrows():
        full_name = str(row.get("Full Name", ""))
        normalized_full = normalize_name(full_name)

        if normalized_full == target:
            return row

    # 2) Contained match either direction
    for _, row in df.iterrows():
        full_name = str(row.get("Full Name", ""))
        normalized_full = normalize_name(full_name)

        if target in normalized_full or normalized_full in target:
            return row

    # 3) First + last token match
    if len(target_parts) >= 2:
        target_first = target_parts[0]

        for _, row in df.iterrows():
            full_name = str(row.get("Full Name", ""))
            normalized_full = normalize_name(full_name)
            full_parts = normalized_full.split()

            if len(full_parts) >= 2:
                full_first = full_parts[0]
                full_last = full_parts[-1]

                if full_first == target_first and full_last == target_last:
                    return row

    # 4) Last name fallback if unique enough
    if target_last:
        last_name_matches = []

        for _, row in df.iterrows():
            full_name = str(row.get("Full Name", ""))
            normalized_full = normalize_name(full_name)
            full_parts = normalized_full.split()

            if full_parts and full_parts[-1] == target_last:
                last_name_matches.append(row)

        if len(last_name_matches) == 1:
            return last_name_matches[0]

    return None
