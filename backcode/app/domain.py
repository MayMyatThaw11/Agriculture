from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FactorRule:
    minimum: float
    maximum: float
    unit: str
    weight: float
    label: str


DEFAULT_RULES: dict[str, FactorRule] = {
    "temperature_c": FactorRule(20, 35, "°C", 1.2, "temperature"),
    "humidity_percent": FactorRule(50, 90, "%", 0.8, "humidity"),
    "soil_moisture_percent": FactorRule(45, 85, "%", 1.5, "soil moisture"),
    "soil_ph": FactorRule(5.5, 7.5, "pH", 1.2, "soil pH"),
    "light_percent": FactorRule(40, 90, "%", 0.7, "light"),
    "rainfall_mm": FactorRule(100, 300, "mm / 7 days", 0.7, "rainfall"),
}


def assess(values: dict[str, float], rules: dict[str, Any] | None = None) -> dict[str, Any]:
    configured = rules or {key: vars(rule) for key, rule in DEFAULT_RULES.items()}
    evidence = []
    total_weight = 0.0
    weighted_score = 0.0
    outside: list[tuple[str, float, float]] = []

    for factor, rule in configured.items():
        if factor not in values:
            continue
        minimum = float(rule["minimum"])
        maximum = float(rule["maximum"])
        value = float(values[factor])
        weight = float(rule.get("weight", 1))
        in_range = minimum <= value <= maximum
        if in_range:
            factor_score = 100.0
        elif value < minimum:
            factor_score = max(0.0, 100 - ((minimum - value) / max(minimum, 1)) * 100)
            outside.append((rule.get("label", factor), value, minimum - value))
        else:
            factor_score = max(0.0, 100 - ((value - maximum) / max(maximum, 1)) * 100)
            outside.append((rule.get("label", factor), value, value - maximum))
        total_weight += weight
        weighted_score += factor_score * weight
        evidence.append(
            {
                "factor": rule.get("label", factor),
                "observed_value": round(value, 2),
                "minimum": minimum,
                "maximum": maximum,
                "unit": rule.get("unit", ""),
                "in_range": in_range,
                "source": values.get(f"{factor}_source", "simulated reading"),
            }
        )

    score = round(weighted_score / total_weight) if total_weight else 0
    risk = "none"
    recommendation = "Conditions are within the demo crop profile. Continue routine monitoring."
    if outside:
        risk = sorted(outside, key=lambda item: item[2], reverse=True)[0][0]
        action = {
            "soil moisture": "Irrigate gradually and recheck soil moisture before the next reading.",
            "temperature": "Increase shade and irrigation checks during the hottest period.",
            "soil pH": "Confirm the estimate with a soil test before changing soil inputs.",
            "humidity": "Improve airflow and inspect leaves for fungal symptoms.",
            "light": "Check shading or canopy exposure and avoid abrupt changes.",
            "rainfall": "Adjust drainage or irrigation planning to the recent rainfall pattern.",
        }.get(risk, "Review the field conditions and take the next agronomic action.")
        recommendation = action

    critical = (
        values.get("soil_moisture_percent", 100) < 20
        or values.get("temperature_c", 0) > 40
        or values.get("soil_ph", 6.5) < 4.5
        or values.get("soil_ph", 6.5) > 9.0
    )
    status = "critical" if critical else "warning" if outside else "healthy"
    if status == "critical":
        score = min(score, 45)
    elif status == "warning":
        score = min(score, 79)

    return {
        "status": status,
        "health_score": max(0, min(100, score)),
        "primary_risk": risk,
        "recommendation": recommendation,
        "evidence": evidence,
        "confidence": "medium" if outside else "high",
    }
