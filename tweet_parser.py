import re


NAME_PATTERN = r"[A-Z][a-zA-Z\.\-']+(?:\s+[A-Z][a-zA-Z\.\-']+){1,3}"


def cleanup_name(name):
    if not name:
        return None

    name = re.sub(r"\s+", " ", name).strip(" ,.-")
    return name


def looks_like_name(value):
    if not value:
        return False

    parts = value.split()
    if len(parts) < 2 or len(parts) > 4:
        return False

    banned_starters = {
        "source", "hearing", "report", "reported", "southern", "mississippi",
        "college", "university", "basketball", "guard", "forward", "center",
        "junior", "senior", "freshman", "sophomore"
    }

    if parts[0].lower() in banned_starters:
        return False

    return True


def extract_player_name(tweet_text):
    if not tweet_text:
        return None

    text = tweet_text.replace("\n", " ").strip()

    patterns = [
        # Standard clean format
        rf"(?P<name>{NAME_PATTERN})\s+(?:has\s+)?entered the transfer portal",
        rf"(?P<name>{NAME_PATTERN})\s+plans to enter the transfer portal",
        rf"(?P<name>{NAME_PATTERN})\s+intends to enter the transfer portal",
        rf"(?P<name>{NAME_PATTERN})\s+is entering the transfer portal",
        rf"(?P<name>{NAME_PATTERN})\s+will enter the transfer portal",
        rf"(?P<name>{NAME_PATTERN})\s+has hit the transfer portal",
        rf"(?P<name>{NAME_PATTERN})\s+hit the transfer portal",

        # Source / hearing style
        rf"source[:\s,]+(?P<name>{NAME_PATTERN})\s+(?:has\s+)?entered the transfer portal",
        rf"source[:\s,]+(?P<name>{NAME_PATTERN})\s+plans to enter the transfer portal",
        rf"source[:\s,]+(?P<name>{NAME_PATTERN})\s+intends to enter the transfer portal",
        rf"hearing[:\s,]+(?P<name>{NAME_PATTERN})\s+(?:has\s+)?entered the transfer portal",
        rf"hearing[:\s,]+(?P<name>{NAME_PATTERN})\s+plans to enter the transfer portal",
        rf"hearing[:\s,]+(?P<name>{NAME_PATTERN})\s+intends to enter the transfer portal",

        # Descriptive prefix before actual player name
        rf"(?:[A-Z][a-zA-Z&\.\-']+\s+){{1,4}}(?:\d-\d\s+)?(?:freshman|sophomore|junior|senior|guard|forward|center)?\s*(?P<name>{NAME_PATTERN})\s+intends to enter the transfer portal",
        rf"(?:[A-Z][a-zA-Z&\.\-']+\s+){{1,4}}(?:\d-\d\s+)?(?:freshman|sophomore|junior|senior|guard|forward|center)?\s*(?P<name>{NAME_PATTERN})\s+plans to enter the transfer portal",
        rf"(?:[A-Z][a-zA-Z&\.\-']+\s+){{1,4}}(?:\d-\d\s+)?(?:freshman|sophomore|junior|senior|guard|forward|center)?\s*(?P<name>{NAME_PATTERN})\s+(?:has\s+)?entered the transfer portal",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            name = cleanup_name(match.group("name"))
            if looks_like_name(name):
                return name

    # Fallback: take the 2-4 word capitalized phrase immediately before portal phrase
    fallback_patterns = [
        rf"(?P<prefix>.+?)\s+(?:has\s+)?entered the transfer portal",
        rf"(?P<prefix>.+?)\s+plans to enter the transfer portal",
        rf"(?P<prefix>.+?)\s+intends to enter the transfer portal",
        rf"(?P<prefix>.+?)\s+is entering the transfer portal",
    ]

    for pattern in fallback_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            prefix = match.group("prefix")
            name_matches = re.findall(NAME_PATTERN, prefix)
            if name_matches:
                candidate = cleanup_name(name_matches[-1])
                if looks_like_name(candidate):
                    return candidate

    return None
