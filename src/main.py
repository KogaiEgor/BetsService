import asyncio
from fastapi import FastAPI

from src.logger import setup_logging
from src.market.router import router as router_market
from src.market.oddscorp_websocket import read_odds_socket
from src.arbs.router import router as router_arbs
from src.arbs.service import cache_arbs


app = FastAPI(
    title="BetsService"
)

logger = setup_logging()
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cache_arbs())
    asyncio.create_task(read_odds_socket())


app.include_router(router_market)
app.include_router(router_arbs)
