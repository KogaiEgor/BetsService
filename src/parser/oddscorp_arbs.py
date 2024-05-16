import aiohttp

from src.config import odd_token


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
                    return await response.json()
                else:
                    return None
        except:
            return None

