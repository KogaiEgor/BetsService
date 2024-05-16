from fastapi import FastAPI
from src.logger import setup_logging
from src.parser.oddscorp_arbs import get_surebet_pari


app = FastAPI(
    title="BetsService"
)

logger = setup_logging()

@app.get("/arbs/")
async def get_arb():
    arb = await get_surebet_pari("soccer")
    return arb



