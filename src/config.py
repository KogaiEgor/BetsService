import os
from redis import asyncio as aioredis

from dotenv import load_dotenv

load_dotenv()

def load_config():
    load_dotenv()

odd_token = os.getenv("ODD_TOKEN")
rd = aioredis.from_url("redis://localhost")
