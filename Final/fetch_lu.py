"""
Fetch hourly "social-ish" time series for memecoins using
LunarCrush /api4/public/coins/:coin/time-series/v2.

- 使用 Bearer Token（Authorization 头）
- bucket = hour, interval = 1m  -> 最近 1 个月的按小时数据
- 从每个点里取：
    time  -> ts
    spam  -> total_mentions (social 热度代理)

写出 CSV: social_mentions_lc_v2.csv
列结构兼容你现有 MySQL social_mentions 表:
    coin_id, ts, twitter_mentions, reddit_mentions, telegram_mentions, total_mentions
"""

import csv
import time as time_module
from datetime import datetime, timezone
from typing import Any, Dict, List

import requests

# ------------- 配置区 ------------- #

# 这里填你在 LunarCrush Playground 右上角/账户里拿到的 Bearer TOKEN
API_TOKEN = "4uy7j29xeogorj49hl7monksblmim9l83i4ko38"

BASE_URL = "https://lunarcrush.com/api4"

# 你项目里用的 coin_id 以及对应的符号（路径里的 :coin）
COINS = [
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

# bucket: 按小时分桶；interval: 最近 1 个月
BUCKET = "hour"
INTERVAL = "1m"

OUTPUT_CSV = "social_mentions_lc_v2.csv"


# ------------- 工具函数 ------------- #

def normalize_unix_timestamp(raw_ts: Any) -> int:
    """把 time 字段规范成 Unix 秒级时间戳."""
    if raw_ts is None:
        raise ValueError("Timestamp is None")

    if isinstance(raw_ts, str):
        raw_ts = float(raw_ts)
    elif not isinstance(raw_ts, (int, float)):
        raw_ts = float(raw_ts)

    # 如果是毫秒级（大于 10^12），除以 1000
    if raw_ts > 10**12:
        raw_ts = raw_ts / 1000.0

    return int(raw_ts)


def unix_to_hour_dt(ts_unix: int) -> datetime:
    """Unix 秒 -> UTC 小时起始时间（分钟/秒清零）."""
    dt = datetime.fromtimestamp(ts_unix, tz=timezone.utc)
    return dt.replace(minute=0, second=0, microsecond=0)


def parse_timeseries_list(ts_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """解析 time-series 列表为统一结构."""
    rows: List[Dict[str, Any]] = []

    for point in ts_list:
        if not isinstance(point, dict):
            continue

        raw_ts = point.get("time") or point.get("timestamp") or point.get("t")
        if raw_ts is None:
            continue

        try:
            unix_ts = normalize_unix_timestamp(raw_ts)
        except Exception:
            continue

        ts_dt = unix_to_hour_dt(unix_ts)

        spam = point.get("spam") or 0
        try:
            spam = int(spam)
        except Exception:
            spam = 0

        rows.append(
            {
                "ts": ts_dt,
                "twitter": 0,
                "reddit": 0,
                "telegram": 0,
                "total": spam,
            }
        )

    rows.sort(key=lambda r: r["ts"])
    return rows


def fetch_coin_timeseries_v2(symbol: str) -> List[Dict[str, Any]]:
    """
    调用 /api4/public/coins/:coin/time-series/v2 拿 time series 数据。

    ⚠ 注意：
    - 如果 Playground 的实际路径跟这里不同（比如还有 /public/coins/coin/time-series/v2?coin=ETH），
      就把下面的 url 拼接方式改成和 Playground 完全一致。
    """

    # 根据文档：/public/coins/:coin/time-series/v2
    url = f"{BASE_URL}/public/coins/{symbol}/time-series/v2"

    params = {
        "bucket": BUCKET,    # 'hour'
        "interval": INTERVAL # '1m' 最近一个月；如果你改成 start/end，就在这里加上
        # 例如：
        # "start": 1730419200,
        # "end":   1733011200,
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
    }

    print(f"[{symbol}] Request {url} params={params}")
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    print(f"[{symbol}] HTTP {resp.status_code}")

    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        print(f"  [ERROR] HTTP error for {symbol}: {e}")
        print("  Body:", resp.text[:500])
        raise

    try:
        data = resp.json()
    except Exception as e:
        print(f"  [ERROR] JSON parse error for {symbol}: {e}")
        print("  Raw:", resp.text[:500])
        raise

    # 根据 v2 文档调整这里：
    # 常见几种可能的结构，下面尽量兼容：
    #
    # 1) { "data": [ { "timeSeries": [ {...}, {...} ] } ] }
    # 2) { "data": [ {...}, {...} ] }  其中每个 {...} 就是一个点
    # 3) 直接就是 [ {...}, {...} ]
    #
    ts_list: List[Dict[str, Any]] = []

    if isinstance(data, dict):
        # 打一行 debug，让你看看实际长啥样（跑一次就够了）
        print(f"  [DEBUG] root keys for {symbol}:", list(data.keys()))

        # 情况 1、2
        container = data.get("data") or data.get("result") or data.get("values")
        if isinstance(container, list):
            if container and isinstance(container[0], dict):
                # 如果第一层就有 'time' 字段，那说明 container 就是点数组
                if "time" in container[0]:
                    ts_list = container  # type: ignore[assignment]
                else:
                    # 否则再从第一个元素里找 time series 列表
                    first = container[0]
                    ts_list = (
                        first.get("timeSeries")
                        or first.get("time_series")
                        or first.get("timeseries")
                        or first.get("values")
                        or []
                    )
        elif isinstance(container, dict):
            ts_list = (
                container.get("timeSeries")
                or container.get("time_series")
                or container.get("timeseries")
                or container.get("values")
                or []
            )
        else:
            # data 本身可能就是列表
            if isinstance(data, list):
                ts_list = data  # type: ignore[assignment]
    elif isinstance(data, list):
        ts_list = data  # type: ignore[assignment]

    if not ts_list:
        print(f"  [WARN] No time series list for {symbol}")
        return []

    rows = parse_timeseries_list(ts_list)
    print(f"  -> got {len(rows)} points for {symbol}")
    return rows


# ------------- 主流程 ------------- #

def main() -> None:
    if not API_TOKEN or API_TOKEN == "PASTE_YOUR_TOKEN_HERE":
        raise RuntimeError("请先在脚本顶部 API_TOKEN 里填入你的 Bearer Token！")

    all_rows: List[List[Any]] = []

    for coin_id, symbol in COINS:
        try:
            rows = fetch_coin_timeseries_v2(symbol)
        except Exception as e:
            print(f"[ERROR] Failed to fetch for {symbol}: {e}")
            continue

        for r in rows:
            ts_str = r["ts"].strftime("%Y-%m-%d %H:%M:%S")
            all_rows.append(
                [
                    coin_id,
                    ts_str,
                    r["twitter"],
                    r["reddit"],
                    r["telegram"],
                    r["total"],
                ]
            )

        # 对 API 礼貌一点，防止 rate limit
        time_module.sleep(1)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "coin_id",
                "ts",
                "twitter_mentions",
                "reddit_mentions",
                "telegram_mentions",
                "total_mentions",
            ]
        )
        writer.writerows(all_rows)

    print(f"\nDone! Wrote {len(all_rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()