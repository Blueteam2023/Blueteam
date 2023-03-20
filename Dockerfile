FROM python:3.10-alpine
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN apk update && \
    apk add --no-cache docker-cli git&& \
    apk add --no-cache --virtual .docker-compose-deps&& \
    pip3 install docker-compose && \
    apk del .docker-compose-deps
ENTRYPOINT [ "python","app.py" ]