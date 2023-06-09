from sys import stderr
from typing import Any
from mysql.connector import connect
from os import environ

config = {
    "host": environ['ENV_HOST'],
    "user": environ["ENV_USER"],
    "password": environ['ENV_ROOT_PASSWORD'],
    "database": environ['ENV_DB_NAME'],
    "port": 3306
}
# For Yuval


def reset_database():
    cnx = connect(**config)
    if cnx.is_connected():
        cursor = cnx.cursor()
        try:
            cursor.execute("DROP TABLE transactions")
            cursor.execute("DROP TABLE containers_registered")
            create_containers = ("CREATE TABLE IF NOT EXISTS `containers_registered` ("
                                 "`container_id` varchar(15) NOT NULL,"
                                 "`weight` int(12) DEFAULT NULL,"
                                 "`unit` varchar(10) DEFAULT NULL,"
                                 "  PRIMARY KEY (`container_id`)"
                                 ") ENGINE=MyISAM AUTO_INCREMENT=10001")
            create_transactions = ("CREATE TABLE IF NOT EXISTS `transactions` ("
                                   "`id` int(12) NOT NULL AUTO_INCREMENT,"
                                   "`datetime` datetime DEFAULT NULL,"
                                   "`direction` varchar(10) DEFAULT NULL,"
                                   "`truck` varchar(50) DEFAULT NULL,"
                                   "`containers` varchar(10000) DEFAULT NULL,"
                                   "`bruto` int(12) DEFAULT NULL,"
                                   "`truckTara` int(12) DEFAULT NULL,"
                                   "`neto` int(12) DEFAULT NULL,"
                                   "`produce` varchar(50) DEFAULT NULL,"
                                   "PRIMARY KEY (`id`)"
                                   ") ENGINE=MyISAM AUTO_INCREMENT=10001 ;")
            cursor.execute(create_containers)
            cursor.execute(create_transactions)
        except:
            print("err")
            # TODO: handle errors
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()


def health():
    cnx = connect(**config)
    if cnx.is_connected():
        cursor = cnx.cursor()
        try:
            query = ("SELECT 1")
            cursor.execute(query)
            return "OK", 200
        except:
            return "ERROR", 500


def get_last_in_containers_and_bruto_by_truck(truck_id: str):
    cnx = connect(**config)
    if cnx.is_connected():
        cursor = cnx.cursor(dictionary=True)
        try:
            query = (f"SELECT bruto,containers FROM transactions WHERE truck = '{truck_id}' AND direction = 'in'"
                     " ORDER BY id DESC LIMIT 1")
            cursor.execute(query)
            return cursor.fetchone()
        except:
            print("err")
            # TODO: handle errors
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()


def get_last_transaction_by_truck(truck_id: str):
    cnx = connect(**config)
    if cnx.is_connected():
        cursor = cnx.cursor(dictionary=True)
        try:
            query = (f"SELECT * FROM transactions WHERE truck = '{truck_id}'"
                     " ORDER BY id DESC LIMIT 1")
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
    # two cases; case 1 - force an update on a container session
    # case 2 - force an update on a truck session
    # in the first case - truck = '-'
    # in the second case - truck != '-'
    query_start: str
    if values['truck'] == "-":
        query_start = (f"SELECT id FROM transactions WHERE truck = '-' AND containers = '{values['containers']}'"
                       " ORDER BY id DESC"
                       " LIMIT 1")
    else:
        query_start = (f"SELECT id FROM transactions WHERE truck = '{values['truck']}'"
                       " ORDER BY id DESC"
                       " LIMIT 1")

    cnx = connect(**config)
    if cnx.is_connected():
        cursor = cnx.cursor()
        try:
            cursor.execute(query_start)
            query_id = int(''.join(map(str, cursor.fetchone())))
            update_query = ("UPDATE transactions"
                            f" SET datetime = '{values['datetime']}', bruto = {values['bruto']}, truckTara = {values['truckTara']},"
                            f" neto = {values['neto']}, truck = '{values['truck']}', containers = '{values['containers']}'"
                            f" WHERE id = {query_id}")
            cursor.execute(update_query)
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


