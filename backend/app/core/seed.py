from decimal import Decimal

import bcrypt

from app.core.database import SessionLocal
from app.core.seed_tourism import seed_tourism
from app.models.destination import Destination
from app.models.transport_rate import TransportRate
from app.models.user import User

DESTINATIONS = [
    {
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
        "transport_type": "Taxi",
        "cost_per_km": Decimal("1.50"),
        "base_fare": Decimal("2.00"),
    },
    {
        "transport_type": "Bus",
        "cost_per_km": Decimal("0.30"),
        "base_fare": Decimal("0.50"),
    },
    {
        "transport_type": "Tuk-tuk",
        "cost_per_km": Decimal("1.00"),
        "base_fare": Decimal("1.50"),
    },
    {
        "transport_type": "Train",
        "cost_per_km": Decimal("0.20"),
        "base_fare": Decimal("1.00"),
    },
]


DEMO_USERS = [
    {
        "full_name": "Demo Tourist",
        "email": "tourist@demo.com",
        "password": "Demo1234",
        "role": "tourist",
    },
    {
        "full_name": "Demo Admin",
        "email": "admin@demo.com",
        "password": "Demo1234",
        "role": "admin",
    },
    {
        "full_name": "Demo Super Admin",
        "email": "superadmin@demo.com",
        "password": "Demo1234",
        "role": "super_admin",
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
            print(
                f"Destination {destination_data['name']} already exists. "
                "Skipping."
            )
            continue

        db.add(Destination(**destination_data))

    db.commit()


def seed_transport_rates(db):
    for rate_data in TRANSPORT_RATES:
        existing = (
            db.query(TransportRate)
            .filter(
                TransportRate.transport_type
                == rate_data["transport_type"]
            )
            .first()
        )

        if existing:
            print(
                f"Transport rate {rate_data['transport_type']} "
                "already exists. Skipping."
            )
            continue

        db.add(TransportRate(**rate_data))

    db.commit()


def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def seed_demo_users(db):
    for user_data in DEMO_USERS:
        existing = (
            db.query(User)
            .filter(User.email == user_data["email"])
            .first()
        )

        if existing:
            print(
                f"User {user_data['email']} already exists. Skipping."
            )
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


def seed_all():
    db = SessionLocal()

    try:
        seed_destinations(db)
        seed_transport_rates(db)
        seed_demo_users(db)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    seed_tourism()

    print("Complete database seed finished successfully.")


if __name__ == "__main__":
    seed_all()