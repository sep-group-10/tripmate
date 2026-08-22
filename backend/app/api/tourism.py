import math
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.attraction import Attraction
from app.models.destination import Destination
from app.models.hotel import Hotel
from app.models.local_event import LocalEvent
from app.models.restaurant import Restaurant
from app.schemas.tourism import (
    AttractionCreate,
    AttractionResponse,
    AttractionUpdate,
    DestinationCreate,
    DestinationListData,
    DestinationListResponse,
    DestinationResponse,
    DestinationUpdate,
    HotelCreate,
    HotelResponse,
    HotelUpdate,
    LocalEventCreate,
    LocalEventResponse,
    LocalEventUpdate,
    RestaurantCreate,
    RestaurantResponse,
    RestaurantUpdate,
)

destination_router = APIRouter(
    prefix="/api/v1/destinations",
    tags=["Destinations"],
)

attraction_router = APIRouter(
    prefix="/api/v1/attractions",
    tags=["Attractions"],
)

hotel_router = APIRouter(
    prefix="/api/v1/hotels",
    tags=["Hotels"],
)

restaurant_router = APIRouter(
    prefix="/api/v1/restaurants",
    tags=["Restaurants"],
)

local_event_router = APIRouter(
    prefix="/api/v1/local-events",
    tags=["Local Events"],
)


# ============================================================
# DESTINATIONS
# ============================================================

@destination_router.post(
    "",
    response_model=DestinationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_destination(
    destination_data: DestinationCreate,
    db: Session = Depends(get_db),
):
    destination = Destination(**destination_data.model_dump())

    db.add(destination)
    db.commit()
    db.refresh(destination)

    return destination


@destination_router.get("", response_model=DestinationListResponse)
def list_destinations(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=50),
    search: str | None = Query(default=None),
    region: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Destination).filter(
        Destination.is_active.is_(True)
    )

    if search:
        query = query.filter(
            Destination.name.ilike(f"%{search}%")
        )

    if region:
        query = query.filter(
            Destination.region.ilike(f"%{region}%")
        )

    total = query.count()
    total_pages = math.ceil(total / limit) if total else 0

    destinations = (
        query.order_by(Destination.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "success": True,
        "data": DestinationListData(
            items=destinations,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        ),
    }

@destination_router.get(
    "/{destination_id}",
    response_model=DestinationResponse,
)
def get_destination(
    destination_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    destination = (
        db.query(Destination)
        .filter(
            Destination.id == destination_id,
            Destination.is_active.is_(True),
        )
        .first()
    )

    if destination is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Destination not found",
                },
            },
        )

    return destination


@destination_router.patch(
    "/{destination_id}",
    response_model=DestinationResponse,
)
def update_destination(
    destination_id: uuid.UUID,
    destination_data: DestinationUpdate,
    db: Session = Depends(get_db),
):
    destination = (
        db.query(Destination)
        .filter(
            Destination.id == destination_id,
            Destination.is_active.is_(True),
        )
        .first()
    )

    if destination is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Destination not found",
                },
            },
        )

    update_data = destination_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(destination, field, value)

    db.commit()
    db.refresh(destination)

    return destination


@destination_router.delete(
    "/{destination_id}",
    response_model=DestinationResponse,
)
def delete_destination(
    destination_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    destination = (
        db.query(Destination)
        .filter(
            Destination.id == destination_id,
            Destination.is_active.is_(True),
        )
        .first()
    )

    if destination is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Destination not found",
                },
            },
        )

    destination.is_active = False

    db.commit()
    db.refresh(destination)

    return destination


# ============================================================
# ATTRACTIONS
# ============================================================

@attraction_router.post(
    "",
    response_model=AttractionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_attraction(
    attraction_data: AttractionCreate,
    db: Session = Depends(get_db),
):
    destination = (
        db.query(Destination)
        .filter(
            Destination.id == attraction_data.destination_id,
            Destination.is_active.is_(True),
        )
        .first()
    )

    if destination is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "DESTINATION_NOT_FOUND",
                    "message": "Destination not found or inactive",
                },
            },
        )

    attraction = Attraction(**attraction_data.model_dump())

    db.add(attraction)
    db.commit()
    db.refresh(attraction)

    return attraction