def update_container(id: str, weight: int, unit: str):
    cnx = connect(**config)
    if cnx.is_connected():
        cursor = cnx.cursor()
        query = ("UPDATE containers_registered"
                 f" SET weight = {weight}, unit = '{unit}'"
                 f" WHERE container_id = '{id}'")
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
    query = (f"SELECT * FROM transactions WHERE datetime >= '{start_date}'"
             f" AND datetime <= '{end_date}' AND {directions_query}")
    if cnx.is_connected():
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute(query)
            result = []
            in_entries: dict[str, int] = {}
            # if entry direction is "in" or "none", submit as-is
            # if entry direction is "out", find previous entry with same truck field which has "in" direction
            # and change id to match its id
            for entry in cursor.fetchall():
                neto = entry["neto"] if entry["neto"] != -1 else "na"
                if entry["direction"] != "out":
                    result_entry = {"id": entry["id"],
                                    "direction": entry["direction"],
                                    "bruto": entry["bruto"],
                                    "neto": neto,
                                    "produce": entry["produce"],
                                    "containers": []}
                    if entry["containers"]:
                        for container in entry["containers"].split(','):
                            result_entry["containers"].append(container)
                    if entry["direction"] == "in":
                        in_entries[entry["truck"]] = entry["id"]
                else:
                    result_entry = {"id": in_entries[entry["truck"]],
                                    "direction": entry["direction"],
                                    "bruto": entry["bruto"],
                                    "neto": neto,
                                    "produce": entry["produce"],
                                    "containers": []}
                result.append(result_entry)
            return result
        except Exception as ex:
            return ex
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
            if not session_start:
                return False

            is_truck = session_start["truck"] != "-"
            result = {"id": session_start["id"],
                      "truck": "na",
                      "bruto": session_start["bruto"]}
            if not is_truck:
                return result
            result["truck"] = session_start["truck"]
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


def get_container_ids_without_weight():
    result = []
    query = f"SELECT container_id FROM containers_registered WHERE weight = -1"

    cnx = connect(**config)
    if cnx.is_connected():
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute(query)
            for entry in cursor.fetchall():
                result.append(entry["container_id"])
            return result
        except:
            print("err")
            # TODO: handle errors
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()


def get_truck_transactions_by_id_and_dates(start_date: str, end_date: str, id: str):
    # get session ids
    session_query = f"SELECT id FROM transactions WHERE truck = '{id}'"
    tara_query = (f"SELECT truckTara FROM transactions WHERE truck = '{id}'"
                  f" AND direction = 'out' ORDER BY id DESC LIMIT 1")
    cnx = connect(**config)
    result = {}
    if cnx.is_connected():
        cursor = cnx.cursor()
        try:
            cursor.execute(session_query)
            for session in cursor:
                if "sessions" not in result:
                    result["sessions"] = []
                result["sessions"].append(session)

            cursor.execute(tara_query)
            if not cursor:
                result["tara"] = "na"
                result["id"] = id
                return result
            for tara in cursor:
                result["tara"] = tara
            result["id"] = "id"
            return result
        except:
            print("err")
            # TODO: handle errors
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()
            return result


def get_container_transactions_by_id_and_dates(start_date: str, end_date: str, id: str):
    session_query = f"SELECT id FROM transactions WHERE containers = '{id}' AND truck = '-'"
    result = {}
    cnx = connect(**config)
    if cnx.is_connected():
        cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute(session_query)
            for session in cursor:
                if "sessions" not in result:
                    result["sessions"] = []
                result["sessions"].append(session["id"])
            result["id"] = id
            result["tara"] = "na"
            if "sessions" not in result:
                return False
            return result
        except:
            print("err")
            # TODO: handle errors
        finally:
            if cnx.is_connected():
                cursor.close()
                cnx.close()
