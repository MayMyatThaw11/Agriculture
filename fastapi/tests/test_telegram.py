from unittest.mock import patch

import httpx

from app.services.telegram import format_alert_message, send_telegram_message


def test_alert_message_contains_measured_sensor_value() -> None:
    message = format_alert_message(
        field_name="Demo field",
        risk_type="soil_moisture_below_range",
        recommendation="Irrigate now.",
        health_score=25,
        evidence={
            "factors": [
                {
                    "factor": "soil_moisture",
                    "value": 10,
                    "unit": "%",
                    "range_min": 40,
                    "range_max": 80,
                }
            ]
        },
    )

    assert "Growing-condition estimate: 25.0%" in message
    assert "Measured soil_moisture: 10 %" in message
    assert "safe range 40-80 %" in message


def test_invalid_telegram_response_is_reported() -> None:
    response = httpx.Response(
        404,
        request=httpx.Request("POST", "https://api.telegram.org/botinvalid/sendMessage"),
    )
    with patch("app.services.telegram.get_settings") as get_settings:
        from pydantic import SecretStr

        get_settings.return_value.telegram_bot_token = SecretStr("invalid")
        get_settings.return_value.telegram_chat_id = "123"
        with patch("app.services.telegram.httpx.Client") as client_factory:
            client_factory.return_value.__enter__.return_value.post.side_effect = (
                httpx.HTTPStatusError("not found", request=response.request, response=response)
            )
            result = send_telegram_message("test")

    assert result.status == "failed"
    assert result.error_code == "telegram_http_404"
