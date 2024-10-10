import aiohttp
import asyncio
import logging
import json
import orjson

from src.config import odd_token
from src.logger import setup_logging



class ValuesOddHandler:

    def __init__(self):
        self.params = {
            "token": odd_token,
            "bk_name": "bet365",
            "get_market_data": 2,
            "min_fi": 6
        }
        self.url = "http://api.oddscp.com:8111/valuebets"
        self.logger = setup_logging()
        self.data = None
        self.match = None
        self.link = None


    async def get_value_odd(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.url, params=self.params) as response:
                    if response.status == 200:
                        self.logger.debug("Status 200 received from odd values")
                        self.data = await response.json()
                    else:
                        self.logger.debug("Wrong status code from odd values")
            except:
                self.logger.error("Error sending request to odd values")


    async def filter_value(self):
        if self.data is None:
            self.logger.error("Error, none received")

        flag = False
        for value in self.data:
            cfs = value['valuing_data']['cfs']
            for cf in cfs:
                if cf == "PIN":
                    self.match = value
                    flag = True
                    break

            if flag == True:
                break

        if self.match is None:
            self.logger.debug("No values for bet365 and pinnacle")


    async def create_link(self):
        try:
            bet_data = json.loads(self.match[f"BK1_market_meta"])
            direct_param = self.match[f"BK1_href"][27:]
            self.link = "https://www.bet365.com/dl/sportsbookredirect/?bs=" + bet_data.get("zw") + "~" + bet_data.get(
                "od") + "&bet=1#/IP" + direct_param
        except Exception as e:
            self.logger.info("Empty links fields in match", exc_info=e)


    async def process_match(self):
        self.logger.debug(f"Get Esports data {self.match}: {json.dumps(self.match, indent=3)}")

        await self.create_link()

        match_name = self.match["BK1_game"]
        bet_id = self.match[f'BK1_event_id']
        result = self.match[f"BK1_bet"]
        bet_type = "Valuebet"
        koef = self.match[f"BK1_cf"]
        koef2 = float(self.match["valuing_data"]["cfs"]["PIN"][0])
        link = self.link

        return result, bet_type, link, koef, koef2, bet_id, 0, match_name


    async def run(self):
        await self.get_value_odd()
        await self.filter_value()
        await asyncio.sleep(1)

        while self.data is None or self.match is None:
            await self.get_value_odd()
            await self.filter_value()
            await asyncio.sleep(1)

        return await self.process_match()


# async def main():
#     res = await ValuesOddHandler().run()
#     print(res)
#
# if __name__ == "__main__":
#     asyncio.run(main())






