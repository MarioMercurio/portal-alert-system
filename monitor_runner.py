from twitter_monitor import process_tweets

def main():
    try:
        alerts = process_tweets(debug=False)
        print(f"Run complete. Alerts sent: {len(alerts)}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
