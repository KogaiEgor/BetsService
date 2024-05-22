import orjson
import websockets
import logging

from src.config import odd_token
from src.parser.service import KoefsHandler


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
    async with websockets.connect(
        "ws://api.oddscp.com:8001", ping_interval=None
    ) as websocket:
        await websocket.send(message)
        async for msg in websocket:
            data = orjson.loads(msg)
            handler = KoefsHandler(data)
            await handler.save_message()


