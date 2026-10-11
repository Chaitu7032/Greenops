from decimal import Decimal, ROUND_HALF_UP
from typing import Union


def calculate_compute_cost(
    duration_seconds: Union[int, float, Decimal],
    cost_per_minute: Union[float, Decimal] = Decimal("0.008000"),
    data_transfer_cost: Union[float, Decimal] = Decimal("0.000000"),
) -> Decimal:
    """
    Calculate compute cost in USD using high-precision Decimal arithmetic.
    Formula:
        Duration_Minutes = Duration_Seconds / 60
        Cost = (Duration_Minutes * Cost_Per_Minute) + Data_Transfer_Cost
    """
    dur_sec = Decimal(str(duration_seconds))
    rate_min = Decimal(str(cost_per_minute))
    transfer = Decimal(str(data_transfer_cost))

    if dur_sec < 0:
        raise ValueError("duration_seconds cannot be negative")
    if rate_min < 0:
        raise ValueError("cost_per_minute cannot be negative")
    if transfer < 0:
        raise ValueError("data_transfer_cost cannot be negative")

    if dur_sec == 0:
        return transfer.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

    duration_minutes = dur_sec / Decimal("60")
    total_cost = (duration_minutes * rate_min) + transfer

    return total_cost.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
