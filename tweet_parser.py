import re

PORTAL_PHRASES = [
    "entered the transfer portal",
    "has entered the transfer portal",
    "plans to enter the transfer portal",
    "intends to enter the transfer portal",
    "is entering the transfer portal",
    "will enter the transfer portal",
    "expected to enter the transfer portal",
    "has hit the transfer portal",
    "hit the transfer portal",
    "entered the portal",
    "plans to enter the portal",
    "intends to enter the portal",
    "will enter the portal",
]

BAD_NAME_PARTS = {
    "southern", "northern", "eastern", "western",
    "mississippi", "texas", "florida", "california",
    "arizona", "ohio", "kansas", "georgia", "louisiana",
    "state", "university", "college", "academy", "school",
    "junior", "senior", "freshman", "sophomore",
    "guard", "forward", "center", "basketball", "hoops",
    "source", "hearing", "report", "reported", "agent",
    "thank", "future", "program", "transfer", "portal",
}

FULL_NAME_PATTERN = r"\b[A-Z][a-zA-Z\.\-']+\s+[A-Z][a-zA-Z\.\-']+\b"


def _clean_text(text):
    text = text or ""
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _is_valid_player_name(name):
    parts = name.split()
    if len(parts) != 2:
        return False

    p1 = parts[0].lower().strip(".,")
    p2 = parts[1].lower().strip(".,")

    if p1 in BAD_NAME_PARTS or p2 in BAD_NAME_PARTS:
        return False

    return True


def _extract_names(text):
    matches = re.findall(FULL_NAME_PATTERN, text)
    return [m.strip(" ,.-") for m in matches if _is_valid_player_name(m)]


def extract_player_name(tweet_text):
    text = _clean_text(tweet_text)
    if not text:
        return None

    lower_text = text.lower()

    # Best method: last valid full name before a portal phrase
    for phrase in PORTAL_PHRASES:
        idx = lower_text.find(phrase)
        if idx != -1:
            prefix = text[:idx]
            names = _extract_names(prefix)
            if names:
                return names[-1]

    # Fallback: last valid full name anywhere
    all_names = _extract_names(text)
    if all_names:
        return all_names[-1]

    return None
