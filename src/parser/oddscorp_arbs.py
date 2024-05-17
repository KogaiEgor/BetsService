import aiohttp
import logging
import time
import json

from src.config import odd_token
from src.parser.utils import calculate_arb

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
        'min_fi': 4
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
            koef1 = match["BK1_cf"]
            koef2 = match["BK2_cf"]
            logger.debug(f"bet365: {koef1} pari: {koef2}")
            arb = calculate_arb(koef1, koef2)
            if arb >= 0.04:
                match_name = match['BK1_game']
                bet_id = match['BK2_event_id']
                link = await create_link(match["BK1_market_meta"], match["BK1_href"])
                result = match["BK1_bet"]
                mirror_res = match["BK2_bet"]
                bet_type = match["bet_type"]
                koef = match["BK1_cf"]
                logger.debug(f"Get match data {result, bet_type, link, koef}")
                return result, bet_type, link, koef, koef2, bet_id, mirror_res, match_name
        elif "Esports" in match["BK2_game"] and "8 mins" in match["BK2_league"]:
            logger.debug(f"Get Esports data BK2: {json.dumps(json_data, indent=3)}")
            koef1 = match["BK2_cf"]
            koef2 = match["BK1_cf"]
            logger.debug(f"bet365: {koef1} pari: {koef2}")
            arb = calculate_arb(koef1, koef2)
            if arb >= 0.04:
                match_name = match['BK2_game']
                bet_id = match['BK1_event_id']
                link = await create_link(match["BK2_market_meta"], match["BK2_href"])
                result = match["BK2_bet"]
                mirror_res = match["BK1_bet"]
                bet_type = match["bet_type"]
                koef = match["BK2_cf"]
                logger.debug(f"Get match data {result, bet_type, link, koef}")
                return result, bet_type, link, koef, koef2, bet_id, mirror_res, match_name

    logger.debug("No arbs more than 4% or no value on pari")
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
        time.sleep(2)
        bet = await parse_surebet(json_data)
        json_data = get_surebet_pari("soccer")
    return bet
