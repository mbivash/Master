from dataclasses import dataclass
from typing import Callable

import pandas as pd


@dataclass(frozen=True)
class BacktestConfig:
    initial_cash: float = 100_000.0
    fee_bps: float = 5.0
    slippage_bps: float = 5.0
    position_fraction: float = 0.10
    min_signal: float = 0.60


@dataclass(frozen=True)
class BacktestResult:
    equity: pd.Series
    trades: pd.DataFrame
    total_return: float
    max_drawdown: float
    win_rate: float
    profit_factor: float


def run_backtest(
    bars: pd.DataFrame,
    signal_fn: Callable[[pd.DataFrame], float],
    config: BacktestConfig = BacktestConfig(),
) -> BacktestResult:
    """Long-only, next-bar execution baseline.

    signal_fn receives history through the current bar and returns [-1, 1].
    A signal is executed on the next bar, preventing look-ahead from the
    strategy callback. Fees and slippage are charged on both entry and exit.
    """
    required = {"timestamp", "close"}
    missing = required - set(bars.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if len(bars) < 2:
        raise ValueError("At least two bars are required")

    cash = config.initial_cash
    qty = 0.0
    entry_value = 0.0
    rows = []
    equity_rows = []

    for i in range(len(bars)):
        price = float(bars.iloc[i]["close"])
        equity = cash + qty * price
        equity_rows.append((bars.iloc[i]["timestamp"], equity))

        if i == len(bars) - 1:
            continue

        signal = float(signal_fn(bars.iloc[: i + 1]))
        signal = max(-1.0, min(1.0, signal))
        target = config.position_fraction if signal >= config.min_signal else 0.0
        next_price = float(bars.iloc[i + 1]["close"])
        target_value = equity * target
        current_value = qty * next_price
        delta = target_value - current_value

        if abs(delta) < 1e-9:
            continue

        cost_rate = (config.fee_bps + config.slippage_bps) / 10_000
        if delta > 0:
            fill = next_price * (1 + config.slippage_bps / 10_000)
            buy_qty = delta / fill
            cost = delta * cost_rate
            cash -= delta + cost
            qty += buy_qty
            entry_value += delta + cost
        else:
            sell_value = min(-delta, qty * next_price)
            fill = next_price * (1 - config.slippage_bps / 10_000)
            sell_qty = sell_value / next_price
            proceeds = sell_qty * fill
            cost = proceeds * config.fee_bps / 10_000
            cash += proceeds - cost
            qty -= sell_qty
            if qty <= 1e-12:
                trade_pnl = cash - (config.initial_cash if not rows else rows[-1]["cash_after"])
                rows.append({"timestamp": bars.iloc[i + 1]["timestamp"], "action": "EXIT", "pnl": trade_pnl, "cash_after": cash})
                qty = 0.0
                entry_value = 0.0

    equity_df = pd.DataFrame(equity_rows, columns=["timestamp", "equity"]).drop_duplicates("timestamp").set_index("timestamp")
    eq = equity_df["equity"]
    total_return = eq.iloc[-1] / config.initial_cash - 1
    drawdown = eq / eq.cummax() - 1
    max_drawdown = float(drawdown.min())
    trades = pd.DataFrame(rows)
    if trades.empty or "pnl" not in trades:
        win_rate = 0.0
        profit_factor = 0.0
    else:
        pnl = trades["pnl"].astype(float)
        win_rate = float((pnl > 0).mean())
        gains = pnl[pnl > 0].sum()
        losses = -pnl[pnl < 0].sum()
        profit_factor = float(gains / losses) if losses else float("inf") if gains else 0.0

    return BacktestResult(eq, trades, float(total_return), max_drawdown, win_rate, profit_factor)
