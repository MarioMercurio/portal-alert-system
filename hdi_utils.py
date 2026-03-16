def get_hdi_icon(hdi):
    if hdi is None:
        return ""
    if hdi >= 90:
        return "💰"
    if hdi >= 85:
        return "🧨"
    if hdi >= 80:
        return "🔥"
    return ""
