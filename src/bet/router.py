from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.config import rd
from src.bet.schemas import Bet
from src.logger import setup_logging
from src.bet.service import get_cache


router = APIRouter(
    prefix="/bet",
    tags=["Bet"]
)
logger = setup_logging()
@router.get("/get_bet/", status_code=status.HTTP_200_OK, response_model=Bet)
async def get_bet():
    bet = await get_cache()
    if not bet:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "No bets from odd"})

    decoded_bet = {key.decode('utf-8'): value.decode('utf-8') for key, value in bet.items()}

    decoded_bet["koef"] = float(decoded_bet["koef"])
    decoded_bet["koef2"] = float(decoded_bet["koef2"])

    return Bet(**decoded_bet)

