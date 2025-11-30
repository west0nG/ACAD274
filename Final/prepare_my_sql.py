import pandas as pd

INPUT = "prices_hourly_resampled.csv"
OUTPUT = "ready_for_mysql_import.csv"

def main():
    print("Loading:", INPUT)
    df = pd.read_csv(INPUT)

    # 确保列存在（你可以 print 一下确认）
    print("Columns in input CSV:", df.columns.tolist())

    # 1. 类型转换
    # close_price 一定要是 float
    df["close_price"] = pd.to_numeric(df["close_price"], errors="coerce")

    # total_volume -> volume_usd（先存在 df 里一列）
    if "total_volume" in df.columns:
        df["volume_usd"] = pd.to_numeric(df["total_volume"], errors="coerce")
    else:
        # 如果真的没有 total_volume，就先填 None
        df["volume_usd"] = None

    # 2. 映射到 MySQL 需要的结构
    df_mysql = pd.DataFrame()
    df_mysql["coin_id"] = df["coin_id"]
    df_mysql["ts"] = pd.to_datetime(df["timestamp_utc"])

    # 开、高、低 都用 close_price 占位
    df_mysql["open_price"] = df["close_price"]
    df_mysql["high_price"] = df["close_price"]
    df_mysql["low_price"]  = df["close_price"]
    df_mysql["close_price"] = df["close_price"]

    # volume_usd 从我们刚才算出来的列拷贝
    df_mysql["volume_usd"] = df["volume_usd"]

    # 排序更整齐
    df_mysql = df_mysql.sort_values(by=["coin_id", "ts"])

    # 导出
    df_mysql.to_csv(OUTPUT, index=False)

    print("File generated:", OUTPUT)
    print(df_mysql.head())
    print("Columns in output CSV:", df_mysql.columns.tolist())

if __name__ == "__main__":
    main()



