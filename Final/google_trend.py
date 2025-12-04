# google_trends_sentiment.py
from pytrends.request import TrendReq
import pandas as pd

COINS = [
    ("doge", "dogecoin"),
    ("shib", "shiba inu"),
    ("pepe", "pepe coin"),
    ("bonk", "bonk crypto"),
    ("floki", "floki coin"),
    ("bome", "bome crypto"),
    ("mog", "mog coin"),
    ("wif", "dogwifhat"),
    ("popcat", "popcat crypto"),
    ("brett", "brett crypto"),
]

OUTPUT_CSV = "google_trends_sentiment.csv"

def main():
    pytrend = TrendReq(hl='en-US', tz=0)  # UTC

    rows = []

    for coin_id, keyword in COINS:
        print(f"[GT] {coin_id} / keyword = {keyword}")
        # 最近 30 天，Google 会给你按天的数据
        pytrend.build_payload(
            kw_list=[keyword],
            timeframe="today 1-m",  # 也可以改成 "today 3-m"
            geo=""
        )
        df = pytrend.interest_over_time()

        if df.empty:
            print(f"  -> empty for {keyword}")
            continue

        df = df.reset_index()  # 把 date 从 index 变成列

        for _, row in df.iterrows():
            date = row["date"].date()              # datetime -> date
            score = int(row[keyword])              # 搜索热度 0~100
            rows.append([coin_id, date, score])

    out_df = pd.DataFrame(rows, columns=["coin_id", "date", "google_interest"])
    out_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved {len(out_df)} rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()