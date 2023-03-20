FROM python:3.10-alpine
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN apk add --update docker openrc
ENTRYPOINT [ "python","app.py" ]