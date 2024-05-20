from src.config import rd


async def validate_data(msg):
    pass


async def cache_koefs(data):
    pass


async def save_message(msg):
    data = await validate_data(msg)
    if data is None:
        return

    await cache_koefs(data)
    return
