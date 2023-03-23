FROM python:3.10-alpine

WORKDIR /code
ENV FLASK_APP=weight.py
ENV FLASK_RUN_HOST=0.0.0.0

RUN apk add --no-cache gcc musl-dev linux-headers
EXPOSE 5000
COPY in ./in
COPY requirements.txt ./


RUN pip install -r requirements.txt
COPY weight.py sqlQueries.py ./