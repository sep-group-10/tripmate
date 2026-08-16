from app.core.database import SessionLocal
from app.models.destination import Destination


DESTINATIONS = [
    {
        "name": "Kandy",
        "description": (
            "A cultural city in the Central Province, known for the "
            "Temple of the Sacred Tooth Relic, scenic hills, and Kandy Lake."
        ),
        "country": "Sri Lanka",
        "region": "Central Province",
        "coordinates": {
            "latitude": 7.2906,
            "longitude": 80.6337,
        },
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
        "coordinates": {
            "latitude": 6.9271,
            "longitude": 79.8612,
        },
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
        "coordinates": {
            "latitude": 6.0535,
            "longitude": 80.2210,
        },
        "is_active": True,
    },
]


def seed_destinations():
    db = SessionLocal()

    try:
        for destination_data in DESTINATIONS:
            existing = (
                db.query(Destination)
                .filter(Destination.name == destination_data["name"])
                .first()
            )

            if existing:
                print(f"{destination_data['name']} already exists. Skipping.")
                continue

            destination = Destination(**destination_data)
            db.add(destination)

        db.commit()
        print("Destination seeding completed successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_destinations()
