FROM python:latest

RUN pip install mysql-connector-python \
	&& pip install flask

WORKDIR /usr/app/src

COPY app.py ./
