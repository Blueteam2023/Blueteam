#!/bin/python3

#Importing modules
from flask import Flask, request, render_template
import mysql.connector
import json
from os import environ
from datetime import datetime

#Preparing environment variables
MYSQL_USER = environ['ENV_USER']
MYSQL_ROOT_PASSWORD = environ['ENV_ROOT_PASSWORD']
MYSQL_HOST = environ['ENV_HOST']
MYSQL_DB_NAME = environ['ENV_DB_NAME']

#Initializing app
app = Flask(__name__)

@app.route('/')
def index():
	return "Connected"


#Health check API
@app.route('/health')
def health_check():
	try:
		connection=mysql.connector.connect(
		user = MYSQL_USER, password = MYSQL_ROOT_PASSWORD, host = MYSQL_HOST, port = "3306", database = MYSQL_DB_NAME)
		connection.close()
		return 'OK', 200
	except:
		return 'failure', 500


#Provider list API
@app.route('/providerlist')
def plist():
	try:
		connection=mysql.connector.connect(
		user = MYSQL_USER, password = MYSQL_ROOT_PASSWORD, host = MYSQL_HOST, port = "3306", database = MYSQL_DB_NAME)

		cursor=connection.cursor()
		cursor.execute('SELECT * FROM Provider;')
		DB_PROV_LIST=cursor.fetchall()
		#JSON_PROV_LIST=list(json.dumps(DB_PROV_LIST))
		connection.close()
		return DB_PROV_LIST
	except:
		return "listfail"
	
#POST provider API
@app.route('/provider', methods=["GET", "POST"])
def prov():
	if request.method=="GET":	
		return render_template('prov.html')
		
	elif request.method=="POST":	
		
		GIVEN_PROV_NAME = request.form['nm']		
		connection=mysql.connector.connect(
		user = MYSQL_USER, password = MYSQL_ROOT_PASSWORD, host = MYSQL_HOST, port = "3306", database = MYSQL_DB_NAME)
		cursor=connection.cursor()


		cursor.execute("SELECT name FROM Provider where name=(%s)",(GIVEN_PROV_NAME,))
		DB_PROV_NAME=cursor.fetchall()
		PROV_NAME = json.dumps(DB_PROV_NAME)
		
		if PROV_NAME == f'[["{GIVEN_PROV_NAME}"]]':
			cursor.execute("SELECT id FROM Provider where name=(%s)",(GIVEN_PROV_NAME,))
			DB_PROV_ID=cursor.fetchall()
			PROV_ID=json.dumps(DB_PROV_ID[0][0])
			connection.close()
			return f"Error: provider name already exists at ID {PROV_ID}"
		else:
			cursor.execute("INSERT INTO Provider (`name`) VALUES ((%s));",(GIVEN_PROV_NAME,))	
			cursor.execute("SELECT id FROM Provider where name=(%s)",(GIVEN_PROV_NAME,))
			DB_PROV_ID=cursor.fetchall()
			PROV_ID=json.dumps(DB_PROV_ID[0][0])
			connection.close()
			return f"Provider name saved to ID {PROV_ID}"
		


	else:
		return "error"


#PUT provider id API
@app.route('/provider/<id>', methods=["GET", "POST"])
def provid(id):

	if request.method=="GET":	
		return render_template('prov-id.html')
		
	elif request.method=="POST":	
		
		GIVEN_PROV_NAME = request.form['nm']		
		connection=mysql.connector.connect(
		user = MYSQL_USER, password = MYSQL_ROOT_PASSWORD, host = MYSQL_HOST, port = "3306", database = MYSQL_DB_NAME)
		cursor=connection.cursor()

		cursor.execute("SELECT name FROM Provider where name=(%s)",(GIVEN_PROV_NAME,))
		DB_PROV_NAME=cursor.fetchall()
		PROV_NAME = json.dumps(DB_PROV_NAME)
		
		if PROV_NAME == f'[["{GIVEN_PROV_NAME}"]]':
			cursor.execute("SELECT id FROM Provider where name=(%s)",(GIVEN_PROV_NAME,))
			DB_PROV_ID=cursor.fetchall()
			PROV_ID=json.dumps(DB_PROV_ID[0][0])
			connection.close()
			return f"Error: provider name already exists at ID {PROV_ID}"
		elif GIVEN_PROV_NAME == "":
			cursor.execute("DELETE FROM `Provider` WHERE id=(%s);",(id,))
			connection.close()
			return f"Provider deleted from database, id {id} is no longer in use" 
			
		else: 
			cursor.execute("UPDATE Provider set name=(%s) where id=(%s)",(GIVEN_PROV_NAME, id,))
			connection.close()
			return f"New provider name saved to ID {id}"


	else:
		return "error"

		
#GET bill API
@app.route('/bill/<id>')
def bill(id):
	
	FROM_DATE = request.args.get('from', datetime.today().strftime("%Y%m01%H%M%S"))
	TO_DATE = request.args.get('to',datetime.today().strftime("%Y%m%d%H%M%S"))
#	#Billing DB Connection
#	connection=mysql.connector.connect(
#	user = MYSQL_USER, password = MYSQL_ROOT_PASSWORD, host = MYSQL_HOST, port = "3306", database = MYSQL_DB_NAME)
#	cursor=connection.cursor()
#	cursor.execute('SELECT name FROM Provider where id=(%s);',(id,))
#	DB_PROV_LIST=cursor.fetchall()
#	#JSON_PROV_LIST=list(json.dumps(DB_PROV_LIST))
#	connection.close()
#	
#	#Weight DB Connection
#	connection=mysql.connector.connect(
#	user = WEIGHT_USER, password = WEIGHT_ROOT_PASSWORD, host = WEIGHT_HOST, port = "3306", database = WEIGHT_DB_NAME)
#	cursor=connection.cursor()
#	cursor.execute('SELECT name FROM transactions where datetime from (%s) to (%s);',(from, to))
#	DB_PROV_LIST=cursor.fetchall()
#	#JSON_PROV_LIST=list(json.dumps(DB_PROV_LIST))
#	connection.close()
	return f"from={FROM_DATE}, to={TO_DATE}"
	
	
	
	
	
#{
#  "id": <str>,
#  "name": <str>,
#  "from": <str>,
#  "to": <str>,
#  "truckCount": <int>,
#  "sessionCount": <int>,
#  "products": [
#    { "product":<str>,
#      "count": <str>, // number of sessions
#      "amount": <int>, // total kg
#      "rate": <int>, // agorot
#      "pay": <int> // agorot
#    },...
#  ],
#  "total": <int> // agorot
#}
	
	
	
	
#main
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
