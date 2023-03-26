FROM python:slim

RUN pip install --upgrade pip
RUN pip install mysql-connector-python \
	&& pip install flask 
RUN pip install openpyxl 
RUN pip install pandas

WORKDIR /usr/app/src

COPY . .
