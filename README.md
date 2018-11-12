

# Backtester

This project is a just a boilerplate that demonstrates usage of PyAlgoTrage library for backtesting your own strategies.

Some sample strategies can be found in `strategies/` dir.


## Usage

Clone this repo and run pip to install other required packages.

    pip install -r requirements.txt

To transform hourly data feed from JSON to CSV and set appropriate column names run a simple Pandas script
`transform_json_to_csv.py`. This way we can later simply use `GenericBarFeed` when passing bar feed.

    python transform_json_to_csv.py

Run example strategy with default settings.

    python strategies/s01_sma_cross.py

