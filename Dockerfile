FROM python:3.10

WORKDIR /moodle-tg-bot
COPY requirements.txt requirements.txt

RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt

RUN apt update

RUN apt-get install -y chromium-driver

RUN chmod 755 .
COPY . .
CMD ["python", "main.py"]