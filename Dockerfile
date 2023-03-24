FROM python:3.10-alpine
WORKDIR /app
COPY . .
RUN apk update && \
    apk add --no-cache docker-cli git ssmtp curl&& \
    apk add --no-cache --virtual .docker-compose-deps&& \
    pip3 install docker-compose gunicorn && \
    apk del .docker-compose-deps
RUN pip install -r requirements.txt
