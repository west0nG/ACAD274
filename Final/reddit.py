# reddit_mentions_pushshift.py
import requests
import pandas as pd
from datetime import datetime, timedelta

COINS = [
    ("doge", "doge"),
    ("shib", "shib"),
    ("pepe", "pepe"),
    ("bonk", "bonk"),
    ("floki", "floki"),
    ("bome", "bome"),
    ("mog", "mog"),
    ("wif", "wif"),
    ("popcat", "popcat"),
    ("brett", "brett"),
]

OUTPUT_CSV = "reddit_mentions_sentiment.csv"
BASE_URL = "https://api.pushshift.io/reddit/search/comment/"

DAYS_BACK = 30  # 最近 30 天

def fetch_day_count(keyword: str, day: datetime) -> int:
    """统计某一天（UTC）里，包含 keyword 的评论数量（简单版，可能截断但作业够用）"""
    start = int(datetime(day.year, day.month, day.day).timestamp())
    end = int((datetime(day.year, day.month, day.day) + timedelta(days=1)).timestamp())

    params = {
        "q": keyword,
        "after": start,
        "before": end,
        "size": 500,         # pushshift 单次最大条数，简单起见只取一次
        "sort": "desc",
    }

    try:
        r = requests.get(BASE_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json().get("data", [])
        return len(data)
    except Exception as e:
        print(f"  [WARN] error for {keyword} {day.date()}: {e}")
        return 0

def main():
    rows = []
    today = datetime.utcnow().date()

    for coin_id, keyword in COINS:
        print(f"[Reddit] {coin_id} / keyword = {keyword}")
        for i in range(DAYS_BACK):
            day = today - timedelta(days=i)
            count = fetch_day_count(keyword, datetime.combine(day, datetime.min.time()))
            rows.append([coin_id, day, count])

    df = pd.DataFrame(rows, columns=["coin_id", "date", "reddit_posts"])
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved {len(df)} rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()