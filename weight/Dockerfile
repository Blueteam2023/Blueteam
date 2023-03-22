FROM python:3.10-alpine

WORKDIR /code
ENV FLASK_APP=weight.py
ENV FLASK_RUN_HOST=0.0.0.0

RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt ./
RUN pip install -r requirements.txt


EXPOSE 5000
COPY weight.py sqlQueries.py ./
COPY in ./
