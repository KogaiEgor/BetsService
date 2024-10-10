import json
import asyncio

from src.config import odd_token, rd
from src.bet.utils import calculate_arb
from src.bet.oddscorp_bet import BaseOddHandler


class ArbsOddHandler(BaseOddHandler):
    def __init__(self):
        super().__init__(
            url='http://api.oddscp.com:8111/forks',
            params={
                'token': odd_token,
                'sport': 'soccer',
                'bk2_name': 'bet365,parimatch_com',
                'min_fi': 4
            }
        )
        self.betka = ''
        self.pari = ''


    async def filter_data(self):
        if self.data is None:
            self.logger.error("Error occurred, None received")
            return

        alive_arb = float('inf')
        for match in self.data:
            if "Esports" in match["BK1_game"] and "8 mins" in match["BK1_league"]:
                if match["alive_sec"] < alive_arb:
                    self.betka = 'BK1'
                    self.pari = 'BK2'
                    self.match = match
                    alive_arb = match["alive_sec"]
            elif "Esports" in match["BK2_game"] and "8 mins" in match["BK2_league"]:
                if match["alive_sec"] < alive_arb:
                    self.betka = 'BK2'
                    self.pari = 'BK1'
                    self.match = match
                    alive_arb = match["alive_sec"]

        if self.match is None:
            self.logger.debug("No arbs more than 4% on pari")


    async def process_match(self):
        self.logger.debug(f"Get Esports data {self.betka}: {json.dumps(self.match, indent=3)}")
        koef_betka = self.match[f"{self.betka}_cf"]
        koef_pari = self.match[f"{self.pari}_cf"]
        self.logger.debug(f"bet365: {koef_betka} pari: {koef_pari}")

        arb = calculate_arb(koef_betka, koef_pari)
        if arb >= 0.0396:
            await self.create_link()

            data = {
                "result": self.match[f"{self.betka}_bet"],
                "bet_type": "Arb",
                "link": self.link,
                "koef_betka": koef_betka,
                "koef_pari": koef_pari,
                "bet_id": self.match[f"{self.pari}_event_id"],
                "mirror_res": self.match[f"{self.pari}_bet"],
                "match_name": self.match[f'{self.betka}_game']
            }
            return data
        return None


# async def main():
#     arb = await ArbsOddHandler().run()
#     print(arb)
#
# if __name__ == "__main__":
#     asyncio.run(main())

