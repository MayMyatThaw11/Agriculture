from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import Alert, Assessment, Field, Notification, utcnow
from app.services.telegram import format_alert_message, send_telegram_message


def create_alert_for_assessment(
    session: Session,
    *,
    field: Field,
    assessment: Assessment,
) -> tuple[Alert | None, Notification | None]:
    """Create one alert after a warning/critical transition.

    A matching risk for the same field within one hour is suppressed. The
    existing in-app alert remains visible while the delivery row records why
    another Telegram message was not sent.
    """
    if assessment.status not in {"warning", "critical"}:
        return None, None

    now = utcnow()
    cooldown_start = now - timedelta(hours=1)
    recent = session.scalar(
        select(Alert)
        .where(
            Alert.field_id == field.id,
            Alert.risk_type == assessment.primary_risk,
            Alert.opened_at >= cooldown_start,
        )
        .order_by(Alert.opened_at.desc())
    )
    fingerprint = f"{field.id}:{assessment.primary_risk}:{assessment.status}"
    if recent:
        suppressed_delivery = Notification(
            alert_id=recent.id,
            channel="telegram",
            destination_ref="cooldown",
            delivery_key=f"{recent.fingerprint}:cooldown:{now.isoformat()}",
            status="suppressed",
            attempt_count=0,
            last_error_code="cooldown_active",
        )
        session.add(suppressed_delivery)
        return recent, suppressed_delivery

    alert = Alert(
        field_id=field.id,
        assessment_id=assessment.id,
        fingerprint=fingerprint,
        severity=assessment.status,
        risk_type=assessment.primary_risk,
        message=assessment.recommendation,
        status="open",
        opened_at=now,
    )
    session.add(alert)
    session.flush()

    delivery_key = f"{fingerprint}:{assessment.id}"
    settings = get_settings()
    delivery = Notification(
        alert_id=alert.id,
        channel="telegram",
        destination_ref=settings.telegram_chat_id or "not-configured",
        delivery_key=delivery_key,
        status="pending",
        attempt_count=1,
    )
    result = send_telegram_message(
        format_alert_message(
            field_name=field.name,
            risk_type=assessment.primary_risk,
            recommendation=assessment.recommendation,
        )
    )
    delivery.status = result.status
    delivery.last_error_code = result.error_code
    if result.status == "sent":
        delivery.sent_at = now
    session.add(delivery)
    return alert, delivery


def acknowledge_alert(session: Session, alert_id: int) -> Alert | None:
    alert = session.get(Alert, alert_id)
    if not alert:
        return None
    alert.status = "acknowledged"
    alert.acknowledged_at = utcnow()
    session.commit()
    session.refresh(alert)
    return alert


def resolve_alert(session: Session, alert_id: int) -> Alert | None:
    alert = session.get(Alert, alert_id)
    if not alert:
        return None
    alert.status = "resolved"
    alert.resolved_at = utcnow()
    session.commit()
    session.refresh(alert)
    return alert
