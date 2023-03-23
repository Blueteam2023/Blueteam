from typing import Any
from mysql.connector import connect
from os import environ

config = {
    "host": environ['MYSQL_HOST'],
    "user": "root",
    "password": environ['MYSQL_ROOT_PASSWORD'],
    "database": environ['MYSQL_DB_NAME'],
    "port": 3306
}

# For Yuval


def get_last_transaction_by_truck(truck_id: str):
    cnx = connect(**config)
    if cnx.is_connected():
        cursor = cnx.cursor(dictionary=True)
        try:
            query = (f"SELECT * FROM transactions WHERE truck_id = '{truck_id}'"
                     "AND direction = 'in' ORDER BY id DESC LIMIT 1")
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
             "SET")
    if "datetime" in values:
        query += f" datetime = '{values['datetime']}'"
        first_entry = False
    if "bruto" in values:
        if not first_entry:
            query += ","
        else:
            first_entry = False
        query += f" bruto = {values['bruto']}"
    if "truck_tara" in values:
        if not first_entry:
            query += ","
        else:
            first_entry = False
        query += f", bruto = {values['truck_tara']}"
    if "neto" in values:
        if not first_entry:
            query += ","
        else:
            first_entry = False
        query += f", bruto = {values['neto']}"
    if "truck" in values:
        if "containers" in values:
            if not first_entry:
                query += ","
            else:
                first_entry = False
            query += " conainers = "
            for container in values["containers"]:
                query += f" '{container}'"
        query += (f", truck == {values['truck']}"
                  " ORDER BY id DESC"
                  " LIMIT 1")
    else:
        query += (f", containers = {values['containers[0]']}"
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
            return result['id']
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
                result.append(cursor.fetchone())
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
        for direction in directions:
            directions_query += f" OR direction = '{direction}'"
    query = (f"SELECT * FROM transactions WHERE datetime >= '{start_date}' AND"
             f" datetime <= '{end_date}' AND direction = {directions_query}")
    if cnx.is_connected():
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except:
            print("err")
            # TODO: handle errors
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()
