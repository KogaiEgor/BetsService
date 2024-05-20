import logging
from src.config import rd



logger = logging.getLogger(__name__)
async def validate_data(msg):
    if isinstance(msg, list) and len(msg) > 1 and msg[1] == "update_markets":
        logger.debug(f"Data: {msg[-1]}")
        return msg[-1]

async def cache_koefs(data):
    logger.debug(f"Get data for caching {data}")
    #caching logic
    return data


async def save_message(msg):
    data = await validate_data(msg)
    if data is None:
        return False

    await cache_koefs(data)
    return True
