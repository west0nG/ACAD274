# coingecko_social_features.py
import requests
import pandas as pd
from datetime import date
import time

# 映射：你数据库里的 coin_id -> CoinGecko 的 coin id
COINS = [
    ("doge",   "dogecoin"),
    ("shib",   "shiba-inu"),
    ("pepe",   "pepe"),
    ("bonk",   "bonk"),
    ("floki",  "floki"),
    ("bome",   "book-of-meme"),
    ("mog",    "mog-coin"),
    ("wif",    "dogwifhat"),  # 如果有问题再改成 "dogwifcoin"
    ("popcat", "popcat"),
    ("brett",  "brett"),
]

BASE_URL = "https://api.coingecko.com/api/v3/coins/"
OUTPUT_CSV = "coingecko_social_features.csv"

def fetch_coin_social(coin_id: str, cg_id: str):
    """从 CoinGecko 拉单个币的情绪 + 社区数据，返回 dict"""
    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "false",       # 价格你已经有了，就不重复拉
        "community_data": "true",
        "developer_data": "false",
        "sparkline": "false",
    }

    url = BASE_URL + cg_id
    print(f"[CG] Fetching {coin_id} ({cg_id}) -> {url}")

    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()

    # 情绪
    sentiment_up   = data.get("sentiment_votes_up_percentage")
    sentiment_down = data.get("sentiment_votes_down_percentage")

    # 社区数据
    community = data.get("community_data") or {}
    twitter_followers         = community.get("twitter_followers")
    reddit_subscribers        = community.get("reddit_subscribers")
    reddit_posts_48h          = community.get("reddit_average_posts_48h")
    reddit_comments_48h       = community.get("reddit_average_comments_48h")
    telegram_channel_users    = community.get("telegram_channel_user_count")

    # 一些额外的“热度”指标（可选）
    public_interest = data.get("public_interest_stats") or {}
    alexa_rank      = public_interest.get("alexa_rank")

    return {
        "coin_id": coin_id,
        "date": date.today(),  # 快照日期（今天）
        "cg_sentiment_up_pct": sentiment_up,
        "cg_sentiment_down_pct": sentiment_down,
        "cg_twitter_followers": twitter_followers,
        "cg_reddit_subscribers": reddit_subscribers,
        "cg_reddit_posts_48h": reddit_posts_48h,
        "cg_reddit_comments_48h": reddit_comments_48h,
        "cg_telegram_users": telegram_channel_users,
        "cg_alexa_rank": alexa_rank,
    }

def main():
    rows = []

    for coin_id, cg_id in COINS:
        try:
            row = fetch_coin_social(coin_id, cg_id)
            rows.append(row)
        except requests.HTTPError as e:
            print(f"  [HTTP ERROR] {coin_id} ({cg_id}): {e}")
        except Exception as e:
            print(f"  [ERROR] {coin_id} ({cg_id}): {e}")

        # 简单防一下 rate limit
        time.sleep(12)

    if not rows:
        print("No data fetched, abort.")
        return

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved {len(df)} rows to {OUTPUT_CSV}")
    print(df)

if __name__ == "__main__":
    main()
