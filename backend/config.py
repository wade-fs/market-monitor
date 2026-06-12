import os
import redis
import json

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
except Exception:
    redis_client = None

def get_cache(key):
    if not redis_client: return None
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception: return None

def set_cache(key, value, ex=43200): # 12 hours
    if not redis_client: return
    try:
        redis_client.set(key, json.dumps(value), ex=ex)
    except Exception: pass
