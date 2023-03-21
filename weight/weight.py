from flask import Flask, render_template,request
from mysql.connector import connect
from http import HTTPStatus
import re
import os

UNIT_CHECK=""
DIRECTION_CHECK = ""

app = Flask(__name__)

config = {
'host' : os.environ['MYSQL_HOST'],
'user': os.environ['MYSQL_USER'],
'password' : os.environ['MYSQL_ROOT_PASSWORD'],
'database' : os.environ['MYSQL_DB_NAME'],
'port':3306
# 'host' :'localhost',
# 'user': 'root',
# 'password':'12345',
# 'database':'weight',
}


@app.route("/",methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/weight",methods=["POST"])
def weight():
    connection = connect(**config)
    cursor = connection.cursor()
    
    sql_last_id = "SELECT id FROM transactions ORDER BY id DESC LIMIT 1"
    last_id = cursor.execute(sql_last_id)
    print(cursor.fetchall())
    
    
    direction = request.args.get('direction')
    truck = request.args.get('truck')
    containers = request.args.get('containers').split(",")
    weight = request.args.get('weight')
    unit = request.args.get('unit')
    force = request.args.get('force')
    produce = request.args.get('produce')

    sql_get_transactions = f"SELECT * FROM transactions WHERE truck={truck}"
    cursor.execute(sql_get_transactions)

    pre_data_weight = {"id":"",
                       "datetime":"",
                       "direction":"none",
                       "truck":"na",
                       "containers":[],
                       "bruto":0,
                       "truckTara":0,
                       "neto":0,
                       "produce":""}



    match direction:
        case "in":
            new_id = last_id+1
            if pre_data_weight["direction"] == "out":
                retr_val = {"id":new_id,"truck":truck,"bruto":weight}
                # insert values into database
                return retr_val
            else:
                return "ERROR: direction must be in if truck is not inside."
            
        case "out":
            if pre_data_weight["direction"] == "in":
                neto = weight - pre_data_weight["truckTara"]
                retr_val = {"id":"out","truck":truck,"bruto":weight,"neto":neto,"truckTara":pre_data_weight["truckTara"]}
                # insert values into database
                return retr_val
            else:
                return "ERROR: direction must be out after in."
            
        case "none":
                new_id = last_id+1
                retr_val = {"id":new_id,"truck":truck,"bruto":weight}
                return retr_val


@app.route("/batch-weight",methods=["POST"])
def batchWeight():
    raise NotImplementedError

@app.route("/unknown",methods=["GET"])
def unknown():
    raise NotImplementedError

@app.route("/weight",methods=["GET"])
def Pweight():
    return render_template("index.html")

@app.route("/item/<id>",methods=["GET"])
def item():
    raise NotImplementedError

@app.route("/session/<id>",methods=["GET"])
def session():
    raise NotImplementedError

@app.route("/health",methods=["GET"])
def health():
    raise NotImplementedError

    
if __name__ == "__main__":

    app.run(debug=True)