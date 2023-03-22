from flask import Flask, render_template, request
from mysql.connector import connect
from http import HTTPStatus
import datetime
import sqlQueries
import json
import csv
import re
UNIT_CHECK = ""
DIRECTION_CHECK = ""
NOT_EXIST = 0
app = Flask(__name__)


def calculateNeto(bruto, containers_weight, truckTara, unit):
    if containers_weight == "na" or truckTara == "na":
        return "na"

    neto = bruto - containers_weight - truckTara
    return neto


def sumContainerWeight(cont1, cont2, cont3, cont4, unit1, unit2, unit3):
    if unit1 == "lbs":
        cont1 *= 2.2
    if unit2 == "lbs":
        cont2 *= 2.2
    if unit3 == "lbs":
        cont3 *= 2.2

    sum = cont1+cont2+cont3+cont4
    return sum


def getWeightContainers(containers):
    unfound_containers = containers
    containers_weight4 = 0
    db_containers = sqlQueries.get_containers_by_id(unfound_containers)
    if db_containers:
        for cont in db_containers:
            w = cont["weight"]
            if cont["unit"] == "lbs":
                w *= 2.2
            containers_weight4 += w
            unfound_containers.remove(cont["container_id"])

    if unfound_containers:
        with open(r'in/containers1.csv', 'r') as f1, open(r"in/containers2.csv", 'r') as f2, open(r'in/containers3.json', 'r') as f3:
            unit1 = f1.readline().split(",")[1]
            unit2 = f2.readline().split(",")[1]

            data1 = csv.reader(f1)
            data2 = csv.reader(f2)
            data3 = json.load(f3)

            unit3 = data3[0]["unit"]

            containers_weight1 = 0
            containers_weight2 = 0
            containers_weight3 = 0

            for container1, container2, container3 in zip(data1, data2, data3):
                if container1[0] in containers:
                    containers_weight1 += container1[1]
                    unfound_containers.remove(container1[0])

                if container2[0] in containers:
                    containers_weight2 += container2[1]
                    unfound_containers.remove(container2[0])

                if container3["id"] in containers:
                    containers_weight3 += container3["weight"]
                    unfound_containers.remove(container3["id"])

        if unfound_containers:
            return "na"
        else:
            cont_sum = sumContainerWeight(
                containers_weight1, containers_weight2, containers_weight3, containers_weight4, unit1, unit2, unit3)
            return cont_sum
    else:
        return containers_weight4


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/weight", methods=["POST"])
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

    weight_data = {"datetime": timestamp, "direction": direction, "truck": truck,
                   "containers": containers, "bruto": weight, "truckTara": "na", "neto": "na", "produce": produce}

    retr_val = {"id": id, "truck": truck, "bruto": weight}
    last_transaction = sqlQueries.get_last_transaction_by_truck(truck)

    match direction:

        case "in":
            if last_transaction == NOT_EXIST:
                id = sqlQueries.insert_transaction(weight_data)
                retr_val["id"] = id
<<<<<<< HEAD
                return json.dump(retr_val)

=======
                return json.dumps(retr_val)   
            
>>>>>>> 69a30cb (dump to dumps)
            match last_transaction["direction"]:

                case "in":
                    if force == True:
                        sqlQueries.change_transaction(weight_data)
                        retr_val["id"] = last_transaction["id"]
                        return json.dumps(retr_val)
                    return "ERROR: 404 truck cannot get in while inside to override last transaction change force to true."

                case "out":
                    id = sqlQueries.insert_transaction(weight_data)
                    retr_val["id"] = id
<<<<<<< HEAD
                    return json.dump(retr_val)

=======
                    return json.dumps(retr_val)
                
>>>>>>> 69a30cb (dump to dumps)
                case "none":
                    return "ERROR: 404 Truck id recognized as registered container id"

        case "out":

            if last_transaction == NOT_EXIST:
                return "ERROR: 404 Truck not exist"

            truckTara = weight
            containers_weight = getWeightContainers(containers)
            neto = calculateNeto(
                last_transaction["bruto"], containers_weight, truckTara, unit)
            retr_val += {"truckTara": truckTara, "neto": neto}

            match last_transaction["direction"]:

                case "in":
                    id = sqlQueries.insert_transaction(weight_data)
                    retr_val["id"] = id
