#!/bin/python3

#Importing modules
from flask import Flask
import mysql.connector

#Initializing app
app = Flask(__name__)

@app.route('/')
def index():
	return "Connected"

@app.route('/health')
def health_check():
	try:
		connection=mysql.connector.connect(
		user='root', password='root', host='mysql', port="3306", database='db')
		print("DB connected")
		
		connection.close()
		return 'OK', 200
	except:
		return 'failure', 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
