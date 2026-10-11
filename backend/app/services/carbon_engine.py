from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Union


def calculate_carbon(
    energy_kwh: Union[int, float, Decimal],
    grid_intensity_gco2_kwh: Union[int, float, Decimal],
) -> Decimal:
    """
    Calculate estimated Scope-2 CO2 equivalent emissions in grams (gCO2e).
    Formula:
        CO2e_grams = Energy_kWh * Grid_Carbon_Intensity_gCO2e_per_kWh
    """
    e_kwh = Decimal(str(energy_kwh))
    intensity = Decimal(str(grid_intensity_gco2_kwh))

    if e_kwh < 0:
        raise ValueError("energy_kwh cannot be negative")
    if intensity < 0:
        raise ValueError("grid_intensity_gco2_kwh cannot be negative")

    if e_kwh == 0 or intensity == 0:
        return Decimal("0.0000")

    carbon_g = e_kwh * intensity
    return carbon_g.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def grams_to_kg(carbon_g: Union[int, float, Decimal]) -> Decimal:
    """Convert grams of CO2e to kilograms of CO2e."""
    c_g = Decimal(str(carbon_g))
    if c_g < 0:
        raise ValueError("carbon_g cannot be negative")
    return (c_g / Decimal("1000")).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
