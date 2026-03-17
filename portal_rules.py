TRUSTED_REPORTERS = {
    "goodmanhoops": 3,
    "jeffborzello": 3,
    "tiptonedits": 3,
    "247sportsportal": 3,
    "verbalcommits": 3,
    "mzenitz": 2,
    "on3sports": 2,
    "on3recruits": 2,
    "247hshoops": 2,
}

STRONG_PORTAL_PHRASES = [
    "entered the transfer portal",
    "has entered the transfer portal",
    "is entering the transfer portal",
    "plans to enter the transfer portal",
    "intends to enter the transfer portal",
    "will enter the transfer portal",
    "has hit the transfer portal",
    "hit the transfer portal",
    "in the transfer portal",
]

MEDIUM_PORTAL_PHRASES = [
    "entered the portal",
    "enter the portal",
    "in the portal",
    "hit the portal",
    "expected to enter the transfer portal",
    "expected to hit the portal",
    "testing the transfer portal",
    "testing portal waters",
    "expected to transfer",
]

BASKETBALL_HINTS = [
    "basketball",
    "hoops",
    "guard",
    "forward",
    "center",
    "men's basketball",
    "mens basketball",
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

    for phrase in STRONG_PORTAL_PHRASES:
        if phrase in text:
            score += 4
            reasons.append(f"strong_phrase:{phrase}")
            break

    for phrase in MEDIUM_PORTAL_PHRASES:
        if phrase in text:
            score += 2
            reasons.append(f"medium_phrase:{phrase}")
            break

    combined = f"{text} {author} {username}"
    if any(hint in combined for hint in BASKETBALL_HINTS):
        score += 1
        reasons.append("basketball_hint")

    return score, reasons


def is_likely_portal_tweet(
    tweet_text: str,
    author_username: str = "",
    author_name: str = "",
    min_score: int = 4,
):
    score, reasons = score_tweet(tweet_text, author_username, author_name)
    return score >= min_score, score, reasons
