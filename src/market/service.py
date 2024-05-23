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
            self.match_id = self.msg[2]
            self.markets = self.msg[-1]
            return True
        elif isinstance(self.msg, list) and len(self.msg) > 1 and self.msg[1] == "remove_event":
            self.logger.debug("Trying to delete event")
            await self.__delete_match(self.msg[2])
        elif isinstance(self.msg, list) and len(self.msg) > 1 and self.msg[1] == "remove_markets":
            self.logger.debug("Trying to remove market")
            await self.__remove_markets(self.msg[2])
        return False


    async def __cache_koefs(self):
        self.logger.debug(f"Cache data with key {self.match_id} and data {self.markets}")
        serialized_data = orjson.dumps(self.markets)
        await rd.hset(self.match_id, mapping={"markets": serialized_data})
        await rd.expire(self.match_id, 480)
        return self.markets


    async def save_message(self):
        if await self.__validate_data():
            await self.__cache_koefs()
            return True
        return False


    async def __delete_match(self, match_id):
        self.logger.debug(f"Trying to delete event with id {match_id}")
        result = await rd.delete(match_id)

        if result == 0:
            self.logger.debug(f"Key {match_id} was not found in the cache")
        else:
            self.logger.debug(f"Key {match_id} was successfully deleted from the cache")



    async def __remove_markets(self, match_id):
        data = await rd.hgetall(match_id)

        if not data:
            self.logger.error(f"Match {match_id} not found in cache")
            return

        decode_data = {key.decode('utf-8'): value.decode('utf-8') for key, value in data.items()}
        remove_markets = set(self.msg[3])

        markets = decode_data['markets']
        updated_markets = []

        for market in markets:
            if market[0] not in remove_markets:
                updated_markets.append(market)

        self.markets = markets
        self.logger.debug(f"Trying to save new markets {markets}")
        await self.__cache_koefs()

