import requests
import csv
import time
from datetime import datetime, timezone

import pandas as pd  # 用来做重采样

# ====== 需要你自己填的：CoinGecko Demo API Key ======
API_KEY = "CG-HwP11oE6qBj5YTf68VP4HtEs"  # 把这里换成你自己的 key，不要传到 GitHub

HEADERS = {
    "accept": "application/json"
}

# 你要抓取的 10 个 memecoin 在 CoinGecko 上的 id
COINGECKO_IDS = {
    "doge":   "dogecoin",
    "shib":   "shiba-inu",
    "pepe":   "pepe",
    "bonk":   "bonk",
    "floki":  "floki",
    "bome":   "book-of-meme",
    "mog":    "mog-coin",
    "wif":    "dogwifhat",
    "popcat": "popcat",
    "brett":  "brett"
}

VS_CURRENCY = "usd"
DAYS = 30

RAW_CSV = "prices_raw.csv"
HOURLY_CSV = "prices_hourly_resampled.csv"


def fetch_market_chart(coin_gecko_id, vs_currency="usd", days=30):
    """
    调用 CoinGecko 的 market_chart 接口。
    注意：不再使用 interval=hourly（那是企业版才有），
    直接让它自动选择粒度。
    """
    url = (
        f"https://api.coingecko.com/api/v3/coins/{coin_gecko_id}/market_chart"
        f"?vs_currency={vs_currency}&days={days}"
        f"&x_cg_demo_api_key={API_KEY}"
    )
    print(f"Fetching: {url}")
    resp = requests.get(url, headers=HEADERS, timeout=20)
    print("status:", resp.status_code, "body:", resp.text[:120], "...")
    resp.raise_for_status()
    return resp.json()


def timestamp_ms_to_utc(ts_ms):
    """把毫秒时间戳转成 UTC 的时间字符串，方便写 CSV / MySQL DATETIME。"""
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def fetch_and_save_raw():
    """
    第一步：从 CoinGecko 抓数据，保存成 prices_raw.csv
    列：
        coin_id, timestamp_utc, close_price, market_cap, total_volume
    """
    with open(RAW_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "coin_id",
            "timestamp_utc",
            "close_price",
            "market_cap",
            "total_volume"
        ])

        for coin_id, cg_id in COINGECKO_IDS.items():
            try:
                data = fetch_market_chart(cg_id, vs_currency=VS_CURRENCY, days=DAYS)
            except Exception as e:
                print(f"[ERROR] Failed to fetch {coin_id}: {e}")
                # 如果被限流，可以稍微睡一会
                if "429" in str(e):
                    print("Hit rate limit, sleeping 20s...")
                    time.sleep(20)
                continue

            prices = data.get("prices", [])  # 每个元素：[timestamp_ms, price]
            market_caps = {mc[0]: mc[1] for mc in data.get("market_caps", [])}
            total_volumes = {tv[0]: tv[1] for tv in data.get("total_volumes", [])}

            print(f"{coin_id}: got {len(prices)} points")

            for ts_ms, price in prices:
                ts_str = timestamp_ms_to_utc(ts_ms)
                market_cap = market_caps.get(ts_ms, "")
                total_volume = total_volumes.get(ts_ms, "")

                writer.writerow([
                    coin_id,
                    ts_str,
                    f"{price:.8f}",
                    f"{market_cap:.2f}" if market_cap != "" else "",
                    f"{total_volume:.2f}" if total_volume != "" else ""
                ])

            # 每个币之间稍微停一下，尊重一下 API 
            time.sleep(1)

    print(f"Raw data saved to {RAW_CSV}")


def resample_to_hourly():
    """
    第二步：用 pandas 把不规则时间点重采样成每小时一条记录，
    并保存为 prices_hourly_resampled.csv
    """
    print(f"Loading raw data from {RAW_CSV} ...")
    df = pd.read_csv(RAW_CSV)

    # 转成 datetime 类型
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])

    # 确保数值列是数值类型
    df["close_price"] = pd.to_numeric(df["close_price"], errors="coerce")
    df["market_cap"] = pd.to_numeric(df["market_cap"], errors="coerce")
    df["total_volume"] = pd.to_numeric(df["total_volume"], errors="coerce")

    hourly_list = []

    for coin_id, g in df.groupby("coin_id"):
        print(f"Resampling {coin_id} ...")
        g = g.set_index("timestamp_utc").sort_index()

        # 按小时重采样：
        #   - close_price：取该小时最后一个价格（更接近“收盘价”概念）
        #   - market_cap / total_volume：同样取最后一个（也可以改成 mean/sum）
        h = g.resample("1H").last()

        # 去掉没有任何价格的小时
        h = h.dropna(subset=["close_price"])

        # 重新把 coin_id 放回列里
        h["coin_id"] = coin_id

        hourly_list.append(h.reset_index())

    if not hourly_list:
        print("No data to resample. Check RAW_CSV.")
        return

    hourly_df = pd.concat(hourly_list, ignore_index=True)

    # 按 coin_id + 时间排序一下，方便导入 MySQL 和调试
    hourly_df = hourly_df.sort_values(by=["coin_id", "timestamp_utc"])

    hourly_df.to_csv(HOURLY_CSV, index=False)
    print(f"Hourly resampled data saved to {HOURLY_CSV}")
    print(hourly_df.head())
    print("Rows per coin:")
    print(hourly_df.groupby("coin_id")["timestamp_utc"].count())


def main():
    fetch_and_save_raw()
    resample_to_hourly()


if __name__ == "__main__":
    main()