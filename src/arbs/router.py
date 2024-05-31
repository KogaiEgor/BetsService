import logging
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.config import rd
from src.arbs.schemas import Bet


router = APIRouter(
    prefix="/arbs",
    tags=["Arbs"]
)
logger = logging.getLogger(__name__)

@router.get("/get_arb/", status_code=status.HTTP_200_OK, response_model=Bet)
async def get_arb():
    arb = await rd.hgetall("last_arb")
    if not arb:
        logger.debug("No arbs")
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "No arbs from odd"})

    decoded_arb = {key.decode('utf-8'): value.decode('utf-8') for key, value in arb.items()}

    decoded_arb["koef"] = float(decoded_arb["koef"])
    decoded_arb["koef2"] = float(decoded_arb["koef2"])

    return Bet(**decoded_arb)

