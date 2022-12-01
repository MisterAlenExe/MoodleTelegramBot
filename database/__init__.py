import json
import aioredis
from aioredis.client import Redis


class Database:
    def __init__(self):
        self.redis = aioredis.from_url(f"redis://localhost", decode_responses=True)

    async def close(self):
        await self.redis.close()

    async def set_key(self, name: str, key: str, value):
        await self.redis.hset(name, key, value)

    async def get_key(self, name: str, key: str):
        return await self.redis.hget(name, key)

    async def set_keys(self, name: str, dict: dict):
        await self.redis.hmset(name, dict)

    async def get_keys(self, name: str, *keys) -> tuple:
        return await self.redis.hmget(name, *keys)

    async def get_dict(self, name: str) -> dict:
        return await self.redis.hgetall(name)
