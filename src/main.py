import asyncio
from fastapi import FastAPI

from src.logger import setup_logging
from src.config import load_config
from src.market.router import router as router_market
from src.market.oddscorp_websocket import read_odds_socket
from src.bet.service import cache_bet
from src.bet.oddscorp_values import ValuesOddHandler
from src.bet.oddscorp_arbs import ArbsOddHandler
from src.bet.router import router as router_bets


app = FastAPI(
    title="BetsService"
)

logger = setup_logging()
@app.on_event("startup")
async def startup_event():
    load_config()
    asyncio.create_task(cache_bet(ValuesOddHandler))
    asyncio.create_task(cache_bet(ArbsOddHandler))
    asyncio.create_task(read_odds_socket())


app.include_router(router_market)
app.include_router(router_bets)
