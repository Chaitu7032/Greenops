# FinOps Compute Cost Engine

## Formula
Compute spending is computed using exact Decimal arithmetic to eliminate binary floating-point round-off error:

$$\text{Cost (\$) } = \left(\frac{\text{Duration (seconds)}}{60}\right) \times \text{CostPerMinute} + \text{DataTransferCost}$$

## Assumptions
- Standard 2-core Ubuntu runner: \$0.008000 / minute.
- Standard 4-core Linux runner: \$0.016000 / minute.
- Standard 8-core Linux runner: \$0.032000 / minute.
- For MVP estimation, `data_transfer_cost = 0` unless explicitly provided.
