import orjson
import logging
from fastapi import APIRouter, status, Response

from src.config import rd
from src.market.schemas import Market



router = APIRouter(
    prefix="/market",
    tags=["Market"]
)

logger = logging.getLogger(__name__)
@router.get("/update_koefs/", status_code=status.HTTP_200_OK, response_model=Market)
async def update_koefs(match_id: str, market: str, response: Response):
    koefs = await rd.hgetall(match_id)
    decoded_koef = {key.decode('utf-8'): value.decode('utf-8') for key, value in koefs.items()}
    if 'markets' not in decoded_koef.keys():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'msg': f"No match with id {match_id}"}
    markets = orjson.loads(decoded_koef['markets'])
    logger.debug(decoded_koef)
    for i in markets:
        if i[0] == market:
            return Market(**{'market': float(i[2])})
    response.status_code = status.HTTP_400_BAD_REQUEST
    return {'msg': f"No market {market} in match {match_id}"}


