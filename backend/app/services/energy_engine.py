from decimal import Decimal, ROUND_HALF_UP
from typing import Union


def calculate_energy(
    duration_seconds: Union[int, float, Decimal],
    power_idle_watts: Union[float, Decimal] = Decimal("10.00"),
    power_max_watts: Union[float, Decimal] = Decimal("50.00"),
    cpu_utilization: Union[float, Decimal] = Decimal("0.70"),
    pue: Union[float, Decimal] = Decimal("1.150"),
) -> Decimal:
    """
    Calculate energy consumption in kWh based on cloud server power profile and PUE.
    Formula:
        Run_Hours = duration_seconds / 3600
        Power_Watts = P_idle + (P_max - P_idle) * CPU_Utilization
        Energy_kWh = (Power_Watts * Run_Hours * PUE) / 1000
    """
    dur = Decimal(str(duration_seconds))
    p_idle = Decimal(str(power_idle_watts))
    p_max = Decimal(str(power_max_watts))
    util = Decimal(str(cpu_utilization))
    pue_val = Decimal(str(pue))

    # Validations
    if dur < 0:
        raise ValueError("duration_seconds cannot be negative")
    if p_idle < 0 or p_max < 0:
        raise ValueError("Power values cannot be negative")
    if p_max < p_idle:
        raise ValueError("power_max_watts cannot be less than power_idle_watts")
    if util < 0 or util > 1:
        raise ValueError("cpu_utilization must be between 0.0 and 1.0")
    if pue_val < Decimal("1.0"):
        raise ValueError("PUE must be greater than or equal to 1.0")

    if dur == 0:
        return Decimal("0.000000")

    run_hours = dur / Decimal("3600")
    power_watts = p_idle + ((p_max - p_idle) * util)
    energy_kwh = (power_watts * run_hours * pue_val) / Decimal("1000")

    return energy_kwh.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
