import asyncio
from typing import List
from fastapi import FastAPI
from fastapi import HTTPException

from src.config import rd
from src.logger import setup_logging
from src.parser.oddscorp_arbs import get_surebet
from src.parser.schemas import Bet



app = FastAPI(
    title="BetsService"
)

logger = setup_logging()

async def get_surebettest():
    return "result", "bet_type", "link", 1.5, 2.5, "bet_id", "mirror_res", "match_name"


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cache_arbs())


async def cache_arbs():
    while True:
        result, bet_type, link, koef, koef2, bet_id, mirror_res, match_name = await get_surebettest()
        logger.info(f"Data: {result, bet_type, link, koef, koef2, bet_id, mirror_res, match_name}")

        data = {
            "result": result,
            "bet_type": bet_type,
            "link": link,
            "koef": koef,
            "koef2": koef2,
            "bet_id": bet_id,
            "mirror_res": mirror_res,
            "match_name": match_name
        }

        rd.hset("last_arb", mapping=data)

        await asyncio.sleep(3)


@app.get("/arbs/", response_model=List[Bet])
async def get_arbs():
    arb = rd.hgetall("last_arb")
    if not arb:
        return []

    decoded_arb = {key.decode('utf-8'): value.decode('utf-8') for key, value in arb.items()}

    # Преобразуем необходимые поля обратно в float
    decoded_arb["koef"] = float(decoded_arb["koef"])
    decoded_arb["koef2"] = float(decoded_arb["koef2"])

    return [Bet(**decoded_arb)]


