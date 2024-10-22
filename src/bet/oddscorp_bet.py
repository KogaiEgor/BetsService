import aiohttp
import asyncio
import json

from abc import ABC, abstractmethod
from src.logger import setup_logging


class BaseOddHandler(ABC):
    def __init__(self, url, params):
        self.params = params
        self.url = url
        self.logger = setup_logging()
        self.data = None
        self.match = None
        self.link = None
        self.betka = "BK1"


    async def get_data_from_api(self):
        # self.logger.debug(self.params)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.url, params=self.params) as response:
                    if response.status == 200:
                        self.logger.debug(f"Status 200 received from odd")
                        self.data = await response.json()
                    else:
                        self.logger.error(f"Wrong status code from {self.url}: {response.status}")
            except Exception as e:
                self.logger.error(f"Error sending request to {self.url}", exc_info=e)


    async def create_link(self):
        try:
            bet_data = json.loads(self.match[f"{self.betka}_market_meta"])
            direct_param = self.match[f"{self.betka}_href"][27:]
            self.link = f"https://www.bet365.com/dl/sportsbookredirect/?bs={bet_data.get('zw')}~{bet_data.get('od')}&bet=1#/IP" + direct_param
        except Exception as e:
            self.logger.error("Error creating link", exc_info=e)


    @abstractmethod
    async def filter_data(self):
        """Метод для фильтрации данных должен быть реализован в дочерних классах"""
        pass


    @abstractmethod
    async def process_match(self):
        """Метод для обработки матча должен быть реализован в дочерних классах"""
        pass


    async def run(self):
        await self.get_data_from_api()
        await self.filter_data()
        await asyncio.sleep(1)
        while self.data is None or self.match is None:
            await self.get_data_from_api()
            await self.filter_data()
            await asyncio.sleep(1)
        return await self.process_match()




