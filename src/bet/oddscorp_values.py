import json
import asyncio

from src.config import odd_token
from src.bet.utils import calculate_value
from src.bet.oddscorp_bet import BaseOddHandler



class ValuesOddHandler(BaseOddHandler):
    def __init__(self):
        super().__init__(
            url="http://api.oddscp.com:8111/valuebets",
            params={
                "token": odd_token,
                "sport": "tennis,soccer,basketball",
                "bk_name": "bet365",
                "get_market_data": 2,
                "min_fi": 8
            }
        )


    async def filter_data(self):
        if self.data is None:
            self.logger.error("Error, none received")

        flag = False
        for value in self.data:
            koef = value['BK1_cf']
            cfs = value['valuing_data']['cfs']
            for bk_name, bk_data in cfs.items():
                if bk_name == "PIN":
                    if calculate_value(bk_data[0], koef) >= 8:
                        self.match = value
                        flag = True
                    break

            if flag == True:
                break

        if self.match is None:
            self.logger.debug("No values more 6% on pinnacle")


    async def process_match(self):
        self.logger.debug(f"Get Esports data {self.match}: {json.dumps(self.match, indent=3)}")
        await self.create_link()

        data = {
            "result": self.match["BK1_bet"],
            "bet_type": "Valuebet",
            "link": self.link,
            "koef": self.match["BK1_cf"],
            "koef2": float(self.match["valuing_data"]["cfs"]["PIN"][0]),
            "bet_id": self.match["BK1_event_id"],
            "mirror_res": "",
            "match_name": self.match["BK1_game"]
        }

        return data


# async def main():
#     res = await ValuesOddHandler().run()
#     print(res)
#
# if __name__ == "__main__":
#     asyncio.run(main())




