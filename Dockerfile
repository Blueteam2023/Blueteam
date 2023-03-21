FROM python:3.10-alpine
WORKDIR /app
RUN apk update && \
    apk add --no-cache docker-cli git&& \
    apk add --no-cache --virtual .docker-compose-deps&& \
    pip3 install docker-compose && \
    apk del .docker-compose-deps
RUN git clone https://github.com/Blueteam2023/Blueteam.git .
RUN pip install -r requirements.txt
ENTRYPOINT [ "python","app.py" ]