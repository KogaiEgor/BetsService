import logging
import asyncio
import time

from src.config import rd
from src.logger import setup_logging



logger = setup_logging()
class ValueTest:
    async def run(self):
        return {
                "result": 'SET_01__HANDICAP__P1(4.5)',
                "bet_type": "Valuebet",
                "link": "https://www.bet365.com/dl/sportsbookredirect/?bs=163216493-1424406378~10/11&bet=1#/IP/EV2044805951098285842C151",
                "koef": 1.909,
                "koef2": 1.819,
                "bet_id": 'BT3EC2F0CFCA647D',
                "mirror_res": "",
                "match_name": 'Fnatic vs Metizport'
            }


class ArbTest:
    async def run(self):
        return {
                "result": 'TOTALS__OVER(2.5)',
                "bet_type": "Arb",
                "link": 'https://www.bet365.com/dl/sportsbookredirect/?bs=163221137-1424949230~5/4&bet=1#/IP/EV151098326402C1',
                "koef": 2.25,
                "koef2": 2.05,
                "bet_id": 'PACSC7860DD683D7',
                "mirror_res": "TOTALS__UNDER(2.5)",
                "match_name": 'Napoli (d1pseN) Esports vs Juventus (Jekunam) Esports'
            }




async def cache_bet(handler):
    while True:
        data = await handler().run()
        if data is None:
            logger.debug(f"No data from {handler.__name__}")
            await asyncio.sleep(2)
            continue

        logger.debug(f"Get data from {handler.__name__}")
        logger.info(f"Get bet data: "
                    f"{data['result'], data['bet_type'], data['link'], data['koef'], data['koef2'], data['bet_id'], data['mirror_res'], data['match_name']}")


        if data['bet_type'] == "Arb":
            hash_name = "last_arb"
        else:
            hash_name = "last_value"

        logger.debug(f"Hash name - {hash_name}")
        await rd.hset(hash_name, mapping=data)
        logger.debug(f"Saved hash")
        await rd.expire(hash_name, 9)



async def get_cache():
    logger.debug("Trying to get arb from hash")
    bet = await rd.hgetall("last_arb")
    if not bet:
        logger.debug("No arbs")
        logger.debug("Trying to get value from hash")
        bet = await rd.hgetall("last_value")
        if not bet:
            logger.debug("No values")
            return None

    logger.debug(bet)
    return bet


# async def main():
#     await cache_bet(ArbTest)
#     print(await get_cache())
#     time.sleep(4)
#     await cache_bet(ValueTest)
#     print(await get_cache())
#
#
# if __name__ == "__main__":
#     asyncio.run(main())

