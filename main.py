from environs import Env
from login import SignIn
from bs4 import BeautifulSoup


def load_config(path: str = None):
    env = Env()
    env.read_env(path)
    data = {
        'barcode': env.str("BARCODE"),
        'password': env.str("PASSWORD")
    }
    return data


def main():
    data = load_config(".env")
    signin = SignIn(data)
    src = signin.login_moodle()
    soup = BeautifulSoup(src, 'lxml')
    text = soup.find_all('a')
    for el in text:
        if el.get('data-parent-key') == 'mycourses':
            print(f"ID of subject - {el.get('data-key')}")
            print(f"Link - {el.get('href')}")


if __name__ == '__main__':
    main()
