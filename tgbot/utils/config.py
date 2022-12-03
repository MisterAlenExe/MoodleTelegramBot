from environs import Env


def load_config():
    env = Env()
    env.read_env(".env")
    data = {
        'bot_token': env.str("BOT_TOKEN")
    }
    return data
