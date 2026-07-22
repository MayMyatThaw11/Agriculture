from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.ndvi import NDVIMeasurement
from app.db.session import get_db_session
from app.schemas.ndvi import NDVIResponse

router = APIRouter(tags=["ndvi"])


@router.get(
    "/ndvi/{pcode}",
    response_model=NDVIResponse,
    status_code=status.HTTP_200_OK,
    summary="Get NDVI data for a region",
)
async def get_ndvi_data(
    pcode: str,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    result = await session.execute(
        select(NDVIMeasurement)
        .where(NDVIMeasurement.region_pcode == pcode)
        .order_by(NDVIMeasurement.id)
    )
    measurements = result.scalars().all()

    if not measurements:
        raise HTTPException(status_code=404, detail=f"No NDVI data found for region {pcode}")

    return NDVIResponse(
        labels=[m.label for m in measurements],
        vim=[m.vim for m in measurements],
        viq=[m.viq for m in measurements],
    )
