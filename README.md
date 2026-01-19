
# MA Trend-Following Research Testbed

This repository implements a controlled moving-average (MA) trend-following strategy,
with the goal of studying **robustness, execution frictions, and risk control mechanisms**
rather than maximizing raw alpha.

## Project Motivation
Instead of optimizing signal complexity, this project fixes a simple MA signal
and focuses on understanding:
- Parameter stability
- Regime dependence
- Execution delay and transaction cost sensitivity
- Risk control effectiveness
- Capacity and scalability limits
- Out-of-sample robustness

## Experiment Structure

- **Exp01**: Signal stability and robustness
- **Exp02**: Risk Control via Volatility Targeting
- **Exp03**: Risk Control via Risk-off Gate
- **Exp04**: Volatility Targeting and Risk-off Gate
- **Exp05**: Execution Frictions
- **Exp06**: Execution Delays
- **Exp07**: Capacity / liquidity proxy stress test
- **Exp08**: Out-of-sample validation

## Key Takeaway
The core takeaway is not whether the MA strategy is profitable,
but **how a simple signal behaves under realistic constraints and where it fails**.


## Research Report

A structured quantitative research report describing the experimental design,
distributional perspective, and key findings is available in [report.md].
