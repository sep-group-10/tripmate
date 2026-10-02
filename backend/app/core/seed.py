import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.core.database import SessionLocal
from app.core.roles import Role
from app.core.security import hash_password
from app.core.seed_tourism import seed_tourism
from app.models.destination import Destination
from app.models.feedback import Feedback
from app.models.transport_rate import TransportRate
from app.models.user import User

DESTINATIONS = [
    {
        "id": uuid.UUID("83f7d353-8731-4663-8e79-1a54d473f6dd"),
        "name": "Kandy",
        "description": (
            "A cultural city in the Central Province, known for the "
            "Temple of the Sacred Tooth Relic, scenic hills, and Kandy Lake."
        ),
        "country": "Sri Lanka",
        "region": "Central Province",
        "latitude": 7.2906,
        "longitude": 80.6337,
        "is_active": True,
    },
    {
        "name": "Colombo",
        "description": (
            "Sri Lanka's commercial capital, offering a mix of modern city life, "
            "colonial architecture, coastal attractions, shopping, and dining."
        ),
        "country": "Sri Lanka",
        "region": "Western Province",
        "latitude": 6.9271,
        "longitude": 79.8612,
        "is_active": True,
    },
    {
        "name": "Galle",
        "description": (
            "A historic coastal city in the Southern Province, famous for "
            "Galle Fort, colonial architecture, beaches, and cultural attractions."
        ),
        "country": "Sri Lanka",
        "region": "Southern Province",
        "latitude": 6.0535,
        "longitude": 80.2210,
        "is_active": True,
    },
]

TRANSPORT_RATES = [
    {
        "transport_type": "bus_budget",
        "region": "Western Province",
        "cost_per_km": Decimal("0.30"),
        "base_fare": Decimal("0.50"),
    },
    {
        "transport_type": "bus_luxury",
        "region": "Western Province",
        "cost_per_km": Decimal("0.50"),
        "base_fare": Decimal("1.00"),
    },
    {
        "transport_type": "train",
        "region": "Western Province",
        "cost_per_km": Decimal("0.20"),
        "base_fare": Decimal("1.00"),
    },
    {
        "transport_type": "tuk_tuk",
        "region": "Western Province",
        "cost_per_km": Decimal("1.00"),
        "base_fare": Decimal("1.50"),
    },
    {
        "transport_type": "car",
        "region": "Western Province",
        "cost_per_km": Decimal("1.50"),
        "base_fare": Decimal("2.00"),
    },
    {
        "transport_type": "van",
        "region": "Western Province",
        "cost_per_km": Decimal("1.80"),
        "base_fare": Decimal("2.50"),
    },
    {
        "transport_type": "bus_budget",
        "region": "Central Province",
        "cost_per_km": Decimal("0.35"),
        "base_fare": Decimal("0.50"),
    },
    {
        "transport_type": "bus_luxury",
        "region": "Central Province",
        "cost_per_km": Decimal("0.55"),
        "base_fare": Decimal("1.00"),
    },
    {
        "transport_type": "train",
        "region": "Central Province",
        "cost_per_km": Decimal("0.22"),
        "base_fare": Decimal("1.00"),
    },
    {
        "transport_type": "tuk_tuk",
        "region": "Central Province",
        "cost_per_km": Decimal("1.10"),
        "base_fare": Decimal("1.50"),
    },
    {
        "transport_type": "car",
        "region": "Central Province",
        "cost_per_km": Decimal("1.60"),
        "base_fare": Decimal("2.00"),
    },
    {
        "transport_type": "van",
        "region": "Central Province",
        "cost_per_km": Decimal("1.90"),
        "base_fare": Decimal("2.50"),
    },
    {
        "transport_type": "bus_budget",
        "region": "Southern Province",
        "cost_per_km": Decimal("0.32"),
        "base_fare": Decimal("0.50"),
    },
    {
        "transport_type": "bus_luxury",
        "region": "Southern Province",
        "cost_per_km": Decimal("0.52"),
        "base_fare": Decimal("1.00"),
    },
    {
        "transport_type": "train",
        "region": "Southern Province",
        "cost_per_km": Decimal("0.21"),
        "base_fare": Decimal("1.00"),
    },
    {
        "transport_type": "tuk_tuk",
        "region": "Southern Province",
        "cost_per_km": Decimal("1.05"),
        "base_fare": Decimal("1.50"),
    },
    {
        "transport_type": "car",
        "region": "Southern Province",
        "cost_per_km": Decimal("1.55"),
        "base_fare": Decimal("2.00"),
    },
    {
        "transport_type": "van",
        "region": "Southern Province",
        "cost_per_km": Decimal("1.85"),
        "base_fare": Decimal("2.50"),
    },
]


DEMO_USERS = [
    {
        "full_name": "Demo Tourist",
        "email": "tourist@demo.com",
        "password": "Demo1234",
        "role": Role.TOURIST.value,
    },
    {
        "full_name": "Demo Admin",
        "email": "admin@demo.com",
        "password": "Demo1234",
        "role": Role.ADMIN.value,
    },
    {
        "full_name": "Demo Super Admin",
        "email": "superadmin@demo.com",
        "password": "Demo1234",
        "role": Role.SUPER_ADMIN.value,
    },
]


