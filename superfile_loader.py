import pandas as pd


def load_superfile(path="SuperFile.xlsx"):
    try:
        # Load sheet without assuming header row
        df = pd.read_excel(path, header=None)

        # Find the row that contains the word "Player"
        header_row = None
        for i in range(len(df)):
            row = df.iloc[i].astype(str).str.lower()
            if "player" in row.values:
                header_row = i
                break

        if header_row is None:
            print("Header row not found")
            return None

        # Reload with the detected header
        df = pd.read_excel(path, header=header_row)

        return df

    except Exception as e:
        print("Error loading SuperFile:", e)
        return None


def find_player(player_name, df):
    if df is None:
        return None

    try:
        matches = df[df["Player"].str.contains(player_name, case=False, na=False)]

        if len(matches) > 0:
            return matches.iloc[0]

    except Exception as e:
        print("Error finding player:", e)

    return None
