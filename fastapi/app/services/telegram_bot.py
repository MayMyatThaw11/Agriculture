import asyncio
import logging
import ssl
from collections.abc import Mapping

import httpx
import truststore

from app.core.config import get_settings

logger = logging.getLogger(__name__)
_POLL_TIMEOUT_SECONDS = 25
_RETRY_DELAY_SECONDS = 5


def _reply_for_update(update: Mapping, allowed_chat_id: str | None) -> tuple[str, str] | None:
    message = update.get("message")
    if not isinstance(message, Mapping):
        return None

    chat = message.get("chat")
    if not isinstance(chat, Mapping) or "id" not in chat:
        return None

    chat_id = str(chat["id"])
    if allowed_chat_id and chat_id != allowed_chat_id:
        return None

    text = message.get("text")
    if not isinstance(text, str):
        return None

    command = text.strip().split(maxsplit=1)[0].lower()
    if command in {"/start", "/help"}:
        return (
            chat_id,
            "AgroGuard bot is online.\n"
            "Use the dashboard for field data and alerts.\n"
            "Send /help to see this message again.",
        )

    return (
        chat_id,
        "AgroGuard received your message. Use /help for bot instructions.",
    )


async def _telegram_request(
    client: httpx.AsyncClient,
    token: str,
    method: str,
    payload: Mapping | None = None,
) -> dict:
    response = await client.post(
        f"https://api.telegram.org/bot{token}/{method}",
        json=payload or {},
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error for {method}: {data.get('error_code')}")
    return data


async def run_telegram_polling() -> None:
    settings = get_settings()
    token = settings.telegram_bot_token.get_secret_value() if settings.telegram_bot_token else None
    if not token:
        logger.warning("Telegram polling enabled but no bot token is configured")
        return

    offset: int | None = None
    timeout = httpx.Timeout(_POLL_TIMEOUT_SECONDS + 5)
    async with httpx.AsyncClient(
        verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT),
        timeout=timeout,
    ) as client:
        try:
            await _telegram_request(client, token, "deleteWebhook", {"drop_pending_updates": False})
            if settings.telegram_chat_id:
                await _telegram_request(
                    client,
                    token,
                    "sendMessage",
                    {
                        "chat_id": settings.telegram_chat_id,
                        "text": "AgroGuard bot started and is ready for /start or /help.",
                    },
                )
        except (httpx.HTTPError, RuntimeError) as exc:
            logger.error(
                "Telegram polling could not initialize or send its startup alert: %s. "
                "Check AGROGUARD_TELEGRAM_BOT_TOKEN and AGROGUARD_TELEGRAM_CHAT_ID.",
                exc,
            )
            return

        while True:
            try:
                payload: dict[str, int] = {"timeout": _POLL_TIMEOUT_SECONDS}
                if offset is not None:
                    payload["offset"] = offset
                data = await _telegram_request(client, token, "getUpdates", payload)
                for update in data.get("result", []):
                    update_id = update.get("update_id")
                    if isinstance(update_id, int):
                        offset = update_id + 1
                    reply = _reply_for_update(update, settings.telegram_chat_id)
                    if reply:
                        chat_id, text = reply
                        await _telegram_request(
                            client,
                            token,
                            "sendMessage",
                            {"chat_id": chat_id, "text": text},
                        )
            except asyncio.CancelledError:
                raise
            except (httpx.HTTPError, RuntimeError, ValueError) as exc:
                logger.error("Telegram polling failed: %s", exc)
                await asyncio.sleep(_RETRY_DELAY_SECONDS)
