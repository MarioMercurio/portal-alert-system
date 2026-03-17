def get_hdi_emoji(hdi_value):
    try:
        hdi = float(hdi_value)
    except Exception:
        return ""

    if hdi >= 90:
        return "💰"
    if hdi >= 85:
        return "🧨"
    if hdi >= 80:
        return "🔥"
    return ""


def format_portal_alert(player_name, school, hdi, reporter, tweet_url, report_url):
    emoji = get_hdi_emoji(hdi)

    subject = f"🚨 Portal Entry: {player_name}"

    body = (
        f"🚨 Portal Entry\n\n"
        f"{player_name} – {school}\n"
        f"HDI: {hdi} {emoji}\n\n"
        f"Reported by: @{reporter}\n\n"
        f"Tweet:\n{tweet_url}\n\n"
        f"Report:\n{report_url}"
    )

    return subject, body
