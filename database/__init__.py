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

    async def if_user_exists(self, user_id: str):
        if await self.redis.exists(user_id):
            return True
        else:
            return False

    async def add_new_user(self, user_id: str):
        new_user = {
            'user_id': user_id,
        }
        await self.set_keys(user_id, new_user)

    async def register_moodle_user(self, user_id: str, barcode: str, password: str, cookies: dict, moodle_userid: str,
                                   token: str):
        user = {
            'barcode': barcode,
            'password': crypt(password, barcode),
            'cookies': json.dumps(cookies),
            'moodle_userid': moodle_userid,
            'webservice_token': crypt(token, moodle_userid)
        }
        await self.set_keys(user_id, user)

    async def get_user_data(self, user_id: str):
        barcode = await self.get_key(user_id, 'barcode')
        password = decrypt(await self.get_key(user_id, 'password'), barcode)
        return barcode, password


def crypto(message: str, secret: str) -> str:
    new_chars = list()
    i = 0
    for num_chr in (ord(c) for c in message):
        num_chr ^= ord(secret[i])
        new_chars.append(num_chr)
        i += 1
        if i >= len(secret):
            i = 0
    return ''.join(chr(c) for c in new_chars)


def crypt(message: str, secret: str) -> str:
    return crypto(message, secret).encode('utf-8').hex()


def decrypt(message_hex: str, secret: str) -> str:
    message = bytes.fromhex(message_hex).decode('utf-8')
    return crypto(message, secret)
