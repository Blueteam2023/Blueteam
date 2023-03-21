#!/bin/python3

#Importing modules
from flask import Flask, request, render_template
import mysql.connector
import json

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
		user='root', password='root', host='mysql', port="3306", database='billdb')
		connection.close()
		return 'OK', 200
	except:
		return 'failure', 500


#Provider list API
@app.route('/providerlist')
def plist():
	try:
		connection=mysql.connector.connect(
		user='root', password='root', host='mysql', port="3306", database='billdb')

		cursor=connection.cursor()
		cursor.execute('SELECT * FROM Provider;')
		provider_list=cursor.fetchall()

		connection.close()
		return provider_list
	except:
		return "listfail"
	
#POST provider API
@app.route('/provider', methods=["GET", "POST"])
def prov():
	if request.method=="GET":	
		return render_template('index.html')
		
	elif request.method=="POST":	
		
		GIVEN_PROV_NAME = request.form['nm']		
		connection=mysql.connector.connect(
		user='root', password='root', host='mysql', port="3306", database='billdb')
		cursor=connection.cursor()


		cursor.execute("SELECT name FROM Provider where name=(%s)",(GIVEN_PROV_NAME,))
		DB_PROV_NAME=cursor.fetchall()	
		json_NAME = json.loads(DB_PROV_NAME)
		
		if json_NAME == GIVEN_PROV_NAME:
			cursor.execute("SELECT id FROM Provider where name=(%s)",(GIVEN_PROV_NAME,))
			DB_PROV_ID=cursor.fetchall()
			return "Error: provider name already exists at ID "
		else:
			cursor.execute("INSERT INTO Provider (`name`) VALUES ((%s));",(GIVEN_PROV_NAME,))	
			cursor.execute("SELECT id FROM Provider where name=(%s)",(GIVEN_PROV_NAME,))
			DB_PROV_ID=cursor.fetchall()			
			return "else"
		connection.close()


	else:
		return "error"


#PUT provider id API
@app.route('/provider<id>')
def provid(id):

#		connection=mysql.connector.connect(
#		user='root', password='root', host='mysql', port="3306", database='db')
#		
#		cursor=connection.cursor()
#		cursor.execute('select * from provider;')
#		provider=cursor.fetchall()
#		
#		connection.close()
	return "provider id"




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=False)
