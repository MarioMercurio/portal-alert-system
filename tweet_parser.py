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

# MUCH stronger filtering
BAD_NAME_PARTS = {
    "southern", "northern", "eastern", "western",
    "mississippi", "texas", "florida", "california",
    "arizona", "ohio", "kansas", "georgia", "louisiana",
    "state", "university", "college", "academy", "school",
    "junior", "senior", "freshman", "sophomore",
    "guard", "forward", "center",
    "men", "mens", "basketball", "hoops",
    "source", "hearing", "report", "reported", "agent"
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

    # 🔴 HARD FILTER: reject anything with bad words
    if p1 in BAD_NAME_PARTS or p2 in BAD_NAME_PARTS:
        return False

    # 🔴 EXTRA PROTECTION: reject if BOTH words are common/location words
    if p1 in BAD_NAME_PARTS and p2 in BAD_NAME_PARTS:
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

    # 🎯 STEP 1 — BEST METHOD:
    # Find portal phrase → take LAST valid name BEFORE it
    for phrase in PORTAL_PHRASES:
        idx = lower_text.find(phrase)
        if idx != -1:
            prefix = text[:idx]
            names = _extract_names(prefix)

            if names:
                return names[-1]

    # 🎯 STEP 2 — "Source:" or "Hearing:" format
    patterns = [
        r"source[:\s,-]+([A-Z][a-zA-Z\.\-']+\s+[A-Z][a-zA-Z\.\-']+)",
        r"hearing[:\s,-]+([A-Z][a-zA-Z\.\-']+\s+[A-Z][a-zA-Z\.\-']+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            name = match.group(1).strip(" ,.-")
            if _is_valid_player_name(name):
                return name

    # 🎯 STEP 3 — fallback: last valid name anywhere
    all_names = _extract_names(text)
    if all_names:
        return all_names[-1]

    return None
