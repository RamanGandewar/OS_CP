from datetime import datetime


def require_fields(payload, fields):
    missing = [field for field in fields if payload.get(field) in (None, "")]
    return missing


def parse_date(value, field_name):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date(), None
    except (TypeError, ValueError):
        return None, f"{field_name} must be in YYYY-MM-DD format"
