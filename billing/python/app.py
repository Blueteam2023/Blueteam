#!/bin/python3

# Importing modules
from flask import Flask, request, render_template
import mysql.connector
import json
from os import environ
from datetime import datetime

# Preparing environment variables
MYSQL_USER = environ['ENV_USER']
MYSQL_ROOT_PASSWORD = environ['ENV_ROOT_PASSWORD']
MYSQL_HOST = environ['ENV_HOST']
MYSQL_DB_NAME = environ['ENV_DB_NAME']
BILLING_MYSQL_PORT = "3306"
#WEIGHT_USER=?
#WEIGHT_ROOT_PASSWORD=?
#WEIGHT_HOST=?
#WEIGHT_PORT=?
#WEIGHT_DB_NAME=?


# Initializing app
app = Flask(__name__)


@app.route('/')
def index():
    return "Connected"


# Health check API
@app.route('/health')
def health_check():

	try:
		connection=mysql.connector.connect(
		user = MYSQL_USER, password = MYSQL_ROOT_PASSWORD, host = MYSQL_HOST, port = BILLING_MYSQL_PORT, database = MYSQL_DB_NAME)
		connection.close()
		return 'OK', 200
	except:
		return 'failure', 500


# Provider list API
@app.route('/providerlist')
def plist():
    try:
        connection = mysql.connector.connect(
            user=MYSQL_USER, password=MYSQL_ROOT_PASSWORD, host=MYSQL_HOST, port=BILLING_MYSQL_PORT, database=MYSQL_DB_NAME)

        cursor = connection.cursor()
        cursor.execute('SELECT * FROM Provider;')
        DB_PROV_LIST = cursor.fetchall()
        # JSON_PROV_LIST=list(json.dumps(DB_PROV_LIST))
        connection.close()
        return DB_PROV_LIST
    except:
        return "listfail"


@app.route('/provider', methods=["GET", "POST"])
def prov():
	if request.method=="GET":	
		return render_template('prov.html')
		
	elif request.method=="POST":	
		
		GIVEN_PROV_NAME = request.form['nm']		
		connection=mysql.connector.connect(
		user = MYSQL_USER, password = MYSQL_ROOT_PASSWORD, host = MYSQL_HOST, port = BILLING_MYSQL_PORT, database = MYSQL_DB_NAME)
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
		user = MYSQL_USER, password = MYSQL_ROOT_PASSWORD, host = MYSQL_HOST, port = BILLING_MYSQL_PORT, database = MYSQL_DB_NAME)
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

# -------------------- start API Trucks -----------------------------------------

@app.route("/truck", methods=["GET", "POST"])
def data_truck():
    if request.method == "GET":
        return render_template('truck.html')

    elif request.method == "POST":
        id = request.form['id']
        provider_id = request.form['provider_id']
        connection = mysql.connector.connect(user="root", password="root", host="billing-mysql", port="3306", database="billdb")
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM Provider where id=(%s)",(int(provider_id),))
        DB_PROV_ID = cursor.fetchall()

        if len(DB_PROV_ID) == 0:
            connection.close()
            return f"Failed: new truck with license plate : {id} can not be add, his provider : {provider_id} does not exist", 500
        else:
            cursor.execute("INSERT INTO Trucks(id, provider_id) VALUES(%s,%s)", (id, provider_id))
            cursor.execute("SELECT id FROM Trucks where id=(%s)", (id,))
            DB_TRUCK_ID = cursor.fetchall()
            connection.close()
            return f"Success: new truck with license plate : {json.dumps(DB_TRUCK_ID[0][0])} has been added", 200



@app.route("/truck/<id>", methods=["PUT"])
def update_truck_license_plate(id):
    data = request.get_json(force=True)
    connection = mysql.connector.connect(user="root", password="root", host="billing-mysql", port="3306", database="billdb")
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM Provider where id=(%s)",(int(data["provider_id"]),))
    PROVIDER_ID = cursor.fetchall()
    if len(PROVIDER_ID) == 0:
        connection.close()
        return { 'message' : f'There is no provider id {data["provider_id"]}'}, 400
    else:
        cursor.execute("SELECT id FROM Trucks where id=(%s)", (id,))
        TRUCK_ID = cursor.fetchall()
        if len(TRUCK_ID) == 0:
            connection.close()
            return { 'message' : f'There is no truck id {id}'}, 400
        else:
            cursor.execute("UPDATE Trucks SET provider_id = (%s) where id=(%s)", (int((data["provider_id"])), id))
            connection.close()
            return { 'message' : f'Truck with license plate {TRUCK_ID[0][0]} has been updated to provider {PROVIDER_ID[0][0]}'}, 200

 # ----  Liste of truck with id -------------


