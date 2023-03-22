#!/bin/python3

#Importing modules
from flask import Flask, request, render_template
import mysql.connector
import json
import os
import pandas as pd
from os import environ
from flask import send_file
from io import BytesIO


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

@app.route('/rates', methods=["GET", "POST"])
def rates():
    if request.method == "POST":
        # Get the option selected by the user
        option = request.form['option']
        
        if option == 'upload':
        
            # Retrieve the tariff file from the request form
            rate_file = request.files['file'].read()
            excel_file = BytesIO(rate_file)
            df = pd.read_excel(excel_file)
            
            required_columns = ['product_id', 'rate', 'scope']
            if not all(col in df.columns for col in required_columns):
                 raise ValueError(f"Error: the DataFrame must have the columns {required_columns}!")

			# Save the new Excel file to the "/in" directory
            excel_data = BytesIO()
            df.to_excel(excel_data, index=False, sheet_name='Sheet1')
            with open('/in/rates.xlsx', 'wb') as f:
                f.write(excel_data.getbuffer())

            excel_file.close()
            excel_data.close()



            # Connect to the MySQL database
            connection = mysql.connector.connect(
                user=MYSQL_USER,
                password=MYSQL_ROOT_PASSWORD,
                host=MYSQL_HOST,
                port="3306",
                database=MYSQL_DB_NAME
            )

            # Insert the data from the DataFrame into the MySQL database
            cursor = connection.cursor()
            cursor.execute("TRUNCATE TABLE Rates")
            for row in df.itertuples():
                cursor.execute(f"INSERT INTO Rates (product_id, rate, scope) VALUES ('{row.product_id}', '{row.rate}', '{row.scope}')")
            connection.commit()
            cursor.close()
            connection.close()

            return '"The new rates have been successfully uploaded!"'

        elif option == 'download':
            # Send the Excel file stored in the "/in" directory as a download
            return send_file(os.path.join('/in', 'rates.xlsx'), as_attachment=True)

    return render_template('rates.html')

#main
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
