import logging
import asyncio

from src.config import rd
from src.arbs.oddscorp_arbs import get_surebet


logger = logging.getLogger(__name__)
async def get_surebettest():
    return "result", "bet_type", "link", 1.5, 2.5, "bet_id", "mirror_res", "match_name"


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

        await rd.hset("last_arb", mapping=data)

        await asyncio.sleep(3)