@app.route('/trucklist')
def trucklist():
    try:
        connection = mysql.connector.connect(user=MYSQL_USER, password=MYSQL_ROOT_PASSWORD, host=MYSQL_HOST, port="3306", database=MYSQL_DB_NAME)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM Trucks;')
        DB_PROV_LIST = cursor.fetchall()
        connection.close()
        return DB_PROV_LIST
    except:
        connection.close()
        return "listfail"
		
#GET bill API
@app.route('/bill/<id>')
def bill(id):
	
	FROM_DATE = request.args.get('from', datetime.today().strftime("%Y%m01%H%M%S"))
	TO_DATE = request.args.get('to',datetime.today().strftime("%Y%m%d%H%M%S"))
	
	#Billing DB Connection
	connection=mysql.connector.connect(
	user = MYSQL_USER, password = MYSQL_ROOT_PASSWORD, host = MYSQL_HOST, port = BILLING_MYSQL_PORT, database = MYSQL_DB_NAME)
	cursor=connection.cursor()
	
	#  "name": <str>,
	cursor.execute('SELECT name FROM Provider where id=(%s);',(id,))
	DB_PROV_NAME=cursor.fetchall()
	try:
		PROV_NAME=json.dumps(DB_PROV_LIST[0][0])
	except:
		return "ERROR: Provider not found."
	#  list of trucks
	cursor.execute('SELECT id FROM Trucks where provider_id=(%s);',(id,))
	TRUCK_LIST=cursor.fetchall()
	STR_TRUCK_LIST=json.dumps(TRUCK_LIST)
	
	
		
	connection.close()
	
	#Weight DB Connection
	connection=mysql.connector.connect(
	user = WEIGHT_USER, password = WEIGHT_ROOT_PASSWORD, host = WEIGHT_HOST, port = WEIGHT_PORT, database = WEIGHT_DB_NAME)
	cursor=connection.cursor()
	
	#  "truckCount": <int>,
	cursor.execute('SELECT count(distinct truck) FROM transactions where datetime > (%s) and datetime < (%s);',(FROM_DATE, TO_DATE,))
	DB_TRUCK_COUNT=cursor.fetchall()
	TRUCK_COUNT=json.dumps(DB_TRUCK_COUNT)
	
	#  "sessionCount": <int>,
	cursor.execute('SELECT count(direction) FROM transactions where direction = "out" and datetime > (%s) and datetime < (%s);',(FROM_DATE, TO_DATE,))
	DB_SESSION_COUNT=cursor.fetchall()
	SESSION_COUNT=json.dumps(DB_SESSION_COUNT)
	
	#  "products": 
	cursor.execute('SELECT produce FROM transactions where datetime >= (%s) and datetime <= (%s);',(FROM_DATE, TO_DATE,))
	DB_PRODUCT_LIST=set(cursor.fetchall())
	#PRODUCT_LIST=list(json.dumps(DB_PRODUCT_LIST))
	PRODUCT_INFO=[]
	for var in DB_PRODUCT_LIST:
		cursor.execute('SELECT count(id) where produce = (%s) and datetime >= (%s) and datetime <= (%s)',(var, FROM_DATE, TO_DATE,))
		count=cursor.fetchall()
		cursor.execute('SELECT sum(neto) where produce = (%s) and datetime >= (%s) and datetime <= (%s)',(var, FROM_DATE, TO_DATE,))
		amount=cursor.fetchall()
		
		PRODUCT_INFO.append(f' \
		"product": "{var}" \
		"count": "{count}" \
		"amount": {amount} \
		"rate": {a} \
		"pay": {a}') 
	
		
	connection.close()
	return STR_TRUCK_LIST
	
	#  "total": <int> // agorot
	
	
	
	
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
