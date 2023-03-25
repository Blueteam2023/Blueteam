from flask import Flask, request, Response
import sqlQueries
from http import HTTPStatus
from datetime import datetime
import json
import csv
import re
import os
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'in'
IS_TRUCK = r"^\d+\-\d+\-\d+$"
IS_PRODUCE = r"^[a-zA-Z]+$"
CHECK_JSON_FILE = r'{"id":"[a-zA-Z]\-\d+","weight":\d+,"unit":"\w+"},\n'


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(file):
    check_line = file.readline().decode().strip("\n")
    file.seek(0, 0)
    if file.mimetype == 'text/csv':
        if check_line == '"id","kg"':
            return "containers1.csv"
        if check_line == '"id","lbs"':
            return "containers2.csv"

    if file.mimetype == 'application/json':
        check_line = file.readline()
        check_line = file.readline().decode()
        file.seek(0, 0)
        if re.search(CHECK_JSON_FILE, check_line):

            return "containers3.json"

    return False


def calculateNeto(bruto, containers_weight, truckTara, unit):
    if containers_weight == "na" or truckTara == "na":
        return "na"
    neto = bruto - containers_weight - truckTara
    if unit == "lbs":
        neto *= 2.2
    if neto < 0:
        return "na"
    return int(neto)


def sumContainerWeight(cont1, cont2, cont3, cont4, unit1, unit2, unit3):
    if unit1 == "lbs":
        cont1 /= 2.2
    if unit2 == "lbs":
        cont2 /= 2.2
    if unit3 == "lbs":
        cont3 /= 2.2

    sum = cont1+cont2+cont3+cont4
    return sum


def get_weight_containers(containers):
    unfound_containers = containers
    containers_weight4 = 0
    db_containers = sqlQueries.get_containers_by_id(unfound_containers)
    if db_containers:
        for cont in db_containers:
            w = cont["weight"]
            if w == -1:
                return "na"
            if cont["unit"] == "lbs":
                w *= 2.2
            containers_weight4 += w
            unfound_containers.remove(cont["container_id"])

    if unfound_containers:
        with open(r'in/containers1.csv', 'r') as f1, open(r"in/containers2.csv", 'r') as f2, open(r'in/containers3.json', 'r') as f3:
            unit1 = f1.readline().split(",")[1].strip("\n").strip('"')
            unit2 = f2.readline().split(",")[1].strip("\n").strip('"')

            data1 = csv.reader(f1)
            data2 = csv.reader(f2)
            data3 = json.load(f3)

            unit3 = data3[0]["unit"]

            containers_weight1 = 0
            containers_weight2 = 0
            containers_weight3 = 0

            for container1, container2, container3 in zip(data1, data2, data3):
                if not unfound_containers:
                    break
                if container1[0] in unfound_containers:
                    containers_weight1 += int(container1[1])
                    unfound_containers.remove(container1[0])
                if container2[0] in unfound_containers:
                    containers_weight2 += int(container2[1])
                    unfound_containers.remove(container2[0])
                if container3["id"] in unfound_containers:
                    containers_weight3 += int(container3["weight"])
                    unfound_containers.remove(container3["id"])

        if not unfound_containers:
            cont_sum = sumContainerWeight(
                containers_weight1, containers_weight2, containers_weight3, containers_weight4, unit1, unit2, unit3)
            return cont_sum
        return "na"
    return containers_weight4


@app.route("/")
def index():
    is_healthy = get_health()
    if not is_healthy:
        with open("./templates/error.html") as error:
            doc = ""
            for line in error.readlines():
                doc += line
            return doc
    with open("./templates/index.html") as index:
        doc = ""
        for line in index.readlines():
            doc += line
        return doc


