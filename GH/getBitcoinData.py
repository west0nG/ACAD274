import yfinance as yf

btc = yf.download("BTC-USD", start="2020-01-01", end="2024-12-31")
print(btc.head())

btc.to_csv("btc_data.csv")

