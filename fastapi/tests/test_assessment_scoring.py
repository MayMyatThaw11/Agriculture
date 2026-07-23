from types import SimpleNamespace

from app.services.assessment import run_assessment


def _requirements():
    return [
        SimpleNamespace(
            factor="soil_moisture",
            min_value=40,
            max_value=80,
            unit="%",
            criticality="important",
        ),
        SimpleNamespace(
            factor="ph",
            min_value=5.5,
            max_value=7.5,
            unit="pH",
            criticality="critical",
        ),
    ]


def test_severe_soil_moisture_is_unhealthy() -> None:
    result = run_assessment(
        SimpleNamespace(soil_moisture=10, ph=6.5),
        None,
        _requirements(),
    )

    assert result["health_score"] < 50
    assert result["status"] == "critical"
    assert result["primary_risk"] == "soil_moisture_below_range"


def test_severe_ph_is_unhealthy() -> None:
    result = run_assessment(
        SimpleNamespace(soil_moisture=60, ph=4),
        None,
        _requirements(),
    )

    assert result["health_score"] < 50
    assert result["status"] == "critical"
    assert result["primary_risk"] == "ph_below_range"


def test_any_out_of_range_moisture_or_ph_is_below_fifty() -> None:
    dry_result = run_assessment(
        SimpleNamespace(soil_moisture=35, ph=6.5),
        None,
        _requirements(),
    )
    acidic_result = run_assessment(
        SimpleNamespace(soil_moisture=60, ph=5.4),
        None,
        _requirements(),
    )

    assert dry_result["health_score"] < 50
    assert acidic_result["health_score"] < 50


def test_condition_score_has_a_nonzero_floor() -> None:
    result = run_assessment(
        SimpleNamespace(soil_moisture=0, ph=3),
        None,
        _requirements(),
    )

    assert result["health_score"] == 5.0
