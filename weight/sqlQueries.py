from typing import Any
from mysql.connector import connect
from os import environ

config = {
    "host": environ['MYSQL_HOST'],
    "user": environ['MYSQL_USER'],
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
            query = (f"FROM transactions SELECT * WHERE truck_id = '{truck_id}'"
                     "ORDER BY id DESC")
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
    query = ("UPDATE transactions"
             "SET")
    if "datetime" in values:
        query += f", datetime = '{values['datetime']}'"
    if "bruto" in values:
        query += f", bruto = {values['bruto']}"
    if "truck_tara" in values:
        query += f", bruto = {values['truck_tara']}"
    if "neto" in values:
        query += f", bruto = {values['neto']}"
    if "truck" in values:
        if "containers" in values:
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
    raise NotImplementedError


def get_containers_by_id(ids: list[str]):
    cnx = connect(**config)
    if cnx.is_connected():
        cursor = cnx.cursor(dictionary=True)
        result = []
        try:
            for id in ids:
                cursor.execute(
                    f"SELECT * FROM containers_registered WHERE container_id == '{id}'")
                result.append(cursor.fetchone())
            return result
        except:
            print("err")
            # TODO: handle errors
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()


def register_container(id: str, weight, int, unit: str):
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
    directions_query = f"direction == '{directions[0]}'"
    if len(directions) > 1:
        for direction in directions:
            directions_query += f" OR direction == '{direction}'"
    query = f"SELECT * FROM transactions WHERE datetime >= '{start_date}' AND datetime <= '{end_date}' AND ({directions_query})"
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
