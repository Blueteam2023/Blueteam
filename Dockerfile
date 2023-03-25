FROM python:3.10-alpine

WORKDIR /app
COPY . .

RUN apk update && \
    apk add --no-cache docker-cli git ssmtp curl openssh&& \
    apk add --no-cache --virtual .docker-compose-deps&& \
    pip3 install docker-compose gunicorn && \
    apk del .docker-compose-deps

RUN pip install -r requirements.txt

RUN mkdir -p /root/.ssh
COPY ./id_ed25519 /root/.ssh/


RUN chmod 600 /root/.ssh/id_ed25519 && \
    chown root:root /root/.ssh/id_ed25519

RUN ssh-keyscan github.com >> /root/.ssh/known_hosts