@attraction_router.get(
    "",
    response_model=list[AttractionResponse],
)
def list_attractions(
    search: str | None = Query(default=None),
    region: str | None = Query(default=None),
    destination_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(Attraction)
        .join(
            Destination,
            Attraction.destination_id == Destination.id,
        )
        .filter(
            Attraction.is_active.is_(True),
            Destination.is_active.is_(True),
        )
    )

    if search:
        query = query.filter(
            Attraction.name.ilike(f"%{search}%")
        )

    if region:
        query = query.filter(
            Destination.region.ilike(f"%{region}%")
        )

    if destination_id:
        query = query.filter(
            Attraction.destination_id == destination_id
        )

    return query.order_by(Attraction.name.asc()).all()

@attraction_router.get(
    "/{attraction_id}",
    response_model=AttractionResponse,
)
def get_attraction(
    attraction_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    attraction = (
        db.query(Attraction)
        .filter(
            Attraction.id == attraction_id,
            Attraction.is_active.is_(True),
        )
        .first()
    )

    if attraction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Attraction not found",
                },
            },
        )

    return attraction


@attraction_router.patch(
    "/{attraction_id}",
    response_model=AttractionResponse,
)
def update_attraction(
    attraction_id: uuid.UUID,
    attraction_data: AttractionUpdate,
    db: Session = Depends(get_db),
):
    attraction = (
        db.query(Attraction)
        .filter(
            Attraction.id == attraction_id,
            Attraction.is_active.is_(True),
        )
        .first()
    )

    if attraction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Attraction not found",
                },
            },
        )

    update_data = attraction_data.model_dump(exclude_unset=True)

    if "destination_id" in update_data:
        destination = (
            db.query(Destination)
            .filter(
                Destination.id == update_data["destination_id"],
                Destination.is_active.is_(True),
            )
            .first()
        )

        if destination is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "DESTINATION_NOT_FOUND",
                        "message": "Destination not found or inactive",
                    },
                },
            )

    for field, value in update_data.items():
        setattr(attraction, field, value)

    db.commit()
    db.refresh(attraction)

    return attraction


@attraction_router.delete(
    "/{attraction_id}",
    response_model=AttractionResponse,
)
def delete_attraction(
    attraction_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    attraction = (
        db.query(Attraction)
        .filter(
            Attraction.id == attraction_id,
            Attraction.is_active.is_(True),
        )
        .first()
    )

    if attraction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Attraction not found",
                },
            },
        )

    attraction.is_active = False

    db.commit()
    db.refresh(attraction)

    return attraction


# ============================================================
# HOTELS
# ============================================================

@hotel_router.post(
    "",
    response_model=HotelResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_hotel(
    hotel_data: HotelCreate,
    db: Session = Depends(get_db),
):
    destination = (
        db.query(Destination)
        .filter(
            Destination.id == hotel_data.destination_id,
            Destination.is_active.is_(True),
        )
        .first()
    )

    if destination is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "DESTINATION_NOT_FOUND",
                    "message": "Destination not found or inactive",
                },
            },
        )

    hotel = Hotel(**hotel_data.model_dump())

    db.add(hotel)
    db.commit()
    db.refresh(hotel)

    return hotel


@hotel_router.get(
    "",
    response_model=list[HotelResponse],
)
def list_hotels(
    search: str | None = Query(default=None),
    region: str | None = Query(default=None),
    destination_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(Hotel)
        .join(
            Destination,
            Hotel.destination_id == Destination.id,
        )
        .filter(
            Hotel.is_active.is_(True),
            Destination.is_active.is_(True),
        )
    )

    if search:
        query = query.filter(
            Hotel.name.ilike(f"%{search}%")
        )

    if region:
        query = query.filter(
            Destination.region.ilike(f"%{region}%")
        )

    if destination_id:
        query = query.filter(
            Hotel.destination_id == destination_id
        )

    return query.order_by(Hotel.name.asc()).all()


