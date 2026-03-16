from hdi_utils import get_hdi_icon

def format_entry_alert(player, school, hdi, reporter, tweet_link, report_link):
    
    icon = get_hdi_icon(hdi)

    message = f"""
🚨 Portal Entry

{player} – {school}
HDI – {hdi} {icon}

Reported by: @{reporter}

Tweet:
{tweet_link}

Report:
{report_link}
"""
    return message
