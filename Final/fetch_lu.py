"""
Fetch hourly social mention data for memecoins using LunarCrush API v2.

Output CSV: social_mentions_lunarcrush.csv

Columns (for MySQL social_mentions table):
    coin_id, ts, twitter_mentions, reddit_mentions, telegram_mentions, total_mentions

- ts: UTC, rounded to the start of the hour, format: YYYY-MM-DD HH:MM:SS
- telegram_mentions: set to 0 for now
"""

import csv
import time
from datetime import datetime, timezone

import requests

# ----------------- CONFIG -----------------

# 你自己的 LunarCrush API Key
API_KEY = "4uy7j29xeogorj49hl7monksblmim9l83i4ko38"

# 最近多少天（和 price_data 对齐，比如 30 天）
DAYS_BACK = 30
DATA_POINTS = DAYS_BACK * 24   # 每小时一个点

# 你的 coin_id 和 LunarCrush 里的 symbol（注意这里是 symbol，不是名字）
COINS = [
    # coin_id   lc_symbol
    ("doge",   "DOGE"),
    ("shib",   "SHIB"),
    ("pepe",   "PEPE"),
    ("bonk",   "BONK"),
    ("floki",  "FLOKI"),
    ("bome",   "BOME"),
    ("mog",    "MOG"),
    ("wif",    "WIF"),
    ("popcat", "POPCAT"),
    ("brett",  "BRETT"),
]

OUTPUT_CSV = "social_mentions_lunarcrush.csv"

API_BASE = "https://api.lunarcrush.com/v2"


# ----------------- HELPER FUNCTIONS -----------------

def unix_to_hour_dt(ts_unix: int) -> datetime:
    """UNIX 秒 → UTC 小时起点 datetime。"""
    dt = datetime.fromtimestamp(ts_unix, tz=timezone.utc)
    # v2 一般 time 已经是整点，但这里保险起见还是 round 一下
    return dt.replace(minute=0, second=0, microsecond=0)


def fetch_coin_social_timeseries_v2(symbol: str):
    """
    调 LunarCrush v2 /v2?data=assets 拿小时级别的 time series。

    返回：list[dict]，每个 dict 代表一个小时：
        {
            "ts": datetime (UTC, hour start),
            "twitter": int,
            "reddit": int,
            "telegram": int (0),
            "total": int,
        }
    """

    params = {
        "data": "assets",
        "symbol": symbol,
        "interval": "hour",          # 小时级
        "data_points": DATA_POINTS,  # 近 30 天
        # 通常 v2 用这个字段告诉它想返回哪些 time series 指标
        "time_series_indicators": "social_volume,tweets,reddit_posts,reddit_comments",
        "key": API_KEY,
    }

    print(f"[{symbol}] Requesting: {API_BASE} with params {params}")
    resp = requests.get(API_BASE, params=params, timeout=30)
    print(f"[{symbol}] HTTP {resp.status_code}")
    resp.raise_for_status()
    data = resp.json()

    # 典型结构：{"data": [ { ..., "timeSeries": [ {...}, {...}, ... ] } ]}
    if not isinstance(data, dict) or "data" not in data:
        print(f"  [WARN] Unexpected JSON structure for {symbol}: type={type(data)} keys={list(data.keys()) if isinstance(data, dict) else None}")
        return []

    assets = data.get("data", [])
    if not assets:
        print(f"  [WARN] No 'data' entries for {symbol}")
        return []

    asset = assets[0]
    ts_list = (
        asset.get("timeSeries")
        or asset.get("time_series")
        or asset.get("timeseries")
        or []
    )

    if not ts_list:
        print(f"  [WARN] No time series for {symbol}. asset keys={list(asset.keys())}")
        return []

    rows = []
    for point in ts_list:
        if not isinstance(point, dict):
            continue

        # 时间字段：常见的是 time
        unix_ts = point.get("time") or point.get("t") or point.get("timestamp")
        if unix_ts is None:
            continue

        try:
            unix_ts = int(unix_ts)
        except Exception:
            try:
                unix_ts = int(float(unix_ts))
            except Exception:
                continue

        ts_dt = unix_to_hour_dt(unix_ts)

        # 社交字段：按可能的 key 尝试
        twitter = (
            point.get("twitter_volume")
            or point.get("tweets")
            or point.get("tweet_volume")
            or point.get("twitter")
            or 0
        )

        # Reddit 可能拆成 posts + comments
        reddit_posts = point.get("reddit_posts") or 0
        reddit_comments = point.get("reddit_comments") or 0
        reddit = (reddit_posts or 0) + (reddit_comments or 0)

        # total 尽量用 social_volume，没有就 twitter + reddit
        total = point.get("social_volume") or point.get("social_score")

        # 转 int，防止 None / str 异常
        try:
            twitter = int(twitter) if twitter is not None else 0
        except Exception:
            twitter = 0

        try:
            reddit = int(reddit) if reddit is not None else 0
        except Exception:
            reddit = 0

        if total is None:
            total = twitter + reddit
        else:
            try:
                total = int(total)
            except Exception:
                total = twitter + reddit

        rows.append({
            "ts": ts_dt,
            "twitter": twitter,
            "reddit": reddit,
            "telegram": 0,   # 现在没有 telegram 数据，先填 0
            "total": total,
        })

    rows.sort(key=lambda r: r["ts"])
    print(f"  -> got {len(rows)} hourly points for {symbol}")
    return rows


# ----------------- MAIN -----------------

def main():
    if not API_KEY:
        raise RuntimeError("请先在脚本顶部填入你的 LunarCrush API key。")

    all_rows = []

    for coin_id, lc_symbol in COINS:
        try:
            rows = fetch_coin_social_timeseries_v2(lc_symbol)
        except requests.HTTPError as e:
            print(f"[ERROR] HTTP error for {lc_symbol}: {e}")
            continue
        except Exception as e:
            print(f"[ERROR] Unexpected error for {lc_symbol}: {e}")
            continue

        for r in rows:
            ts_str = r["ts"].strftime("%Y-%m-%d %H:%M:%S")
            all_rows.append([
                coin_id,         # 你的 coin_id（小写）
                ts_str,          # ts
                r["twitter"],    # twitter_mentions
                r["reddit"],     # reddit_mentions
                r["telegram"],   # telegram_mentions
                r["total"],      # total_mentions
            ])

        # 礼貌一点，避免刷 API 太猛
        time.sleep(1)

    # 写 CSV，列名和 social_mentions 表结构一致
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
        writer.writerows(all_rows)

    print(f"\nDone! Wrote {len(all_rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()