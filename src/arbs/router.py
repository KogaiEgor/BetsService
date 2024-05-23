from fastapi import APIRouter, status, Response

from src.config import rd
from src.arbs.schemas import Bet


router = APIRouter(
    prefix="/arbs",
    tags=["Arbs"]
)


@router.get("/get_arb/", status_code=status.HTTP_200_OK, response_model=Bet)
async def get_arb(response: Response):
    arb = await rd.hgetall("last_arb")
    if not arb:
        return []

    decoded_arb = {key.decode('utf-8'): value.decode('utf-8') for key, value in arb.items()}

    decoded_arb["koef"] = float(decoded_arb["koef"])
    decoded_arb["koef2"] = float(decoded_arb["koef2"])

    return Bet(**decoded_arb)

