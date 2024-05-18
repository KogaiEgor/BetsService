from pydantic import BaseModel


class Bet(BaseModel):
    result: str
    bet_type: str
    link: str
    koef: float
    koef2: float
    bet_id: str
    mirror_res: str
    match_name: str

