import pytest
from decimal import Decimal
from app.services.cost_engine import calculate_compute_cost
from app.services.energy_engine import calculate_energy
from app.services.carbon_engine import calculate_carbon, grams_to_kg
from app.services.duration_estimator import estimate_duration_heuristic
from app.services.diff_analyzer import DiffAnalysisResult


def test_calculate_compute_cost_standard():
    # 12 minutes (720 seconds) at $0.008/min = $0.096
    cost = calculate_compute_cost(duration_seconds=720, cost_per_minute=Decimal("0.008000"))
    assert cost == Decimal("0.096000")


def test_calculate_compute_cost_zero_and_edge_cases():
    assert calculate_compute_cost(0) == Decimal("0.000000")
    assert calculate_compute_cost(60, Decimal("0.010000"), Decimal("0.005000")) == Decimal("0.015000")

    with pytest.raises(ValueError):
        calculate_compute_cost(-10)

    with pytest.raises(ValueError):
        calculate_compute_cost(60, cost_per_minute=-0.01)


def test_calculate_energy_standard():
    # Formula: [(10 + (50-10)*0.70) * (3600/3600) * 1.15] / 1000
    # Power = 10 + 28 = 38W. Energy = 38 * 1 * 1.15 / 1000 = 0.043700 kWh
    energy = calculate_energy(
        duration_seconds=3600,
        power_idle_watts=Decimal("10.00"),
        power_max_watts=Decimal("50.00"),
        cpu_utilization=Decimal("0.70"),
        pue=Decimal("1.150"),
    )
    assert energy == Decimal("0.043700")


def test_calculate_energy_bounds_and_validations():
    assert calculate_energy(0) == Decimal("0.000000")

    with pytest.raises(ValueError):
        calculate_energy(100, cpu_utilization=-0.1)

    with pytest.raises(ValueError):
        calculate_energy(100, cpu_utilization=1.2)

    with pytest.raises(ValueError):
        calculate_energy(100, pue=0.9)

    with pytest.raises(ValueError):
        calculate_energy(100, power_idle_watts=50, power_max_watts=10)


def test_calculate_carbon_standard():
    # 0.05 kWh * 300 gCO2e/kWh = 15.0 gCO2e
    carbon = calculate_carbon(energy_kwh=Decimal("0.050000"), grid_intensity_gco2_kwh=Decimal("300.00"))
    assert carbon == Decimal("15.0000")
    assert grams_to_kg(carbon) == Decimal("0.0150")


def test_calculate_carbon_zero_and_negative():
    assert calculate_carbon(0, Decimal("350.00")) == Decimal("0.0000")
    assert calculate_carbon(Decimal("0.05"), 0) == Decimal("0.0000")

    with pytest.raises(ValueError):
        calculate_carbon(-1, 300)

    with pytest.raises(ValueError):
        calculate_carbon(1, -50)


def test_duration_estimator_heuristic():
    diff_doc_only = DiffAnalysisResult(
        changed_files_count=2,
        lines_added=10,
        lines_deleted=2,
        source_files_count=0,
        test_files_count=0,
        documentation_files_count=2,
        configuration_files_count=0,
        integration_files_count=0,
        raw_files=["README.md", "docs/architecture.md"],
    )
    est_doc = estimate_duration_heuristic(diff_doc_only)
    assert est_doc <= Decimal("30.00")

    diff_mixed = DiffAnalysisResult(
        changed_files_count=5,
        lines_added=200,
        lines_deleted=50,
        source_files_count=3,
        test_files_count=2,
        documentation_files_count=0,
        configuration_files_count=0,
        integration_files_count=0,
        raw_files=[],
    )
    # 60 + (3*12) + (2*20) + (250 * 0.05) = 60 + 36 + 40 + 12.5 = 148.5
    est_mixed = estimate_duration_heuristic(diff_mixed)
    assert est_mixed == Decimal("148.50")
