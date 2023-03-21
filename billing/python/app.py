#!/bin/python3

#Importing modules
from flask import Flask, request, render_template
import mysql.connector
import json
from os import environ

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
			return f"Error: provider name already exists at ID {PROV_ID}"
		else:
			cursor.execute("INSERT INTO Provider (`name`) VALUES ((%s));",(GIVEN_PROV_NAME,))	
			cursor.execute("SELECT id FROM Provider where name=(%s)",(GIVEN_PROV_NAME,))
			DB_PROV_ID=cursor.fetchall()
			PROV_ID=json.dumps(DB_PROV_ID[0][0])
			return f"Provider name saved to ID {PROV_ID}"
		connection.close()


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
			return f"Error: provider name already exists at ID {PROV_ID}"
		elif GIVEN_PROV_NAME == "":
			cursor.execute("DELETE FROM `Provider` WHERE id=(%s);",(id,))
			return f"Provider deleted from database, id {id} is no longer in use" 
			
		else: 
			cursor.execute("UPDATE Provider set name=(%s) where id=(%s)",(GIVEN_PROV_NAME, id,))
			return f"New provider name saved to ID {id}"
		connection.close()


	else:
		return "error"


#main
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