@hotel_router.get(
    "/{hotel_id}",
    response_model=HotelResponse,
)
def get_hotel(
    hotel_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    hotel = (
        db.query(Hotel)
        .filter(
            Hotel.id == hotel_id,
            Hotel.is_active.is_(True),
        )
        .first()
    )

    if hotel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Hotel not found",
                },
            },
        )

    return hotel


@hotel_router.patch(
    "/{hotel_id}",
    response_model=HotelResponse,
)
def update_hotel(
    hotel_id: uuid.UUID,
    hotel_data: HotelUpdate,
    db: Session = Depends(get_db),
):
    hotel = (
        db.query(Hotel)
        .filter(
            Hotel.id == hotel_id,
            Hotel.is_active.is_(True),
        )
        .first()
    )

    if hotel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Hotel not found",
                },
            },
        )

    update_data = hotel_data.model_dump(exclude_unset=True)

    if "destination_id" in update_data:
        destination = (
            db.query(Destination)
            .filter(
                Destination.id == update_data["destination_id"],
                Destination.is_active.is_(True),
            )
            .first()
        )

        if destination is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "DESTINATION_NOT_FOUND",
                        "message": "Destination not found or inactive",
                    },
                },
            )

    for field, value in update_data.items():
        setattr(hotel, field, value)

    db.commit()
    db.refresh(hotel)

    return hotel


@hotel_router.delete(
    "/{hotel_id}",
    response_model=HotelResponse,
)
def delete_hotel(
    hotel_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    hotel = (
        db.query(Hotel)
        .filter(
            Hotel.id == hotel_id,
            Hotel.is_active.is_(True),
        )
        .first()
    )

    if hotel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Hotel not found",
                },
            },
        )

    hotel.is_active = False

    db.commit()
    db.refresh(hotel)

    return hotel


# ============================================================
# RESTAURANTS
# ============================================================

@restaurant_router.post(
    "",
    response_model=RestaurantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_restaurant(
    restaurant_data: RestaurantCreate,
    db: Session = Depends(get_db),
):
    destination = (
        db.query(Destination)
        .filter(
            Destination.id == restaurant_data.destination_id,
            Destination.is_active.is_(True),
        )
        .first()
    )

    if destination is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "DESTINATION_NOT_FOUND",
                    "message": "Destination not found or inactive",
                },
            },
        )

    restaurant = Restaurant(**restaurant_data.model_dump())

    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)

    return restaurant

@restaurant_router.get(
    "",
    response_model=list[RestaurantResponse],
)
def list_restaurants(
    search: str | None = Query(default=None),
    region: str | None = Query(default=None),
    destination_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(Restaurant)
        .join(
            Destination,
            Restaurant.destination_id == Destination.id,
        )
        .filter(
            Restaurant.is_active.is_(True),
            Destination.is_active.is_(True),
        )
    )

    if search:
        query = query.filter(
            Restaurant.name.ilike(f"%{search}%")
        )

    if region:
        query = query.filter(
            Destination.region.ilike(f"%{region}%")
        )

    if destination_id:
        query = query.filter(
            Restaurant.destination_id == destination_id
        )

    return query.order_by(Restaurant.name.asc()).all()


@restaurant_router.get(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
)
def get_restaurant(
    restaurant_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    restaurant = (
        db.query(Restaurant)
        .filter(
            Restaurant.id == restaurant_id,
            Restaurant.is_active.is_(True),
        )
        .first()
    )

    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Restaurant not found",
                },
            },
        )

    return restaurant


