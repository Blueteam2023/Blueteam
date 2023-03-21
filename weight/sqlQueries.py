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
        try:
            cursor = cnx.cursor(dictionary=True)
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
    raise NotImplementedError


def get_container_weight_by_id(id: str):
    raise NotImplementedError


# For Carmen
def get_transaction_range_by_dates_and_directions(start_date: str, end_date: str, directions: list[str]):
    raise NotImplementedError
