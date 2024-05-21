from fastapi import APIRouter


router = APIRouter(
    prefix="/arbs",
    tags=["Bots"]
)

@router.get("/get_arb/")
async def get_arb():
    return "arb"


