from environs import Env


def load_config():
    env = Env()
    env.read_env(".env")
    data = {
        'barcode': env.str("BARCODE"),
        'password': env.str("PASSWORD"),
        'user_id': env.str("USER_ID"),
        'webservice_token': env.str("WEBSERVICE_TOKEN"),
        'bot_token': env.str("BOT_TOKEN")
    }
    return data
