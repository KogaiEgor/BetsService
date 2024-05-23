import asyncio
import orjson

from typing import List
from fastapi import FastAPI, status, Response

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


@app.get("/arbs/", status_code=status.HTTP_200_OK, response_model=List[Bet])
async def get_arbs(response: Response):
    arb = await rd.hgetall("last_arb")
    if not arb:
        return []

    decoded_arb = {key.decode('utf-8'): value.decode('utf-8') for key, value in arb.items()}

    decoded_arb["koef"] = float(decoded_arb["koef"])
    decoded_arb["koef2"] = float(decoded_arb["koef2"])

    return [Bet(**decoded_arb)]


@app.get("/update_koefs/", status_code=status.HTTP_200_OK)
async def update_koefs(match_id: str, market: str, response: Response):
    koefs = await rd.hgetall(match_id)
    decoded_koef = {key.decode('utf-8'): value.decode('utf-8') for key, value in koefs.items()}
    if 'markets' not in decoded_koef.keys():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'msg': f"No match with id {match_id}"}
    markets = orjson.loads(decoded_koef['markets'])
    logger.debug(decoded_koef)
    for i in markets:
        if i[0] == market:
            return {market: float(i[2])}
    response.status_code = status.HTTP_400_BAD_REQUEST
    return {'msg': f"No market {market} in match {match_id}"}


app.include_router(router_bots)

