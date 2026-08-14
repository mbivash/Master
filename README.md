# Master — Autonomous Quant Research & Paper Trading

Master is a research-first autonomous trading laboratory built around probabilistic market forecasting, regime detection, strategy ensembles, edge monitoring, risk firewalls, and paper execution.

## Safety boundary

The initial release is **paper-trading only**. No broker credentials are required and no real-money orders are implemented. Live execution is intentionally isolated behind a broker interface and a hard risk firewall.

## Architecture

```text
Market Data -> Features -> Kronos Forecast -> Regime -> Strategy Ensemble
                                               -> Edge Monitor
                                                        -> Portfolio/Risk Firewall
                                                        -> Paper Execution
                                                        -> Trade Autopsy
                                                        -> Research Experiments
```

## Design principles

1. Never trust a single model.
2. Measure expected value after costs, not prediction accuracy alone.
3. Detect regime changes before increasing exposure.
4. Monitor whether a strategy's live/paper edge is degrading.
5. Make risk limits non-overridable by agents.
6. Separate research, decisioning, risk, and execution.
7. No live trading until walk-forward and paper validation pass explicit gates.

## Current milestone

**M0: executable research core** — typed domain models, risk firewall, deterministic ensemble decisioning, paper broker, edge monitor, and tests.

Kronos integration is an adapter: the core remains usable with a deterministic mock forecast while the model weights are installed separately.

## License

MIT
