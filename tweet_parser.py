import re

def extract_player_name(tweet_text):
    """
    Very simple starter parser.
    Looks for capitalized first + last name patterns.
    """
    pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-zA-Z\.\'-]+)+\b'
    matches = re.findall(pattern, tweet_text)

    if matches:
        return matches[0]

    return None
