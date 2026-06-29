from datetime import datetime, timedelta, timezone


def active_dates() -> dict[str, str]:
    now = datetime.now(timezone.utc)
    return {
        "fecha_inicio": (now - timedelta(days=1)).isoformat(),
        "fecha_fin": (now + timedelta(days=1)).isoformat(),
    }
