import math
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.destination import Destination
from app.schemas.tourism import (
    DestinationCreate,
    DestinationListData,
    DestinationListResponse,
    DestinationResponse,
    DestinationUpdate,
)

router = APIRouter(prefix="/api/v1/destinations", tags=["Destinations"])


@router.post(
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


@router.get("", response_model=DestinationListResponse)
def list_destinations(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    query = db.query(Destination).filter(Destination.is_active.is_(True))

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


@router.get("/{destination_id}", response_model=DestinationResponse)
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


@router.patch("/{destination_id}", response_model=DestinationResponse)
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


@router.delete("/{destination_id}", response_model=DestinationResponse)
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