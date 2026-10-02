import math
import uuid
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import extract, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.errors import ApiError, ErrorCode
from app.core.roles import Role
from app.core.security import generate_admin_invite_token
from app.models.activity_log import ActivityLog
from app.models.destination import Destination
from app.models.feedback import Feedback
from app.models.trip import Trip
from app.models.user import User
from app.routers.auth import _frontend_base_url
from app.schemas.admin import (
    ActivityEntry,
    AdminCreateData,
    AdminCreateRequest,
    AdminStats,
    AdminStatusUpdate,
    FeedbackResponse,
    FeedbackStatusUpdate,
    MonthPoint,
    TripsGrowthData,
    UserListData,
    UserListResponse,
)
from app.schemas.common import ApiResponse
from app.services.activity_log import log_activity
from app.services.email import send_email
from app.services.email_templates import admin_invite_email


def _add_months(base: date, months: int) -> date:
    """Shift `base` (always day-of-month 1) by `months`, without pulling in
    a dateutil dependency for this single calculation."""
    total = base.month - 1 + months
    year = base.year + total // 12
    month = total % 12 + 1
    return date(year, month, 1)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_role(Role.ADMIN))],
)


@router.get("/stats", response_model=ApiResponse[AdminStats])
def get_admin_stats(db: Session = Depends(get_db)):
    """Counts backing the dashboard KPI row. Each is a direct count against
    its own table - no derived/estimated numbers."""
    return ApiResponse(
        data=AdminStats(
            total_users=db.query(User).count(),
            pending_feedback_count=db.query(Feedback)
            .filter(Feedback.status == "pending")
            .count(),
            draft_trips_count=db.query(Trip).filter(Trip.status == "draft").count(),
            destinations_count=db.query(Destination)
            .filter(Destination.is_active.is_(True))
            .count(),
        )
    )


@router.get("/trips-growth", response_model=ApiResponse[TripsGrowthData])
def get_trips_growth(db: Session = Depends(get_db)):
    """Monthly trip-creation and user-registration counts for the last 12
    months (oldest first), for the dashboard's trend chart."""
    today = datetime.now(timezone.utc).date()
    # First day of the current month, then 11 months back - so the window
    # is exactly the last 12 calendar months including this one.
    window_start = _add_months(date(today.year, today.month, 1), -11)

    def _monthly_counts(model, column):
        rows = (
            db.query(
                extract("year", column).label("year"),
                extract("month", column).label("month"),
                func.count(model.id).label("count"),
            )
            .filter(column >= window_start)
            .group_by("year", "month")
            .all()
        )
        return {(int(row.year), int(row.month)): row.count for row in rows}

    trips_by_month = _monthly_counts(Trip, Trip.created_at)
    users_by_month = _monthly_counts(User, User.created_at)

    months = []
    for offset in range(12):
        month_date = _add_months(window_start, offset)
        key = (month_date.year, month_date.month)
        months.append(
            MonthPoint(
                label=month_date.strftime("%b"),
                trips=trips_by_month.get(key, 0),
                users=users_by_month.get(key, 0),
            )
        )

    return ApiResponse(data=TripsGrowthData(months=months))


