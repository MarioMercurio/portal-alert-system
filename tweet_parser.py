import re

def extract_player_name(tweet_text):
    """
    Detect player names including initials like A.J. Storr or DJ Wagner
    """

    pattern = r'\b(?:[A-Z]\.[A-Z]\.|[A-Z][a-z]+)\s+[A-Z][a-zA-Z\'\-]+\b'

    matches = re.findall(pattern, tweet_text)

    if matches:
        return matches[0]

    return None
