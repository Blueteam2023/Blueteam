from flask import Flask, request, Response
import sqlQueries
from http import HTTPStatus
from datetime import datetime
import json
import csv
UNIT_CHECK = ""
DIRECTION_CHECK = ""
NOT_EXIST = 0

app = Flask(__name__)


def calculateNeto(bruto, containers_weight, truckTara, unit):
    if containers_weight == "na" or truckTara == "na":
        return 0

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


def get_weight_containers(containers):
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


@app.route("/weight", methods=["POST", "GET"])
def post_weight():
    if request.method == "GET":
        start = request.args.get("start")
        end = request.args.get("end")
        direct = request.args.get("direct")
        return get_weight(start, end, direct)
    
    id = 0
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = ''
    direction = request.args.get('direction')
    truck = str(request.args.get('truck'))
    containers = str(request.args.get('containers'))
    weight = request.args.get('weight')
    unit = request.args.get('unit')
    force = request.args.get('force')
    produce = request.args.get('produce')
      
    
    # handle wrong insertions
    if type(direction) != str or direction.lower() != "in" and direction.lower() != "out" and direction.lower() != "none":
        body = "Direction must be in/out/none\n"
    if not weight.isdigit():
        body += "Weight must be positive integer.\n"
    if not isinstance(unit,str) or unit.lower() != "kg" and unit.lower() != "lbs":
        body += "Unit value must be Kg/Lbs\n"
    if not isinstance(force,str) or force.lower() != 'true' and force.lower() != 'false':
        body += "Force value must be True/False\n"
    if not isinstance(produce,str):
        body += "Produce must be letters string\n"
    if body != '':
        return Response(response=body, status=HTTPStatus.BAD_REQUEST)
    force = force.lower()
    unit = unit.lower()
    
    weight_data = {"datetime": timestamp, "direction": direction, "truck": truck,
                   "containers": containers, "bruto": weight, "truckTara": -1, "neto": -1, "produce": produce}
    retr_val = {"id": id, "truck": truck, "bruto": weight}

    last_transaction = sqlQueries.get_last_transaction_by_truck(truck)
    match direction:

        case "in":
            if not last_transaction:
                id = sqlQueries.insert_transaction(weight_data)
                retr_val["id"] = id
                return Response(response=json.dumps(retr_val), status=HTTPStatus.OK)

            match last_transaction["direction"]:

                case "in":
                    if force == 'true':
                        sqlQueries.change_transaction(weight_data)
                        retr_val["id"] = last_transaction["id"]
                        return Response(response=json.dumps(retr_val), status=HTTPStatus.OK)
                    body = "Truck already in. To override current 'in', request with force=True"
                    return Response(response=body, status=HTTPStatus.BAD_REQUEST)

                case "out":
                    id = sqlQueries.insert_transaction(weight_data)
                    retr_val["id"] = id
                    return Response(response=json.dumps(retr_val), status=HTTPStatus.OK)

        case "out":

            if not last_transaction:
                return Response(response="Truck has not been weighed yet", status=HTTPStatus.BAD_REQUEST)

            truckTara = weight
            containers_weight = get_weight_containers(
                last_transaction["containers"].split(","))
            neto = calculateNeto(
                last_transaction["bruto"], containers_weight, truckTara, unit)
            retr_val += {"truckTara": truckTara, "neto": neto}

            match last_transaction["direction"]:

                case "in":
                    id = sqlQueries.insert_transaction(weight_data)
                    retr_val["id"] = id
                    return json.dumps(retr_val)

                case "out":
                    if force == 'true':
                        sqlQueries.change_transaction(weight_data)
                        retr_val["id"] = last_transaction["id"]
                        return json.dumps(retr_val)
                    return "ERROR: 404 truck cannot get out if not inside to override last transaction change force to true."

                case "none":
                    return "ERROR: 404 container id recognized, containers can not have in/out directions"

        case "none":
            if not last_transaction:
                # id = sqlQueries.insert_transaction(weight_data)
                sqlQueries.register_container(id, weight, unit)
                retr_val["id"] = id
                return json.dumps(retr_val)

            elif last_transaction["direction"] == "none" and force == 'true':
                sqlQueries.change_transaction(weight_data)
                # sqlQueries.change_container(weight_data)
                return json.dumps(retr_val)

            else:
                return "Error: 404 container already registerd OR truck id was entered, trucks direction cannot be none"


@app.route("/batch-weight", methods=["POST"])
def post_batch_weight():
    raise NotImplementedError


@app.route("/unknown", methods=["GET"])
def get_unknown():
    raise NotImplementedError


def get_weight(start, end, direct):
    start_date = None
    end_date = None
    try:
        parsed_start = datetime.strptime(start, "%Y%m%d%H%M%S")
        parsed_end = datetime.strptime(end, "%Y%m%d%H%M%S")
        if parsed_end > parsed_start:
            start_date = str(parsed_start)
            end_date = str(parsed_end)
    finally:
        if not start_date:
            start_date = str(datetime.today().strftime("%Y-%m-%d 00:00:00"))
        if not end_date:
            end_date = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if not direct:
            direct = ""
        directions_list = direct.split(',')
        directions_used = []
        if "in" in directions_list:
            directions_used.append("in")
        if "out" in directions_list:
            directions_used.append("out")
        if "none" in directions_list:
            directions_used.append("none")
        if not directions_used:
            directions_used = ["in", "out", "none"]

        result = sqlQueries.get_transaction_range_by_dates_and_directions(
            start_date, end_date, directions_used)
        return Response(response=json.dumps(result), status=HTTPStatus.OK)
@app.route("/item/<id>", methods=["GET"])
def get_item():
    raise NotImplementedError


@app.route("/session/<id>", methods=["GET"])
def get_session():
    raise NotImplementedError


@app.route("/health", methods=["GET"])
def get_health():
    return Response(status=HTTPStatus.OK)


if __name__ == "__main__":
    app.run(debug=True)