@app.route("/weight", methods=["POST", "GET"])
def post_weight():
    if request.method == "GET":
        start = request.args.get("from")
        end = request.args.get("to")
        direct = request.args.get("filter")
        return get_weight(start, end, direct)

    id = 0
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = ''
    direction = request.form.get('direction')
    truck = str(request.form.get('truck'))
    containers = str(request.form.get('containers'))
    weight = request.form.get('weight')
    unit = request.form.get('unit')
    force = request.form.get('force')
    produce = request.form.get('produce')

    # handle wrong insertions
    if not (re.match(IS_TRUCK, truck) or (truck == "na" and direction.lower() == "none")):
        body = "Truck lisence must be in numbers divided by dashes\n"
    if not direction.lower() in "in,out,none":
        body += "Direction must be in/out/none\n"
    if not weight.isdigit():
        body += "Weight must be positive integer.\n"
    if not unit.lower() in "kg,lbs":
        body += "Unit value must be Kg/Lbs\n"
    if not force.lower() in "true,false":
        body += "Force value must be True/False\n"
    if not re.match(IS_PRODUCE, produce):
        body += "Produce must be letters string"
    if body != '':
        return Response(response=body, status=HTTPStatus.BAD_REQUEST)
    force = force.lower()
    unit = unit.lower()
    weight = int(weight)

    weight_data = {"datetime": timestamp, "direction": direction, "truck": truck,
                   "containers": containers, "bruto": weight, "truckTara": -1, "neto": -1, "produce": produce}
    retr_val = {"id": id, "truck": truck, "bruto": weight}

    last_transaction = sqlQueries.get_last_transaction_by_truck(truck)
    match direction:

        case "in":
            if not last_transaction:
                id = sqlQueries.insert_transaction(weight_data)
                retr_val["id"] = id
                for container in containers.split(','):
                    if get_weight_containers([container]) == "na" and not sqlQueries.get_containers_by_id([container]):
                        sqlQueries.register_container(container, -1, "kg")
                return Response(response=json.dumps(retr_val), status=HTTPStatus.OK)

            match last_transaction["direction"]:

                case "in":
                    if force == 'true':
                        sqlQueries.change_transaction(weight_data)
                        retr_val["id"] = last_transaction["id"]
                        for container in containers.split(','):
                            if get_weight_containers([container]) == "na" and not sqlQueries.get_containers_by_id([container]):
                                sqlQueries.register_container(
                                    container, -1, "kg")
                        return Response(response=json.dumps(retr_val), status=HTTPStatus.OK)
                    body = "Truck already in. To override current 'in', request with force=True"
                    return Response(response=body, status=HTTPStatus.BAD_REQUEST)

                case "out":
                    id = sqlQueries.insert_transaction(weight_data)
                    retr_val["id"] = id
                    return Response(response=json.dumps(retr_val), status=HTTPStatus.OK)

        case "out":

            if not last_transaction:
                body = "Truck has not been weighed yet"
                return Response(response=body, status=HTTPStatus.BAD_REQUEST)
            if containers or produce != "na":
                body = "Truck must be empty while getting out"
                return Response(response=body, status=HTTPStatus.BAD_REQUEST)
            truckTara = weight
            last_in_transaction = sqlQueries.get_last_in_containers_and_bruto_by_truck(
                truck)
            containers_weight = get_weight_containers(
                last_in_transaction["containers"].split(","))
            neto = calculateNeto(
                last_in_transaction["bruto"], containers_weight, truckTara, unit)
            
            weight_data["truckTara"] = truckTara
            weight_data["neto"] = neto if neto != "na" else -1
            retr_val["truckTara"] = truckTara
            retr_val["neto"] = neto

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
                    body = "Truck cannot get out if not inside to override last transaction change force to true."
                    return Response(response=body, status=HTTPStatus.BAD_REQUEST)

        case "none":
            # when a container is registered, we do two things:
            # 1) create a transaction for it
            # 2) if the container is not in containers_registered, registers it
            # otherwise, update the entry
            weight_data["truck"] = "-"
            weight_data["produce"] = "-"
            containers = containers.split(",")
            if len(containers) > 1:
                body = "While registering container only one container is allowed"
                return Response(response=body, status=HTTPStatus.BAD_REQUEST)
            container_id = " ".join(containers)
            last_container = sqlQueries.get_containers_by_id(containers)

            if not last_container:
                id = sqlQueries.insert_transaction(weight_data)
                sqlQueries.register_container(container_id, weight, unit)
                retr_val["id"] = id
                return json.dumps(retr_val)

            if force != 'true':
                body = "Container already registerd. In order to over write container weight request force = True."
                return Response(response=body, status=HTTPStatus.BAD_REQUEST)

            id = sqlQueries.insert_transaction(weight_data)
            sqlQueries.update_container(container_id, weight, unit)
            retr_val["id"] = id
            return json.dumps(retr_val)


@app.route("/batch-weight", methods=["POST"])
def post_batch_weight():
    batch_file = request.files['file']
    if not batch_file:
        body = "No selected file"
        return Response(response=body, status=HTTPStatus.BAD_REQUEST)
    if "json" not in batch_file.mimetype and "csv" not in batch_file.mimetype:
        body = "Illegal format"
        return Response(response=body, status=HTTPStatus.BAD_REQUEST)
    if batch_file and allowed_file(batch_file):
        filename = secure_filename(allowed_file(batch_file))
        batch_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        body = f"File uploaded succefuly. replaced {filename}"
        return Response(response=body, status=HTTPStatus.OK)


@app.route("/unknown", methods=["GET"])
def get_unknown():
    result = sqlQueries.get_container_ids_without_weight()
    return Response(response=json.dumps(result), status=HTTPStatus.OK)


def get_weight(start, end, direct):
    start_date = str(datetime.today().strftime("%Y-%m-%d 00:00:00"))
    end_date = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        parsed_start = datetime.strptime(start, "%Y%m%d%H%M%S")
        parsed_end = datetime.strptime(end, "%Y%m%d%H%M%S")
        if parsed_end > parsed_start:
            start_date = str(parsed_start)
            end_date = str(parsed_end)
    finally:
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


@app.route("/item", methods=["GET"])
def get_item():
    start = request.args.get('from')
    end = request.args.get('to')
    id = request.args.get('id')
    if not id or not start or not end:
        return Response(response="Missing data", status=HTTPStatus.BAD_REQUEST)

    is_truck = re.match(IS_TRUCK, id)
    start_date = str(datetime.today().strftime("%Y-%m-%d 00:00:00"))
    end_date = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        parsed_start = datetime.strptime(start, "%Y%m%d%H%M%S")
        parsed_end = datetime.strptime(end, "%Y%m%d%H%M%S")
        if parsed_end > parsed_start:
            start_date = str(parsed_start)
            end_date = str(parsed_end)
    finally:
        if is_truck:
            transactions = sqlQueries.get_truck_transactions_by_id_and_dates(
                start_date, end_date, id)
            return Response(response=json.dumps(transactions), status=HTTPStatus.OK)

        transactions = sqlQueries.get_container_transactions_by_id_and_dates(
            start_date, end_date, id)
        return Response(response=json.dumps(transactions), status=HTTPStatus.OK)


@app.route("/session/<id>", methods=["GET"])
def get_session(id: str):
    try:
        id_int = int(id)
        result = sqlQueries.get_session_by_id(id_int)
        if not result:
            return Response(response="Id given is not a valid session id", status=HTTPStatus.BAD_REQUEST)
        return Response(response=json.dumps(result), status=HTTPStatus.OK)
    except:
        return Response(response="Id given is not a valid session id", status=HTTPStatus.BAD_REQUEST)


@app.route("/health", methods=["GET"])
def get_health():
    return sqlQueries.health()


def reset_database():
    sqlQueries.reset_database()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