@router.get("/activity", response_model=ApiResponse[list[ActivityEntry]])
def list_recent_activity(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Most recent rows from the activity log, for the dashboard's Recent
    Activity feed. Rows are written by log_activity() from the various
    create/update/delete endpoints across the app."""
    entries = (
        db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit).all()
    )
    return ApiResponse(data=entries)


@router.get("/users", response_model=UserListResponse)
def list_admin_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=50),
    status_filter: str | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Paginated user list for the Admins page and the dashboard's
    "Total users" KPI. `status` is either "active" or "suspended" -
    the User model only has is_active, there is no separate "pending"
    account state."""
    query = db.query(User)

    if status_filter == "active":
        query = query.filter(User.is_active.is_(True))
    elif status_filter == "suspended":
        query = query.filter(User.is_active.is_(False))

    if q:
        like = f"%{q}%"
        query = query.filter(User.full_name.ilike(like) | User.email.ilike(like))

    total = query.count()
    total_pages = math.ceil(total / limit) if total else 0

    users = (
        query.order_by(User.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "success": True,
        "data": UserListData(
            items=users,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        ),
    }


@router.get("/feedback", response_model=ApiResponse[list[FeedbackResponse]])
def list_admin_feedback(
    status_filter: str | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Feedback list for the Feedback admin page. Joined against User for
    the reviewer's display name - Feedback itself has no destination link,
    so that field is intentionally absent from the response."""
    query = db.query(Feedback, User.full_name).join(User, Feedback.user_id == User.id)

    if status_filter:
        query = query.filter(Feedback.status == status_filter)

    if q:
        like = f"%{q}%"
        query = query.filter(User.full_name.ilike(like) | Feedback.comment.ilike(like))

    rows = query.order_by(Feedback.created_at.desc()).all()

    return ApiResponse(
        data=[
            FeedbackResponse(
                id=feedback.id,
                user_id=feedback.user_id,
                user_name=full_name,
                rating=feedback.rating,
                comment=feedback.comment,
                status=feedback.status,
                created_at=feedback.created_at,
            )
            for feedback, full_name in rows
        ]
    )


@router.patch("/feedback/{feedback_id}", response_model=ApiResponse[FeedbackResponse])
def update_feedback_status(
    feedback_id: uuid.UUID,
    payload: FeedbackStatusUpdate,
    db: Session = Depends(get_db),
):
    feedback = (
        db.query(Feedback, User.full_name)
        .join(User, Feedback.user_id == User.id)
        .filter(Feedback.id == feedback_id)
        .first()
    )
    if feedback is None:
        raise ApiError(ErrorCode.NOT_FOUND, "Feedback not found")

    entry, full_name = feedback
    entry.status = payload.status
    db.add(entry)
    db.commit()
    db.refresh(entry)

    log_activity(
        db,
        "Feedback",
        f"Feedback marked {entry.status}",
        f"{full_name} · {entry.rating} stars",
    )

    return ApiResponse(
        data=FeedbackResponse(
            id=entry.id,
            user_id=entry.user_id,
            user_name=full_name,
            rating=entry.rating,
            comment=entry.comment,
            status=entry.status,
            created_at=entry.created_at,
        )
    )


@router.get(
    "/admins",
    response_model=UserListResponse,
    dependencies=[Depends(require_role(Role.SUPER_ADMIN))],
)
def list_admins(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=50),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Paginated list of admin/super-admin accounts, for the super
    admin's "Manage admins" page. Super-admin-only."""
    query = db.query(User).filter(
        User.role.in_([Role.ADMIN.value, Role.SUPER_ADMIN.value])
    )

    if q:
        like = f"%{q}%"
        query = query.filter(User.full_name.ilike(like) | User.email.ilike(like))

    total = query.count()
    total_pages = math.ceil(total / limit) if total else 0

    admins = (
        query.order_by(User.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "success": True,
        "data": UserListData(
            items=admins,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        ),
    }


@router.post(
    "/admins",
    response_model=ApiResponse[AdminCreateData],
    status_code=201,
    dependencies=[Depends(require_role(Role.SUPER_ADMIN))],
)
def create_admin(
    payload: AdminCreateRequest,
    db: Session = Depends(get_db),
):
    """Create a new ADMIN account with no password set. The system has
    exactly one super admin, so this never creates one. Emails the new
    admin an invite link to set their password through the existing
    reset-password flow. Super-admin-only."""
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user is not None:
        raise ApiError(ErrorCode.EMAIL_ALREADY_EXISTS, "Email is already registered")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        role=Role.ADMIN.value,
        is_active=True,
        is_email_verified=True,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ApiError(
            ErrorCode.EMAIL_ALREADY_EXISTS, "Email is already registered"
        ) from exc
    db.refresh(user)

    token, expires_at = generate_admin_invite_token()
    user.password_reset_token = token
    user.reset_token_expiry = expires_at
    db.add(user)
    db.commit()

    link = f"{_frontend_base_url()}/reset-password?token={token}"
    subject, body = admin_invite_email(link)
    send_email(user.email, subject, body)

    log_activity(db, "Admin", f"{user.full_name} added as {user.role}", user.email)

    return ApiResponse(
        data=AdminCreateData(
            email=user.email,
            message="Admin account created. An invite email has been sent.",
        )
    )


@router.patch(
    "/admins/{admin_id}/status",
    response_model=ApiResponse[dict],
    dependencies=[Depends(require_role(Role.SUPER_ADMIN))],
)
def update_admin_status(
    admin_id: uuid.UUID,
    payload: AdminStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Activate or deactivate an admin account. A super admin cannot act
    on their own account (lockout risk) or on another super admin's -
    only ADMIN-role accounts can be deactivated this way."""
    target = (
        db.query(User)
        .filter(
            User.id == admin_id,
            User.role.in_([Role.ADMIN.value, Role.SUPER_ADMIN.value]),
        )
        .first()
    )
    if target is None:
        raise ApiError(ErrorCode.NOT_FOUND, "Admin not found")

    if target.id == current_user.id:
        raise ApiError(
            ErrorCode.FORBIDDEN, "You cannot change your own account's status"
        )
    if target.role == Role.SUPER_ADMIN.value:
        raise ApiError(
            ErrorCode.FORBIDDEN, "Super admin accounts cannot be changed this way"
        )

    target.is_active = payload.is_active
    db.add(target)
    db.commit()

    action = "activated" if payload.is_active else "deactivated"
    log_activity(db, "Admin", f"{target.full_name} {action}", target.email)

    return ApiResponse(data={})
