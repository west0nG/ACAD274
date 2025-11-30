"""
Fetch hourly Twitter mention counts for memecoins using snscrape.

Output CSV structure:
coin_id, ts, twitter_mentions, reddit_mentions, telegram_mentions, total_mentions

- ts is in UTC and rounded to the start of the hour: YYYY-MM-DD HH:00:00
- reddit_mentions and telegram_mentions are set to 0 for now
- total_mentions = twitter_mentions (you can later add reddit/telegram)
"""

import csv
from datetime import datetime, timedelta, timezone

# ---- hack: globally disable SSL verify for requests (used inside snscrape) ----
import requests

_old_request = requests.sessions.Session.request

def _no_verify_request(self, method, url, **kwargs):
    # 如果外面没指定 verify，就强制关掉 SSL 验证
    kwargs.setdefault("verify", False)
    return _old_request(self, method, url, **kwargs)

requests.sessions.Session.request = _no_verify_request
# ---------------------------------------------------------------------------

import snscrape.modules.twitter as sntwitter


# -------- CONFIGURATION --------

# How many days back from now you want to fetch
DAYS_BACK = 30

# Safety cap for max tweets per coin (to avoid infinite scraping)
MAX_TWEETS_PER_COIN = 20000

# Your coin list and search queries on Twitter
# You can tweak these queries later if you want
COINS = [
    {"coin_id": "doge",   "query": "dogecoin OR $DOGE"},
    {"coin_id": "shib",   "query": "shiba inu OR $SHIB"},
    {"coin_id": "pepe",   "query": "pepe coin OR $PEPE"},
    {"coin_id": "bonk",   "query": "bonk coin OR $BONK"},
    {"coin_id": "floki",  "query": "floki OR $FLOKI"},
    {"coin_id": "bome",   "query": "bome coin OR $BOME"},
    {"coin_id": "mog",    "query": "mog coin OR $MOG"},
    {"coin_id": "wif",    "query": "\"dog wif hat\" OR $WIF"},
    {"coin_id": "popcat", "query": "popcat OR $POPCAT"},
    {"coin_id": "brett",  "query": "brett coin OR $BRETT"},
]

OUTPUT_CSV = "twitter_mentions_hourly.csv"


def truncate_to_hour(dt: datetime) -> datetime:
    """Return dt truncated to the start of the hour (UTC)."""
    # Ensure timezone-aware UTC datetime
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    return dt.replace(minute=0, second=0, microsecond=0)


def fetch_hourly_counts_for_coin(coin_id: str, query: str,
                                 start_dt: datetime,
                                 end_dt: datetime,
                                 max_tweets: int):
    """
    Use snscrape to fetch tweets for a coin and aggregate counts per hour.

    Returns:
        dict[datetime -> int] where datetime is the hour-start in UTC.
    """
    hourly_counts = {}

    # snscrape uses "since:YYYY-MM-DD until:YYYY-MM-DD" (until is exclusive)
    # We extend 'until' by 1 day to make sure we cover end_dt
    since_str = start_dt.date().isoformat()
    until_str = (end_dt + timedelta(days=1)).date().isoformat()

    search_query = f"({query}) since:{since_str} until:{until_str}"
    print(f"[{coin_id}] Query: {search_query}")

    scraper = sntwitter.TwitterSearchScraper(search_query).get_items()

    scraper = sntwitter.TwitterSearchScraper(search_query).get_items()

    tweet_count = 0
    try:
        for tweet in scraper:
            tweet_dt = tweet.date  # already UTC
            # Stop if we went too far back
            if tweet_dt < start_dt:
                break

            # Ignore tweets after end_dt
            if tweet_dt > end_dt:
                continue

            hour_start = truncate_to_hour(tweet_dt)
            hourly_counts[hour_start] = hourly_counts.get(hour_start, 0) + 1

            tweet_count += 1
            if tweet_count >= max_tweets:
                print(f"[{coin_id}] Reached max_tweets={max_tweets}, stopping.")
                break
    except Exception as e:
        print(f"[{coin_id}] ERROR while scraping: {e}")
        # 返回当前已经累计的（可能是空 dict），避免整个脚本崩掉
        return hourly_counts

def main():
    # Use UTC "now" and round down to the current hour
    end_dt = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start_dt = end_dt - timedelta(days=DAYS_BACK)

    print(f"Fetching tweets from {start_dt} to {end_dt} (UTC)")

    # coin_id -> {hour_start -> count}
    all_counts = {}

    for coin in COINS:
        coin_id = coin["coin_id"]
        query = coin["query"]
        counts = fetch_hourly_counts_for_coin(
            coin_id=coin_id,
            query=query,
            start_dt=start_dt,
            end_dt=end_dt,
            max_tweets=MAX_TWEETS_PER_COIN,
        )
        all_counts[coin_id] = counts

    # ---- Write CSV ----
    # CSV header matches your social_mentions table layout as much as possible
    # (assuming columns: coin_id, ts, twitter_mentions, reddit_mentions,
    #  telegram_mentions, total_mentions)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "coin_id",
            "ts",
            "twitter_mentions",
            "reddit_mentions",
            "telegram_mentions",
            "total_mentions",
        ])

        # For each coin, write rows sorted by hour
        for coin in COINS:
            coin_id = coin["coin_id"]
            counts = all_counts.get(coin_id, {})
            for hour_start in sorted(counts.keys()):
                twitter_mentions = counts[hour_start]
                reddit_mentions = 0
                telegram_mentions = 0
                total_mentions = twitter_mentions  # later add reddit/telegram

                ts_str = hour_start.strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow([
                    coin_id,
                    ts_str,
                    twitter_mentions,
                    reddit_mentions,
                    telegram_mentions,
                    total_mentions,
                ])

    print(f"\nDone! CSV saved to: {OUTPUT_CSV}")
    print("You can now import this into your `social_mentions` table.")


if __name__ == "__main__":
    main()