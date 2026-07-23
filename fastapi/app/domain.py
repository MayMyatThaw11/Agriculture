from typing import Any


def assess(values: dict[str, float], requirements: list[dict[str, Any]]) -> dict[str, Any]:
    evidence = []
    total_weight = 0.0
    weighted_score = 0.0
    outside: list[tuple[str, float, float]] = []

    for req in requirements:
        factor = req["factor"]
        if factor not in values:
            continue
        minimum = float(req["min_value"])
        maximum = float(req["max_value"])
        value = float(values[factor])
        weight = float(req.get("weight", 1))
        in_range = minimum <= value <= maximum
        if in_range:
            factor_score = 100.0
        elif value < minimum:
            factor_score = max(0.0, 100 - ((minimum - value) / max(minimum, 1)) * 100)
            outside.append((req.get("label", factor), value, minimum - value))
        else:
            factor_score = max(0.0, 100 - ((value - maximum) / max(maximum, 1)) * 100)
            outside.append((req.get("label", factor), value, value - maximum))
        total_weight += weight
        weighted_score += factor_score * weight
        evidence.append({
            "factor": req.get("label", factor),
            "observed_value": round(value, 2),
            "minimum": minimum,
            "maximum": maximum,
            "unit": req.get("unit", ""),
            "in_range": in_range,
        })

    score = round(weighted_score / total_weight) if total_weight else 0
    risk = "none"
    recommendation = "Conditions are within the crop profile. Continue routine monitoring."

    if outside:
        risk = sorted(outside, key=lambda item: item[2], reverse=True)[0][0]
        action_map = {
            "soil moisture": "Irrigate gradually and recheck soil moisture before next reading.",
            "temperature": "Increase shade and irrigation checks during the hottest period.",
            "soil pH": "Confirm the estimate with a soil test before changing soil inputs.",
            "humidity": "Improve airflow and inspect leaves for fungal symptoms.",
            "light": "Check shading or canopy exposure and avoid abrupt changes.",
            "rainfall": "Adjust drainage or irrigation planning to the recent rainfall pattern.",
        }
        recommendation = action_map.get(
            risk, "Review field conditions and take next action."
        )

    critical = (
        values.get("soil_moisture", 100) < 20
        or values.get("temperature", 0) > 40
        or values.get("ph", 6.5) < 4.5
        or values.get("ph", 6.5) > 9.0
    )
    status = "critical" if critical else "warning" if outside else "healthy"
    if status == "critical":
        score = min(score, 45)
    elif status == "warning":
        score = min(score, 79)

    return {
        "status": status,
        "health_score": max(0, min(100, score)),
        "primary_risk": risk if risk != "none" else None,
        "recommendation": recommendation,
        "evidence": evidence,
        "confidence": "medium" if outside else "high",
    }
