import logging
from fastapi import APIRouter, status, Response

from src.config import rd
from src.arbs.schemas import Bet


router = APIRouter(
    prefix="/arbs",
    tags=["Arbs"]
)
logger = logging.getLogger(__name__)

@router.get("/get_arb/", status_code=status.HTTP_200_OK, response_model=Bet)
async def get_arb(response: Response):
    arb = await rd.hgetall("last_arb")
    if not arb:
        return []
    result = await rd.delete("last_arb")

    if result == 0:
        logger.debug(f"last_arb was not found in the cache")
    else:
        logger.debug(f"last_arb was successfully deleted from the cache")

    decoded_arb = {key.decode('utf-8'): value.decode('utf-8') for key, value in arb.items()}

    decoded_arb["koef"] = float(decoded_arb["koef"])
    decoded_arb["koef2"] = float(decoded_arb["koef2"])

    return Bet(**decoded_arb)

