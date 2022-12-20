from environs import Env


def load_config():
    env = Env()
    env.read_env(".env")
    data = {
        'BOT_TOKEN': env.str("BOT_TOKEN"),
        'REDIS_PASSWD': env.str("REDIS_PASSWORD")
    }
    return data
