import re

PORTAL_PHRASES = [
    "entered the transfer portal",
    "has entered the transfer portal",
    "plans to enter the transfer portal",
    "intends to enter the transfer portal",
    "is entering the transfer portal",
    "will enter the transfer portal",
    "has hit the transfer portal",
    "hit the transfer portal",
    "in the transfer portal",
]

IGNORE_WORDS = {
    "southern", "northern", "eastern", "western",
    "mississippi", "texas", "florida", "california",
    "arizona", "ohio", "kansas", "georgia", "louisiana",
    "state", "university", "college", "academy", "school",
    "junior", "senior", "freshman", "sophomore",
    "guard", "forward", "center",
    "source", "hearing", "report", "reported", "agent",
    "men", "mens", "basketball", "hoops",
}

FULL_NAME_PATTERN = r"\b[A-Z][a-zA-Z\.\-']+\s+[A-Z][a-zA-Z\.\-']+\b"


def _clean_text(text):
    text = text or ""
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _is_bad_name(name):
    if not name:
        return True

    parts = name.split()
    if len(parts) != 2:
        return True

    lowered = [p.lower().strip(".,") for p in parts]

    # Reject if either token is clearly a school/location/common descriptor
    if lowered[0] in IGNORE_WORDS or lowered[1] in IGNORE_WORDS:
        return True

    return False


def _extract_names_from_text(text):
    candidates = re.findall(FULL_NAME_PATTERN, text)
    cleaned = []

    for name in candidates:
        name = name.strip(" ,.-")
        if not _is_bad_name(name):
            cleaned.append(name)

    return cleaned


def extract_player_name(tweet_text):
    text = _clean_text(tweet_text)

    if not text:
        return None

    lower_text = text.lower()

    # 1) Best method:
    # Look immediately before the portal phrase and take the LAST valid full name.
    for phrase in PORTAL_PHRASES:
        idx = lower_text.find(phrase)
        if idx != -1:
            prefix = text[:idx]
            names_before_phrase = _extract_names_from_text(prefix)

            if names_before_phrase:
                return names_before_phrase[-1]

    # 2) Source/hearing style tweets:
    # "Source: Isaac Tavares intends to enter..."
    source_patterns = [
        r"source[:\s,-]+(?P<name>[A-Z][a-zA-Z\.\-']+\s+[A-Z][a-zA-Z\.\-']+)",
        r"hearing[:\s,-]+(?P<name>[A-Z][a-zA-Z\.\-']+\s+[A-Z][a-zA-Z\.\-']+)",
    ]

    for pattern in source_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            name = match.group("name").strip(" ,.-")
            if not _is_bad_name(name):
                return name

    # 3) Fallback:
    # Use the last valid full name anywhere in the tweet.
    all_names = _extract_names_from_text(text)
    if all_names:
        return all_names[-1]

    return None
