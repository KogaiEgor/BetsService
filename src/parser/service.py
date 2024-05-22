import logging
import orjson
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
        elif isinstance(self.msg, list) and len(self.msg) > 1 and self.msg[1] == "remove_event":
            await self.delete_match(self.msg[2])
        return False

    async def __cache_koefs(self):
        self.logger.debug(f"Cache data with key {self.match_id} and data {self.markets}")
        serialized_data = orjson.dumps(self.markets)
        await rd.hset(self.match_id, mapping={"markets": serialized_data})
        return self.markets

    async def save_message(self):
        if await self.__validate_data():
            await self.__cache_koefs()
            return True
        return False


    async def delete_match(self, match_id):
        try:
            self.logger.debug(f"Trying to delete event with id {match_id}")
            await rd.delete(match_id)
            return
        except:
            return
