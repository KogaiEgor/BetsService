import logging
from src.config import rd


class KoefsHandler:
    def __init__(self, msg):
        self.msg = msg
        self.match_id = ''
        self.markets = ''
        self.logger = logging.getLogger(__name__)

    async def __validate_data(self):
        if isinstance(self.msg, list) and len(self.msg) > 1 and self.msg[1] == "update_markets":
            self.logger.debug(f"Data: {self.msg}")
            self.match_id = self.msg[2]
            self.markets = self.msg[-1]
            return True
        return False

    async def __cache_koefs(self):
        self.logger.debug(f"Get data for caching {self.markets}")
        # caching logic
        return self.markets

    async def save_message(self):
        if await self.__validate_data():
            await self.__cache_koefs()
            return True
        return False

