FROM python:3.10-alpine
WORKDIR /app
COPY . .
RUN apk update && \
    apk add --no-cache docker-cli git ssmtp&& \
    apk add --no-cache --virtual .docker-compose-deps&& \
    pip3 install docker-compose && \
    apk del .docker-compose-deps
COPY ssmtp.conf /etc/ssmtp/ssmtp.conf
RUN pip install -r requirements.txt
ENTRYPOINT [ "python","app.py" ]