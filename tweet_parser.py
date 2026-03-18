import re

IGNORE_TOKENS = {
    "southern", "northern", "eastern", "western",
    "mississippi", "texas", "florida", "california",
    "state", "university", "college", "junior", "senior",
    "freshman", "sophomore", "guard", "forward", "center",
    "agent", "source", "hearing", "report", "reported"
}

PORTAL_PHRASES = [
    "entered the transfer portal",
    "has entered the transfer portal",
    "plans to enter the transfer portal",
    "intends to enter the transfer portal",
    "is entering the transfer portal",
    "will enter the transfer portal",
    "in the transfer portal",
    "has hit the transfer portal",
    "hit the transfer portal",
]

FULL_NAME_PATTERN = r"\b[A-Z][a-zA-Z\.\-']+\s+[A-Z][a-zA-Z\.\-']+\b"
SURNAME_PATTERN = r"\b[A-Z][a-zA-Z\.\-']{2,}\b"


def _clean_text(text):
    text = text or ""
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _looks_like_full_name(name):
    if not name:
        return False

    parts = name.split()
    if len(parts) != 2:
        return False

    lowered = {p.lower().strip(".,") for p in parts}
    if lowered & IGNORE_TOKENS:
        return False

    return True


def _looks_like_surname(token):
    if not token:
        return False

    token_l = token.lower().strip(".,")
    if token_l in IGNORE_TOKENS:
        return False

    if len(token_l) < 3:
        return False

    return True


def extract_player_name(tweet_text):
    text = _clean_text(tweet_text)

    if not text:
        return None

    # 1) Try to find a clean 2-word player name near a portal phrase
    lower_text = text.lower()
    for phrase in PORTAL_PHRASES:
        idx = lower_text.find(phrase)
        if idx != -1:
            start = max(0, idx - 120)
            end = min(len(text), idx + len(phrase) + 40)
            window = text[start:end]

            full_names = re.findall(FULL_NAME_PATTERN, window)
            full_names = [n for n in full_names if _looks_like_full_name(n)]

            if full_names:
                return full_names[-1]

    # 2) Broader full-name search across the whole tweet
    full_names = re.findall(FULL_NAME_PATTERN, text)
    full_names = [n for n in full_names if _looks_like_full_name(n)]

    if full_names:
        return full_names[-1]

    # 3) If only a surname is present, return that as fallback
    # This allows superfile_loader.py to try surname matching.
    tokens = re.findall(SURNAME_PATTERN, text)
    tokens = [t for t in tokens if _looks_like_surname(t)]

    portal_zone = []
    for phrase in PORTAL_PHRASES:
        idx = lower_text.find(phrase)
        if idx != -1:
            start = max(0, idx - 120)
            end = min(len(text), idx + len(phrase) + 80)
            zone = text[start:end]
            portal_zone.extend(re.findall(SURNAME_PATTERN, zone))

    portal_zone = [t for t in portal_zone if _looks_like_surname(t)]

    if portal_zone:
        return portal_zone[-1]

    if tokens:
        return tokens[-1]

    return None
