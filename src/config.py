import os
import redis

from dotenv import load_dotenv

load_dotenv()

odd_token = os.environ.get("ODD_TOKEN")
rd = redis.Redis(host='localhost', port=6379, db=0)
