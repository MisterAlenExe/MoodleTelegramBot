FROM ubuntu:22.04

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Almaty

COPY requirements.txt .

RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -yqq --no-install-recommends python3 python3-pip wget unzip tzdata && \
    pip3 install -r requirements.txt && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    dpkg-reconfigure --frontend noninteractive tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /moodle-tg-bot
COPY . /moodle-tg-bot

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /moodle-tg-bot
USER appuser

CMD ["python3", "main.py"]