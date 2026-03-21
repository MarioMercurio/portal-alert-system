TRUSTED_REPORTERS = {
    "goodmanhoops": 3,
    "jeffborzello": 3,
    "tiptonedits": 3,
    "verbalcommits": 3,
    "on3sports": 2,
    "travisbranham_": 2,
    "247sportsportal": 2,
}

STRONG_PORTAL_PHRASES = [
    "entered the transfer portal",
    "has entered the transfer portal",
    "plans to enter the transfer portal",
    "intends to enter the transfer portal",
    "is entering the transfer portal",
    "will enter the transfer portal",
    "expected to enter the transfer portal",
    "has hit the transfer portal",
    "hit the transfer portal",
]

MEDIUM_PORTAL_PHRASES = [
    "entered the portal",
    "enter the portal",
    "will enter the portal",
    "plans to enter the portal",
    "intends to enter the portal",
    "expected to enter the portal",
    "testing the transfer portal",
    "testing the waters",
]

WEAK_OR_NOISY_PHRASES = [
    "in the transfer portal",
    "transfer portal",
    "portal",
]

NEGATIVE_PHRASES = [
    "wouldn't be surprised",
    "would not be surprised",
    "maybe",
    "possibly",
    "could enter",
    "might enter",
    "if he enters",
    "if they enter",
    "if these guys leave",
    "thank you for the season",
    "future of the program",
    "continue being competitive",
]

BASKETBALL_HINTS = [
    "basketball",
    "hoops",
    "guard",
    "forward",
    "center",
    "junior",
    "senior",
    "freshman",
    "sophomore",
    "f/c",
    "mbb",
]


def score_tweet(tweet_text: str, author_username: str = "", author_name: str = ""):
    text = (tweet_text or "").lower()
    username = (author_username or "").lower().replace("@", "").strip()
    author = (author_name or "").lower()

    score = 0
    reasons = []

    if username in TRUSTED_REPORTERS:
        score += TRUSTED_REPORTERS[username]
        reasons.append(f"trusted_reporter:{username}")

    strong_hit = False
    for phrase in STRONG_PORTAL_PHRASES:
        if phrase in text:
            score += 4
            reasons.append(f"strong_phrase:{phrase}")
            strong_hit = True
            break

    if not strong_hit:
        for phrase in MEDIUM_PORTAL_PHRASES:
            if phrase in text:
                score += 2
                reasons.append(f"medium_phrase:{phrase}")
                break

    combined = f"{text} {author} {username}"
    if any(hint in combined for hint in BASKETBALL_HINTS):
        score += 1
        reasons.append("basketball_hint")

    for phrase in NEGATIVE_PHRASES:
        if phrase in text:
            score -= 3
            reasons.append(f"negative_phrase:{phrase}")
            break

    return score, reasons


def is_likely_portal_tweet(
    tweet_text: str,
    author_username: str = "",
    author_name: str = "",
    min_score: int = 4,
):
    score, reasons = score_tweet(tweet_text, author_username, author_name)
    return score >= min_score, score, reasons
