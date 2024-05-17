import asyncio
from fastapi import FastAPI
from fastapi import HTTPException

import redis

from src.config import rd
from src.logger import setup_logging
from src.parser.oddscorp_arbs import get_surebet



app = FastAPI(
    title="BetsService"
)

logger = setup_logging()

# async def get_surebettest():
#     # Здесь будет ваш код для получения данных surebet
#     return "result", "bet_type", "link", 1.5, 2.5, "bet_id", "mirror_res", "match_name"


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cache_arbs())


async def cache_arbs():
    while True:
        result, bet_type, link, koef, koef2, bet_id, mirror_res, match_name = await get_surebet()
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


@app.get("/arbs/")
async def get_arbs():
    arb = rd.hgetall("last_arb")
    return arb



