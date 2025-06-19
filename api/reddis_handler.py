import redis
from api.config import settings

r = redis.StrictRedis(host=f"{settings.redis_hostname}", port=settings.redis_port, db=settings.redis_db, decode_responses=True)

def store_refresh_token(user_id : int, token : str, expires_in : int):
    key = f"refresh_token : {user_id}"
    r.setex(key, expires_in, token)

def get(key):
    return r.get(key)

def incr(key):
    return r.incr(key)

def setex(key, time_in_secnds, value):
    return r.setex(key, time_in_secnds, value)

def delete(key):
    return r.delete(key)