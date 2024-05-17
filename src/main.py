import asyncio
from fastapi import FastAPI
from redis import asyncio as aioredis

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from src.logger import setup_logging
from src.parser.oddscorp_arbs import get_surebet, get_surebet_pari


app = FastAPI(
    title="BetsService"
)

logger = setup_logging()

async def get_surebettest():
    # Здесь будет ваш код для получения данных surebet
    return "result", "bet_type", "link", 1.5, 2.5, "bet_id", "mirror_res", "match_name"


@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fast-api cache")
    asyncio.create_task(cache_arbs())


async def cache_arbs():
    while True:
        result, bet_type, link, koef, koef2, bet_id, mirror_res, match_name = await get_surebettest()
        logger.info(f"Data: {result, bet_type, link, koef, koef2, bet_id, mirror_res, match_name}")

        @cache(expire=60)
        async def index():
            logger.debug("Saving arb to cache")
            return dict(result=result, bet_type=bet_type, link=link,
                        koef=koef, koef2=koef2, bet_id=bet_id,
                        mirror_res=mirror_res, match_name=match_name)

        await index()
        await asyncio.sleep(3)


@app.get("/arbs/")
async def get_arb():
    arb = await get_surebet_pari("soccer")
    return arb



