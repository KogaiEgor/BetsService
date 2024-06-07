import asyncio

import orjson
import websockets
import logging
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK, InvalidMessage

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
        try:
            async with websockets.connect(
                "ws://api.oddscp.com:8001", ping_interval=None
            ) as websocket:
                await websocket.send(message)
                async for msg in websocket:
                    try:
                        msg = await asyncio.wait_for(websocket.recv(), timeout=60)
                        if msg is None:
                            logger.warning("None received from odd")
                            break

                        data = orjson.loads(msg)
                        if isinstance(data, dict) and 'last_delay_100avg' in data.keys():
                            logger.info(f"PING = {data}")
                            if data['last_delay_100avg'] > 100:
                                logger.warning("Ping exceeded 100ms, reconnecting...")
                                break
                        handler = KoefsHandler(data)
                        await handler.save_message()
                    except asyncio.TimeoutError:
                        logger.warning("Timeout on receiving message. Reconnecting...")
                        break
                    except ConnectionClosedError as e:
                        logger.warning(f"Connection closed with error: {e}. Reconnecting...")
                        break
                    except ConnectionResetError as e:
                        logger.warning(f"Connection reset error: {e}. Reconnecting...")
                        break
                    except websockets.ConnectionClosedOK:
                        logger.info("Connection closed normally. Reconnecting...")
                        break
                    except InvalidMessage as e:
                        logger.error(f"Invalid message received: {e}. Reconnecting...")
                        break
                    except Exception as e:
                        logger.error(f"Unexpected error: {e}")
                        break

                    try:
                        handler = KoefsHandler(data)
                        await handler.save_message()
                    except Exception as e:
                        logger.error(f"Error saving {msg}", exc_info=e)
        except Exception as e:
            logger.error(f"ERROR ERROR ERROR ERROR " , exc_info=e)
        await asyncio.sleep(5)
        logger.info("Websocket connection reloaded")
