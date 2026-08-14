# Qlib integration

Qlib is used as the quantitative research/data-processing layer, not as a claim of free real-time NSE data.

The adapter boundary is intentionally small so the project can support:

- Qlib historical datasets
- local CSV/Parquet market data
- a future licensed/live Indian-market provider

Kronos expects normalized OHLCV candles; this project converts upstream data into that contract before forecasting.

Install the optional dependency with `pip install -e '.[qlib]'` when Qlib is available in the environment.
