FROM python:slim

RUN pip install --upgrade pip
RUN pip install mysql-connector-python \
	&& pip install flask \
	&& pip install openpyxl \
	&& pip install pandas 


WORKDIR /usr/app/src

COPY . .
