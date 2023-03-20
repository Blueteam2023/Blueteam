#!/bin/python3

from flask import Flask
import mysql.connector


app = Flask(__name__)

@app.route('/health')
def health_check():
	try:
		mydb = mysql.connector.connect(
		host = "0fa8cfcbe42f",
		user = "mysql",
		password = "")
		return 'OK', 200
	except:
		return 'failure', 500
if __name__ == '__main__':
	app.run(debug=True)
