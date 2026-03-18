import re

# Common words / phrases to ignore
IGNORE_WORDS = {
    "University", "College", "State", "Southern", "Northern",
    "Eastern", "Western", "Mississippi", "Texas", "Florida",
    "California", "Carolina", "Kansas", "Ohio"
}


def extract_player_name(text):
    """
    Extract most likely player name from tweet text.
    """

    if not text:
        return None

    # Clean text
    text = text.replace("\n", " ")

    # Step 1: Find all capitalized word pairs (possible names)
    candidates = re.findall(r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b", text)

    if not candidates:
        return None

    # Step 2: Remove obvious non-player phrases
    filtered = []
    for name in candidates:
        parts = name.split()

        if any(word in IGNORE_WORDS for word in parts):
            continue

        filtered.append(name)

    if not filtered:
        filtered = candidates  # fallback

    # Step 3: Prioritize names near portal language
    portal_phrases = [
        "entered the transfer portal",
        "enter the transfer portal",
        "intends to enter",
        "in the transfer portal"
    ]

    text_lower = text.lower()

    for phrase in portal_phrases:
        if phrase in text_lower:
            # Get nearby text window
            idx = text_lower.index(phrase)
            window = text[max(0, idx - 80): idx + 80]

            for name in filtered:
                if name in window:
                    return name

    # Step 4: fallback → return first clean candidate
    return filtered[0]
