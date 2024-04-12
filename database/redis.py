import redis
from services.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_CACHE_DB
)


def get_redis():
    yield redis_client
