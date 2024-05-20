import os
from redis import asyncio as aioredis

from dotenv import load_dotenv

load_dotenv()

odd_token = os.environ.get("ODD_TOKEN")
rd = aioredis.from_url("redis://localhost")
