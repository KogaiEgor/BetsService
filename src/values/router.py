import logging
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.config import rd
from src.arbs.schemas import Bet
from src.logger import setup_logging


router = APIRouter(
    prefix="/valuebet",
    tags=["Valuebet"]
)
logger = setup_logging()

@router.get("/get_valuebet/", status_code=status.HTTP_200_OK, response_model=Bet)
async def get_arb():
    arb = await rd.hgetall("last_value")
    if not arb:
        logger.debug("No values")
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "No values from odd"})

    decoded_value= {key.decode('utf-8'): value.decode('utf-8') for key, value in arb.items()}

    decoded_value["koef"] = float(decoded_value["koef"])
    decoded_value["koef2"] = float(decoded_value["koef2"])

    return Bet(**decoded_value)


@router.get("/get_bet/", status_code=status.HTTP_200_OK, response_model=Bet)
async def get_bet():
    bet = await rd.hgetall("last_arb")
    if not bet:
        logger.debug("No arbs")
        bet = await rd.hgetall("last_value")
        if not bet:
            logger.debug("No values")
            return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "No bets from odd"})

    decoded_bet = {key.decode('utf-8'): value.decode('utf-8') for key, value in bet.items()}

    decoded_bet["koef"] = float(decoded_bet["koef"])
    decoded_bet["koef2"] = float(decoded_bet["koef2"])

    return Bet(**decoded_bet)