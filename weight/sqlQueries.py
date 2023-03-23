from typing import Any
from mysql.connector import connect
from os import environ

config = {

    "host": environ['MYSQL_HOST'],
    "user": "root",
    "password": environ['MYSQL_ROOT_PASSWORD'],
    "database": environ['MYSQL_DB_NAME'],
    "port": 3306
    # "host":'localhost',
    # "user":'root',
    # "password":'12345',
    # "database":'weight',
    # "port":3306
}
# For Yuval


def get_last_transaction_by_truck(truck_id: str):
    cnx = connect(**config)
    if cnx.is_connected():
        cursor = cnx.cursor(dictionary=True)
        try:
            query = (f"SELECT * FROM transactions WHERE truck = '{truck_id}'"
                     " AND direction = 'in' ORDER BY id DESC LIMIT 1")
            cursor.execute(query)
            return cursor.fetchone()
        except:
            print("err")
            # TODO: handle errors
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()


def get_last_transaction_by_container(container_id: str):
    cnx = connect(**config)
    if cnx.is_connected():
        cursor = cnx.cursor(dictionary=True)
        try:
            query = (f"SELECT * FROM transactions WHERE containers = '{container_id}'"
                     "AND direction = 'none' ORDER BY id DESC LIMIT 1")

            cursor.execute(query)
            return cursor.fetchone()
        except:
            print("err")
            # TODO: handle errors
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()


def change_transaction(values: dict[str, Any]):
    first_entry = True
    query = ("UPDATE transactions"
             f" SET datetime = '{values['datetime']}', bruto = {values['bruto']}, truckTara = {values['truck_tara']}"
             f" neto = {values['neto']}, truck = {values['truck']}, containers = '{values['containers']}'")
    if values['truck'] != "-":
        query += (f" WHERE truck == {values['truck']}"
                  " ORDER BY id DESC"
                  " LIMIT 1")
    else:
        query += (f" WHERE containers = {values['containers[0]']}"
                  " ORDER BY id DESC"
                  " LIMIT 1")
    cnx = connect(**config)
    if cnx.is_connected():
        cursor = cnx.cursor()
        try:
            cursor.execute(query)
        except:
            print("err")
            # TODO: handle errors
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()


def insert_transaction(values: dict[str, Any]):
    query = ("INSERT INTO transactions (datetime, direction, truck, containers, bruto, truckTara, neto, produce)"
             f" VALUES ('{values['datetime']}', '{values['direction']}', '{values['truck']}', '{values['containers']}',"
             f" {values['bruto']}, {values['truckTara']}, {values['neto']}, '{values['produce']}')")
    cnx = connect(**config)
    if cnx.is_connected():
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute(query)
            cursor.execute(
                "SELECT id FROM transactions ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            return result['id']  # type: ignore
        except:
            print("err")
            # TODO: error handling
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()


def get_containers_by_id(ids: list[str]):
    cnx = connect(**config)
    if cnx.is_connected():
        cursor = cnx.cursor(dictionary=True)
        result = []
        try:
            for id in ids:
                cursor.execute(
                    f"SELECT * FROM containers_registered WHERE container_id = '{id}'")
                container = cursor.fetchone()
                if container:
                    result.append(container)
            return result
        except:
            print("err")
            # TODO: handle errors
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()


def register_container(id: str, weight: int, unit: str):
    cnx = connect(**config)
    if cnx.is_connected():
        cursor = cnx.cursor()
        query = ("INSERT INTO containers_registered (container_id, weight, unit)"
                 f"VALUES ('{id}', {weight}, '{unit}')")
        try:
            cursor.execute(query)
        except:
            print("err")
            # TODO: handle errors
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()


# For Carmen
def get_transaction_range_by_dates_and_directions(start_date: str, end_date: str, directions: list[str]):
    cnx = connect(**config)
    directions_query = f"direction = '{directions[0]}'"
    if len(directions) > 1:
        for index in range(1, len(directions)):
            directions_query += f" OR direction = '{directions[index]}'"
    query = (f"SELECT id, truck, direction, bruto, neto, produce, containers FROM transactions WHERE datetime >= '{start_date}'"
             f" AND datetime <= '{end_date}' AND {directions_query}")
    if cnx.is_connected():
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute(query)
            result = []
            in_entries: dict[str, list[int]] = {}
            # if entry direction is "in" or "none", submit as-is
            # if entry direction is "out", find previous entry with same truck field which has "in" direction
            # and change id to match its id
            for entry in cursor.fetchall():
                if entry["direction"] == "in" or entry["direction"] == "none":  # type: ignore
                    result_entry = {"id": entry["id"],
                                    "direction": entry["direction"],
                                    "bruto": entry["bruto"],
                                    "neto": entry["neto"],
                                    "produce": entry["produce"],
                                    "containers": []}
                    if entry["containers"] != "NULL":
                        for container in entry["containers"].split(','):
                            entry["containers"].append(container)
                    result.append(result_entry)
                    if entry["direction"] == "in":
                        if entry["truck"] in in_entries:
                            in_entries[entry["truck"]].append(entry["id"])
                        else:
                            in_entries[entry["truck"]] = [entry["id"]]
                else:
                    result_entry = {"id": in_entries[entry["truck"][-1]],
                                    "direction": entry["direction"],
                                    "bruto": entry["bruto"],
                                    "neto": entry["neto"],
                                    "produce": entry["produce"],
                                    "containers": []}
            return result
        except:
            print("err")
            # TODO: handle errors
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()


def get_session_by_id(id: int):
    # direction = 'in', session start
    session_start_query = f"SELECT * FROM transactions WHERE id = {id}"
    cnx = connect(**config)
    if cnx.is_connected():
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute(session_start_query)
            session_start = cursor.fetchone()
            is_truck = session_start["truck"] != "-"
            result = {"id": session_start["id"],
                      "truck": "na",
                      "bruto": session_start["bruto"]}
            if not is_truck:
                return result

            session_end_query = (f"SELECT * FROM transactions WHERE id > {id} AND truck = '{session_start['truck']}"
                                 " 'AND direction = 'out' LIMIT 1")
            cursor.execute(session_end_query)
            session_end = cursor.fetchone()
            if not session_end:
                return result
            result["truckTara"] = session_end["truckTara"]
            result["neto"] = session_end["neto"]
            return result
        except:
            print("err")
            # TODO: error logging
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()
