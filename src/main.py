import asyncio
from fastapi import FastAPI
from src.logger import setup_logging
from src.parser.oddscorp_arbs import get_surebet, get_surebet_pari


app = FastAPI(
    title="BetsService"
)

logger = setup_logging()

@app.on_event("startup")
async def startup_event():
    while True:
        result, bet_type, link, koef, koef2, bet_id, mirror_res, match_name = await get_surebet()
        logger.info(f"Data: {result, bet_type, link, koef, koef2, bet_id, mirror_res, match_name}")
        await asyncio.sleep(3)


@app.get("/arbs/")
async def get_arb():
    arb = await get_surebet_pari("soccer")
    return arb



