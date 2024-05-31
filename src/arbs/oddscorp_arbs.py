import aiohttp
import asyncio
import logging
import json
import orjson

from src.config import odd_token, rd
from src.arbs.utils import calculate_arb

logger = logging.getLogger(__name__)
class ArbsOddHadler:
    def __init__(self):
        self.params = {
                        'token': odd_token,
                        'sport': 'soccer',
                        'bk2_name': 'bet365,parimatch_com',
                        'min_fi': 0
                    }
        self.url = 'http://api.oddscp.com:8111/forks'
        self.betka = ''
        self.pari = ''
        self.logger = logging.getLogger(__name__)

        self.link = ''

        self.data = None
        self.match = None


    async def get_arbs_from_odd(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.url, params=self.params) as response:
                    if response.status == 200:
                        logger.debug("Status 200 received from odd")
                        self.data = await response.json()
                    else:
                        self.logger.error("Wrong status from odd")
                        return None
            except:
                self.logger.error("Error trying to send request to odd")
                return None


    async def parse_data(self):
        if self.data is None:
            self.logger.error("Error occurred, None received")
            return None

        for match in self.data:
            if "Esports" in match["BK1_game"] and "8 mins" in match["BK1_league"]:
                self.logger.debug(f"Get Esports data BK1: {orjson.dumps(self.data)}")
                self.betka = 'BK1'
                self.pari = 'BK2'
                self.match = match
            elif "Esports" in match["BK2_game"] and "8 mins" in match["BK2_league"]:
                self.logger.debug(f"Get Esports data BK2: {orjson.dumps(self.data)}")
                self.betka = 'BK2'
                self.pari = 'BK1'
                self.match = match

        logger.debug("No arbs more than 4% or no value on pari")

    async def create_link(self):
        try:
            bet_data = json.loads(self.match[f"{self.betka}_market_meta"])
            direct_param = self.match[f"{self.betka}_href"][27:]
            self.link = "https://www.bet365.com/dl/sportsbookredirect/?bs=" + bet_data.get("zw") + "~" + bet_data.get(
                "od") + "&bet=1#/IP" + direct_param
        except Exception as e:
            self.logger.info("Empty links fields in match", exc_info=e)


    async def process_match(self):
        self.logger.debug(f"Get Esports data {self.betka}: {json.dumps(self.match, indent=3)}")
        koef_betka = self.match[f"{self.betka}_cf"]
        koef_pari = self.match[f"{self.pari}_cf"]
        self.logger.debug(f"bet365: {koef_betka} pari: {koef_pari}")
        arb = calculate_arb(koef_betka, koef_pari)
        if arb >= 0.01:
            await self.create_link()
            match_name = self.match[f'{self.betka}_game']
            bet_id = self.match[f'{self.pari}_event_id']
            result = self.match[f"{self.betka}_bet"]
            mirror_res = self.match[f"{self.pari}_bet"]
            bet_type = self.match["bet_type"]
            koef = self.match[f"{self.betka}_cf"]
            self.logger.debug(f"Get match data {result, bet_type, self.link, koef}")
            return result, bet_type, self.link, koef_betka, koef_pari, bet_id, mirror_res, match_name
        return None

    async def run(self):
        await self.get_arbs_from_odd()
        await self.parse_data()
        await asyncio.sleep(3)
        while self.data or self.match is None:
            await self.get_arbs_from_odd()
            await self.parse_data()
            await asyncio.sleep(3)
        return await self.process_match()

