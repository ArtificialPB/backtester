import pandas as pd

df = pd.read_json('data/btcusd_1h.json')
df.set_index('timestamp', inplace=True)

df.index.names = ['Date Time']
df = df.rename(index=str, columns={
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close",
    "timestamp": "Date Time",
    "volume": "Volume"
})

df.to_csv('data/btcusd_1h.csv')