@restaurant_router.patch(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
)
def update_restaurant(
    restaurant_id: uuid.UUID,
    restaurant_data: RestaurantUpdate,
    db: Session = Depends(get_db),
):
    restaurant = (
        db.query(Restaurant)
        .filter(
            Restaurant.id == restaurant_id,
            Restaurant.is_active.is_(True),
        )
        .first()
    )

    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Restaurant not found",
                },
            },
        )

    update_data = restaurant_data.model_dump(exclude_unset=True)

    if "destination_id" in update_data:
        destination = (
            db.query(Destination)
            .filter(
                Destination.id == update_data["destination_id"],
                Destination.is_active.is_(True),
            )
            .first()
        )

        if destination is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "DESTINATION_NOT_FOUND",
                        "message": "Destination not found or inactive",
                    },
                },
            )

    for field, value in update_data.items():
        setattr(restaurant, field, value)

    db.commit()
    db.refresh(restaurant)

    return restaurant


@restaurant_router.delete(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
)
def delete_restaurant(
    restaurant_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    restaurant = (
        db.query(Restaurant)
        .filter(
            Restaurant.id == restaurant_id,
            Restaurant.is_active.is_(True),
        )
        .first()
    )

    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Restaurant not found",
                },
            },
        )

    restaurant.is_active = False

    db.commit()
    db.refresh(restaurant)

    return restaurant


# ============================================================
# LOCAL EVENTS
# ============================================================

@local_event_router.post(
    "",
    response_model=LocalEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_local_event(
    event_data: LocalEventCreate,
    db: Session = Depends(get_db),
):
    destination = (
        db.query(Destination)
        .filter(
            Destination.id == event_data.destination_id,
            Destination.is_active.is_(True),
        )
        .first()
    )

    if destination is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "DESTINATION_NOT_FOUND",
                    "message": "Destination not found or inactive",
                },
            },
        )

    event = LocalEvent(**event_data.model_dump())

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@local_event_router.get(
    "",
    response_model=list[LocalEventResponse],
)
def list_local_events(
    search: str | None = Query(default=None),
    region: str | None = Query(default=None),
    destination_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(LocalEvent)
        .join(
            Destination,
            LocalEvent.destination_id == Destination.id,
        )
        .filter(
            LocalEvent.is_active.is_(True),
            Destination.is_active.is_(True),
        )
    )

    if search:
        query = query.filter(
            LocalEvent.name.ilike(f"%{search}%")
        )

    if region:
        query = query.filter(
            Destination.region.ilike(f"%{region}%")
        )

    if destination_id:
        query = query.filter(
            LocalEvent.destination_id == destination_id
        )

    return query.order_by(LocalEvent.name.asc()).all()


@local_event_router.get(
    "/{event_id}",
    response_model=LocalEventResponse,
)
def get_local_event(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    event = (
        db.query(LocalEvent)
        .filter(
            LocalEvent.id == event_id,
            LocalEvent.is_active.is_(True),
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Local event not found",
                },
            },
        )

    return event


@local_event_router.patch(
    "/{event_id}",
    response_model=LocalEventResponse,
)
def update_local_event(
    event_id: uuid.UUID,
    event_data: LocalEventUpdate,
    db: Session = Depends(get_db),
):
    event = (
        db.query(LocalEvent)
        .filter(
            LocalEvent.id == event_id,
            LocalEvent.is_active.is_(True),
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Local event not found",
                },
            },
        )

    update_data = event_data.model_dump(exclude_unset=True)

    if "destination_id" in update_data:
        destination = (
            db.query(Destination)
            .filter(
                Destination.id == update_data["destination_id"],
                Destination.is_active.is_(True),
            )
            .first()
        )

        if destination is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "DESTINATION_NOT_FOUND",
                        "message": "Destination not found or inactive",
                    },
                },
            )

    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return event


@local_event_router.delete(
    "/{event_id}",
    response_model=LocalEventResponse,
)
def delete_local_event(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    event = (
        db.query(LocalEvent)
        .filter(
            LocalEvent.id == event_id,
            LocalEvent.is_active.is_(True),
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Local event not found",
                },
            },
        )

    event.is_active = False

    db.commit()
    db.refresh(event)

    return event