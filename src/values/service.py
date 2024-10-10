import logging
import asyncio

from src.config import rd
from src.arbs.oddscorp_arbs import ArbsOddHadler


logger = logging.getLogger(__name__)
async def get_surebettest():
    return "result", "bet_type", "link", 1.5, 2.5, "bet_id", "mirror_res", "match_name"


async def cache_values():
    while True:
        data = await ArbsOddHadler().run()
        if data is None:
            await asyncio.sleep(2)
            continue
        result, bet_type, link, koef, koef2, bet_id, mirror_res, match_name = data

        logger.info(f"Get arbs data: {result, bet_type, link, koef, koef2, bet_id, mirror_res, match_name}")

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

        await rd.hset("last_value", mapping=data)
        await rd.expire("last_value", 9)
        await asyncio.sleep(3)

