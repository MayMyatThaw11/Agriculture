import logging
import ssl
from dataclasses import dataclass

import httpx
import truststore

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TelegramResult:
    status: str
    error_code: str | None = None


def format_alert_message(
    *,
    field_name: str,
    risk_type: str,
    recommendation: str,
    health_score: float | None = None,
    evidence: dict | None = None,
) -> str:
    measured = ""
    if evidence:
        factor = next(
            (
                item
                for item in evidence.get("factors", [])
                if risk_type.startswith(f"{item.get('factor')}_")
            ),
            None,
        )
        if factor:
            measured = (
                f"\nMeasured {factor['factor']}: {factor['value']} {factor['unit']}"
                f" (safe range {factor['range_min']}-{factor['range_max']} {factor['unit']})"
            )
    score_line = (
        f"\nGrowing-condition estimate: {health_score:.1f}%"
        if health_score is not None
        else ""
    )
    return (
        f"AgroGuard alert\nField: {field_name}\n"
        f"Risk: {risk_type}{score_line}{measured}\n"
        f"Recommended action: {recommendation}"
    )


def send_telegram_message(message: str) -> TelegramResult:
    settings = get_settings()
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return TelegramResult(status="suppressed", error_code="telegram_not_configured")

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token.get_secret_value()}/sendMessage"
    try:
        # Use the OS certificate store so corporate/network TLS certificates trusted
        # by Windows are honored without weakening HTTPS verification.
        with httpx.Client(
            verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT),
            timeout=5.0,
        ) as client:
            response = client.post(
                url,
                json={"chat_id": settings.telegram_chat_id, "text": message},
            )
        response.raise_for_status()
        return TelegramResult(status="sent")
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Telegram sendMessage rejected the request: HTTP %s",
            exc.response.status_code,
        )
        return TelegramResult(
            status="failed",
            error_code=f"telegram_http_{exc.response.status_code}",
        )
    except (httpx.HTTPError, ValueError) as exc:
        logger.error("Telegram sendMessage failed: %s", exc)
        return TelegramResult(status="failed", error_code="telegram_delivery_failed")
