import asyncio

import orjson
import websockets
import logging

from src.config import odd_token
from src.market.service import KoefsHandler


config = {
    "cmd": "subscribe",
    "auth_key": odd_token,
    "needed_bk": ["parimatch_com:live"],
    "send_events_ids": True,
    "needed_sport": ["soccer"],
    "short_format": True
}
message = orjson.dumps(config)


logger = logging.getLogger(__name__)
async def read_odds_socket():
    while True:
        async with websockets.connect(
            "ws://api.oddscp.com:8001", ping_interval=None
        ) as websocket:
            await websocket.send(message)
            async for msg in websocket:
                data = orjson.loads(msg)
                # if isinstance(data, list) and len(data) > 1 and (data[1] in ("update_markets", "remove_event", "remove_markets")):
                #     print(msg)
                #logger.debug(f" Websocket {msg}")
                if isinstance(data, dict):
                    if 'last_delay_100avg' in data.keys():
                        logger.info(F"PING = {data}")
                        if data['last_delay_100avg'] > 100:
                            logger.warning("Ping exceeded 100ms, reconnecting...")
                            await asyncio.sleep(1)
                            logger.info("Websocket connection reloaded")
                            break
                handler = KoefsHandler(data)
                await handler.save_message()
        logger.info("Websocket connection reloaded")
