from flask import Flask, render_template,request
from mysql.connector import connect
from http import HTTPStatus
import datetime
import sqlQueries
import json
import csv
UNIT_CHECK=""
DIRECTION_CHECK = ""

app = Flask(__name__)

def calculateNeto(bruto,containers_weight1,containers_weight2,truckTara,unit):
    if containers_weight1 == "na" or containers_weight2 == "na":
        return "na"
    elif unit == "kg":
        if containers_weight1[1] == "lbs":
            containers_weight1[0] *= 2.2
        if containers_weight2[1] == "lbs":
            containers_weight2[0] *= 2.2
    elif unit == "lbs":
        if containers_weight1[1] == "kg":
            containers_weight1[0] /= 2.2
        if containers_weight2[1] == "kg":
            containers_weight2[0] /= 2.2

    neto = bruto - containers_weight1 - containers_weight2 - truckTara
    return neto

def getWeightContainers(containers):
    with open(r'in/containers1.json','r') as f1, open(r"in/containers2.json",'r') as f2:
        unit1 = f1.readline().split(",")[1]
        unit2 = f2.readline().split(",")[1]
        data1=csv.reader(f1)
        data2=csv.reader(f2)
        containers_weight1 = 0
        containers_weight2 = 0
        cont_num = len(containers)
        check = 0
        for container1,container2 in zip(data1,data2):
            if container1[0] in containers:
                containers_weight1 += container1[1]
                check_len += 1
            if container2[0] in containers:
                containers_weight2 += container2[1]
                check_len += 1
    if check == cont_num:
        return [containers_weight1,unit1],[containers_weight2,unit2]
    else:
        return "na","na"


def getTaraTruck(truckid):
  with open(r'in/containers3.json','r') as f:
    data=json.load(f) 
    for truck in data.values():
        if truckid == truck["id"]:
            return truck["weight"]
    return "na"

@app.route("/",methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/weight",methods=["POST"])
def weight():
    
    id = 0
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    direction = request.args.get('direction')
    truck = request.args.get('truck')
    containers = request.args.get('containers').split(",")
    weight = request.args.get('weight')
    unit = request.args.get('unit')
    force = request.args.get('force')
    produce = request.args.get('produce')
    
    
    truckTara = getTaraTruck(truck)
    weight_data = {"datetime":timestamp,"direction":direction,"truck":truck,"containers":containers,"bruto":weight,"truckTara":truckTara,"neto":"na","produce":produce}
    
    retr_val = {"id":id,"truck":truck,"bruto":weight}
    last_transaction = sqlQueries.get_last_transaction_by_truck(truck)

    match direction:
        case "in":    
            if last_transaction["direction"] == "in" and force == True:
                id = sqlQueries.change_transaction(weight_data)
                retr_val["id"] = last_transaction["id"]
                return retr_val
            elif last_transaction['direction'] == "out":
                id = sqlQueries.insert_transaction(weight_data)
                retr_val["id"] = id
                return retr_val
            elif last_transaction == "none":
                #insert data ti containers registerd
                id = sqlQueries.insert_transaction(weight_data)
                retr_val["id"] = id
                return retr_val
            return "ERROR: 404 truck cannot get in while inside to override last transaction change force to true."
            
        case "out":
            if last_transaction == "none":
                return "ERROR: 404 container id recognized, containers cant have in/out directions"
            
            containers_weight1,containers_weight2 = getWeightContainers(containers)
            neto = calculateNeto(last_transaction["bruto"],containers_weight1,containers_weight2,truckTara,unit)
            retr_val += {"truckTara":truckTara,"neto":neto}
            
            if last_transaction["direction"] == "in":
                id = sqlQueries.insert_transaction(weight_data)
                retr_val["id"] = id
                return retr_val
            
            elif last_transaction["direction"] == "out" and force == True:
                id = sqlQueries.change_transaction(weight_data)
                retr_val["id"] = last_transaction["id"]
                return retr_val
            return "ERROR: 404 truck cannot get out if not inside to override last transaction change force to true."
        
        
        case "none":
                if last_transaction == "none":
                    #id = sqlQueries.register_container()
                    retr_val["id"] = id
                    return retr_val
                else:
                    return "Error: 404 container already registerd OR truck id was entered, trucks direction cannot be none"


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