<<<<<<< HEAD
                    return json.dump(retr_val)

=======
                    return json.dumps(retr_val)
                
>>>>>>> 69a30cb (dump to dumps)
                case "out":
                    if force == True:
                        sqlQueries.change_transaction(weight_data)
                        retr_val["id"] = last_transaction["id"]
                        return json.dumps(retr_val)
                    return "ERROR: 404 truck cannot get out if not inside to override last transaction change force to true."

                case "none":
                    return "ERROR: 404 container id recognized, containers can not have in/out directions"

        case "none":
<<<<<<< HEAD
            if last_transaction == NOT_EXIST:
                id = sqlQueries.insert_transaction(weight_data)
                sqlQueries.register_container()
                retr_val["id"] = id
                return json.dump(retr_val)

            elif last_transaction["direction"] == "none" and force == True:
                sqlQueries.change_transaction(weight_data)
                # sqlQueries.change_container(weight_data)
                return json.dumps(retr_val)

            else:
                return "Error: 404 container already registerd OR truck id was entered, trucks direction cannot be none"


@app.route("/batch-weight", methods=["POST"])
=======
                if last_transaction == NOT_EXIST:
                    id = sqlQueries.insert_transaction(weight_data)
                    sqlQueries.register_container()
                    retr_val["id"] = id
                    return json.dumps(retr_val)
                
                elif last_transaction["direction"] == "none" and force == True:
                    sqlQueries.change_transaction(weight_data)
                    #sqlQueries.change_container(weight_data)
                    return json.dumps(retr_val)
                
                else:
                    return "Error: 404 container already registerd OR truck id was entered, trucks direction cannot be none"


@app.route("/batch-weight",methods=["POST"])
>>>>>>> 69a30cb (dump to dumps)
def batchWeight():
    raise NotImplementedError


@app.route("/unknown", methods=["GET"])
def unknown():
    return True


@app.route("/weight/<start>/<end>/<directed>", methods=["GET"])
def Gweight(start, end, direct):

    pattern = r"\d{14}"
    if re.match(pattern, start) and re.match(pattern, end):
        if (datetime.datetime.strptime(end, "%Y%m%d%H%M%S")) > (datetime.datetime.strptime(start, "%Y%m%d%H%M%S")):
            start_date = datetime.datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
            end_date = datetime.datetime.strftime(end, "%Y-%m-%d %H:%M:%S")
    else:
        print("error with the dates provided, will show all results of the current day ")
        start_date = datetime.datetime.strftime("%Y-%m-%d 00:00:00")
        end_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    are_directions = 0
    directions = ["in", "out", "none"]
    if not "in" in direct:
        directions.remove("in")
        are_directions += 1
    if not "out" in direct:
        directions.remove("out")
        are_directions += 1
    if not "none" in direct:
        directions.remove("none")
<<<<<<< HEAD
        are_directions += 1
    if (not directions) or (are_directions == 3):
        directions = ["in", "out", "none"]

    get_weight = sqlQueries.get_transactions_range_by_date_and_directions(
        start_date, end_date, directions)
    response = jsonify(get_weight)
    # response.status_code = 200
=======
        are_directions +=1
    if (not directions) or (are_directions ==3): 
        directions=["in","out","none"]
        
          
    get_weight = sqlQueries.get_transaction_range_by_dates_and_directions(start_date, end_date, directions)
    response = json.dumps(get_weight)
    #response.status_code = 200
>>>>>>> 69a30cb (dump to dumps)
    return response


@app.route("/item/<id>", methods=["GET"])
def item():
    return True


@app.route("/session/<id>", methods=["GET"])
def session():
    return True


@app.route("/health", methods=["GET"])
def health():
    raise NotImplementedError


if __name__ == "__main__":

    app.run(debug=True)
