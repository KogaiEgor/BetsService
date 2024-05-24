import aiohttp
import asyncio
import logging
import time
import json
import orjson

from src.config import odd_token, rd
from src.arbs.utils import calculate_arb

logger = logging.getLogger(__name__)
async def get_surebet_pari(sport):
    """
    Запрашивает вилки bet365 и parimatch с минимальным процентом 4
    :param sport: какой спорт ставим
    :return: ответ от апи
    """
    params = {
        'token': odd_token,
        'sport': sport,
        'bk2_name': 'bet365,parimatch_com',
        'min_fi': 0
    }

    url = 'http://api.oddscp.com:8111/forks'

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    logger.debug("Status 200 received from odd")
                    return await response.json()
                else:
                    logger.error("Wrong status from odd")
                    return None
        except:
            logger.error("Error trying to send request to odd")
            return None


async def create_link(market_data, href):
    """
    Создает ссылку с данных из oddscorp
    :param market_data:
    :param href:
    :return:
    """
    try:
        bet_data = json.loads(market_data)
        direct_param = href[27:]
        link = "https://www.bet365.com/dl/sportsbookredirect/?bs=" + bet_data.get("zw") + "~" + bet_data.get("od") + "&bet=1#/IP" + direct_param
        return link
    except Exception as e:
        print(e)
        logger.info("Empty links fields in match")


async def parse_surebet(json_data):
    """
    Достает из json данные для ставки на киберфутбол если они есть
    :param json_data: данные с апи
    :return: result: на что ставка, bet_type: тип ставки, link: ссылка на матч, koef: коэф на бетке, koef2: коэф на пари
    :return: None если нет подходящих матчей
    """
    if json_data is None:
        logger.error("Error occurred, None received")
        return None

    for match in json_data:
        if "Esports" in match["BK1_game"] and "8 mins" in match["BK1_league"]:
            logger.debug(f"Get Esports data BK1: {json.dumps(json_data, indent=3)}")
            match_data = await process_match(match, "BK1", "BK2")
            if match_data:
                return match_data
        elif "Esports" in match["BK2_game"] and "8 mins" in match["BK2_league"]:
            logger.debug(f"Get Esports data BK2: {json.dumps(json_data, indent=3)}")
            match_data = await process_match(match, "BK2", "BK1")
            if match_data:
                return match_data

    logger.debug("No arbs more than 4% or no value on pari")
    return None


async def process_match(match, bk1, bk2):
    logger.debug(f"Get Esports data {bk1}: {json.dumps(match, indent=3)}")
    koef1 = match[f"{bk1}_cf"]
    koef2 = match[f"{bk2}_cf"]
    logger.debug(f"bet365: {koef1} pari: {koef2}")
    arb = calculate_arb(koef1, koef2)
    if arb >= 0.01:
        match_name = match[f'{bk1}_game']
        bet_id = match[f'{bk2}_event_id']
        link = await create_link(match[f"{bk1}_market_meta"], match[f"{bk1}_href"])
        result = match[f"{bk1}_bet"]
        mirror_res = match[f"{bk2}_bet"]
        bet_type = match["bet_type"]
        koef = match[f"{bk1}_cf"]
        logger.debug(f"Get match data {result, bet_type, link, koef}")
        return result, bet_type, link, koef, koef2, bet_id, mirror_res, match_name
    return None


async def get_surebet():
    """
    Вызывает функцию для которая обращается к АПИ и использует ее пока не получит нужные данные
    :return:
    """
    json_data = await get_surebet_pari("soccer")

    while json_data is None:
        logger.error(f"Error occurred trying get data from odd")
        time.sleep(3)
        json_data = await get_surebet_pari("soccer")
    bet = await parse_surebet(json_data)
    while bet == None:
        time.sleep(3)
        bet = await parse_surebet(json_data)
        json_data = await get_surebet_pari("soccer")
    return bet


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

