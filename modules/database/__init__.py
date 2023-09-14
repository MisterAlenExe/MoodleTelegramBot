import json
import aioredis
from aioredis.client import Redis


redis: Redis = None
redis1: Redis = None


async def start_redis(passwd: str):
    global redis
    redis = await aioredis.from_url(f"redis://redis", password=passwd, decode_responses=True)


async def close_redis():
    await redis.close()


async def get_all_users():
    return await redis.keys()


async def set_key(name: str, key: str, value):
    await redis.hset(name, key, value)


async def get_key(name: str, key: str):
    return await redis.hget(name, key)


async def set_keys(name: str, dict: dict):
    await redis.hmset(name, dict)


async def get_keys(name: str, *keys) -> tuple:
    return await redis.hmget(name, *keys)


async def get_dict(name: str) -> dict:
    return await redis.hgetall(name)


async def if_user_exists(user_id: str):
    if await redis.exists(user_id):
        return True
    else:
        return False


async def add_new_user(user_id: str):
    new_user = {
        "user_id": user_id,
    }
    await set_keys(user_id, new_user)


async def register_moodle_user(
    user_id: str,
    barcode: str,
    moodle_userid: str,
    token: str,
):
    user = {
        "barcode": barcode,
        "moodle_userid": moodle_userid,
        "token": crypt(token, barcode),
    }
    await set_keys(user_id, user)


async def get_user_data(user_id: str):
    moodle_userid = await get_key(user_id, "moodle_userid")
    token = decrypt(await get_key(user_id, "token"), "221900")
    return moodle_userid, token


def crypto(message: str, secret: str) -> str:
    new_chars = list()
    i = 0
    for num_chr in (ord(c) for c in message):
        num_chr ^= ord(secret[i])
        new_chars.append(num_chr)
        i += 1
        if i >= len(secret):
            i = 0
    return "".join(chr(c) for c in new_chars)


def crypt(message: str, secret: str) -> str:
    return crypto(message, secret).encode("utf-8").hex()


def decrypt(message_hex: str, secret: str) -> str:
    message = bytes.fromhex(message_hex).decode("utf-8")
    return crypto(message, secret)
