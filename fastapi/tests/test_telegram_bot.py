from app.services.telegram_bot import _reply_for_update


def test_start_message_gets_online_reply() -> None:
    reply = _reply_for_update(
        {"message": {"chat": {"id": 123}, "text": "/start"}},
        allowed_chat_id="123",
    )

    assert reply == (
        "123",
        "AgroGuard bot is online.\n"
        "Use the dashboard for field data and alerts.\n"
        "Send /help to see this message again.",
    )


def test_messages_from_another_chat_are_ignored() -> None:
    assert _reply_for_update(
        {"message": {"chat": {"id": 456}, "text": "/start"}},
        allowed_chat_id="123",
    ) is None
