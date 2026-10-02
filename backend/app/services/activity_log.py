from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog


def log_activity(db: Session, kind: str, title: str, meta: str | None = None):
    """Record one row for the dashboard's Recent Activity feed. Call this
    right after the triggering change is committed, with its own add +
    commit - a logging failure must never roll back the caller's change,
    so this is deliberately a separate transaction."""
    entry = ActivityLog(kind=kind, title=title, meta=meta)
    db.add(entry)
    db.commit()