DEMO_FEEDBACK = [
    {
        "author_email": "tourist@demo.com",
        "rating": 2,
        "comment": "Good route through the fort, but two of the restaurants suggested were closed on Mondays. Worth checking opening hours.",
        "days_ago": 0,
    },
    {
        "author_email": "tourist@demo.com",
        "rating": 3,
        "comment": "The estimated hotel cost was well under what we actually paid. Would help to show a price range instead of one number.",
        "days_ago": 1,
    },
    {
        "author_email": "tourist@demo.com",
        "rating": 4,
        "comment": "Two leopard sightings in one morning! The early safari slot made all the difference.",
        "days_ago": 5,
    },
    {
        "author_email": "tourist@demo.com",
        "rating": 3,
        "comment": "Jaffna to Delft had us on the ferry in heavy wind. A weather warning for boat trips would be great.",
        "days_ago": 9,
    },
    {
        "author_email": "tourist@demo.com",
        "rating": 1,
        "comment": "The Temple of the Tooth listing had the wrong dress code info. We were turned away at first.",
        "days_ago": 2,
    },
    {
        "author_email": "tourist@demo.com",
        "rating": 5,
        "comment": "The Nine Arch Bridge timing was perfect, we caught the train right as we arrived.",
        "days_ago": 12,
        "resolution_outcome": "No action needed",
        "resolved_by_email": "superadmin@demo.com",
        "resolved_days_ago": 11,
    },
    {
        "author_email": "tourist@demo.com",
        "rating": 2,
        "comment": "Temple of the Tooth dress code info was outdated.",
        "days_ago": 14,
        "resolution_outcome": "Fixed the data",
        "resolution_note": "Updated dress code and added a note about shoulder cover.",
        "resolved_by_email": "admin@demo.com",
        "resolved_days_ago": 13,
    },
    {
        "author_email": "tourist@demo.com",
        "rating": 4,
        "comment": "Whale watching was great. Would like more vegetarian options in the restaurant list.",
        "days_ago": 17,
        "resolution_outcome": "Shared with team",
        "resolution_note": "Sent to content team for restaurant tagging.",
        "resolved_by_email": "admin@demo.com",
        "resolved_days_ago": 16,
    },
    {
        "author_email": "tourist@demo.com",
        "rating": 5,
        "comment": "Sunrise climb suggestion was spot on. Very smooth planning overall.",
        "days_ago": 21,
        "resolution_outcome": "No action needed",
        "resolved_by_email": "superadmin@demo.com",
        "resolved_days_ago": 20,
    },
]


def seed_destinations(db):
    for destination_data in DESTINATIONS:
        existing = (
            db.query(Destination)
            .filter(Destination.name == destination_data["name"])
            .first()
        )

        if existing:
            print(f"Destination {destination_data['name']} already exists. Skipping.")
            continue

        db.add(Destination(**destination_data))

    db.commit()


def seed_transport_rates(db):
    required_types = {rate_data["transport_type"] for rate_data in TRANSPORT_RATES}

    db.query(TransportRate).filter(
        TransportRate.transport_type.notin_(required_types)
    ).delete(synchronize_session=False)

    db.query(TransportRate).filter(TransportRate.region == "General").delete(
        synchronize_session=False
    )

    for rate_data in TRANSPORT_RATES:
        existing = (
            db.query(TransportRate)
            .filter(
                TransportRate.transport_type == rate_data["transport_type"],
                TransportRate.region == rate_data["region"],
            )
            .first()
        )

        if existing:
            print(
                f"Transport rate {rate_data['transport_type']} "
                f"for {rate_data['region']} already exists. Skipping."
            )
            continue

        db.add(TransportRate(**rate_data))

    db.commit()


def seed_demo_users(db):
    for user_data in DEMO_USERS:
        existing = db.query(User).filter(User.email == user_data["email"]).first()

        if existing:
            print(f"User {user_data['email']} already exists. Skipping.")
            continue

        db.add(
            User(
                full_name=user_data["full_name"],
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
                is_active=True,
                is_email_verified=True,
            )
        )

    db.commit()


def seed_demo_feedback(db):
    """Seeds a mix of pending/resolved feedback against the demo tourist
    account, for exercising the admin Feedback page without every
    teammate having to hand-create rows. `days_ago` is resolved relative
    to seed time rather than a fixed date, so it stays plausible however
    long after seeding it's viewed."""
    now = datetime.now(timezone.utc)

    for feedback_data in DEMO_FEEDBACK:
        author = (
            db.query(User).filter(User.email == feedback_data["author_email"]).first()
        )
        if author is None:
            print(
                f"Feedback author {feedback_data['author_email']} not found. Skipping."
            )
            continue

        existing = (
            db.query(Feedback)
            .filter(
                Feedback.user_id == author.id,
                Feedback.comment == feedback_data["comment"],
            )
            .first()
        )
        if existing:
            print(
                f"Feedback '{feedback_data['comment'][:40]}…' already exists. Skipping."
            )
            continue

        resolved_by_email = feedback_data.get("resolved_by_email")
        resolved_by = (
            db.query(User).filter(User.email == resolved_by_email).first()
            if resolved_by_email
            else None
        )

        db.add(
            Feedback(
                user_id=author.id,
                rating=feedback_data["rating"],
                comment=feedback_data["comment"],
                status="resolved" if resolved_by else "pending",
                resolution_outcome=feedback_data.get("resolution_outcome"),
                resolution_note=feedback_data.get("resolution_note"),
                resolved_by=resolved_by.id if resolved_by else None,
                resolved_at=(
                    now - timedelta(days=feedback_data["resolved_days_ago"])
                    if resolved_by
                    else None
                ),
                created_at=now - timedelta(days=feedback_data["days_ago"]),
            )
        )

    db.commit()


def seed_all():
    db = SessionLocal()

    try:
        seed_destinations(db)
        seed_transport_rates(db)
        seed_demo_users(db)
        seed_demo_feedback(db)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    seed_tourism()

    print("Complete database seed finished successfully.")


if __name__ == "__main__":
    seed_all()
