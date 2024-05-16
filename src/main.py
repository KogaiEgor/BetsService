from fastapi import FastAPI
from src.parser.oddscorp_arbs import get_surebet_pari


app = FastAPI(
    title="BetsService"
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/arbs/")
async def get_arb():
    arb = await get_surebet_pari("soccer")
    return arb



