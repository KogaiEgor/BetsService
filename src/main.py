import asyncio
from typing import List
from fastapi import FastAPI
from fastapi import HTTPException

from src.config import rd
from src.logger import setup_logging
from src.bots.router import router as router_bots
from src.parser.oddscorp_arbs import get_surebet, cache_arbs
from src.parser.oddscorp_websocket import read_odds_socket
from src.parser.schemas import Bet



app = FastAPI(
    title="BetsService"
)

logger = setup_logging()
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cache_arbs())
    asyncio.create_task(read_odds_socket())


@app.get("/arbs/", response_model=List[Bet])
async def get_arbs():
    arb = await rd.hgetall("last_arb")
    if not arb:
        return []

    decoded_arb = {key.decode('utf-8'): value.decode('utf-8') for key, value in arb.items()}

    decoded_arb["koef"] = float(decoded_arb["koef"])
    decoded_arb["koef2"] = float(decoded_arb["koef2"])

    return [Bet(**decoded_arb)]


@app.get("/update_koefs/")
async def update_koefs(match_id: str):
    koefs = await rd.hgetall(match_id)
    logger.debug(koefs)
    decoded_koef = {key.decode('utf-8'): value.decode('utf-8') for key, value in koefs.items()}
    logger.debug(decoded_koef)
    return [decoded_koef]


app.include_router(router_bots)

