from typing import Any
from mysql.connector import connect


def get_transactions_by_id(config: dict[str, Any], truck_id: str):
    query = f"SELECT * FROM transactions WHERE truck_id = '{truck_id}'"

    try:
        cnx = connect(**config)
        cursor = cnx.cursor()
        cursor.execute(query)

        result = ""
        for id, datetime, direction, truck, containers, bruto, truckTara, neto, produce in cursor:
            result += f"{id} {datetime} {direction} {truck} {containers} {bruto} {truckTara} {neto} {produce}"
        return result
    except:
        cnx = None
        cursor = None
        # TODO: implement error logging
    finally:
        if cnx and cursor:
            cursor.close()
            cnx.close()
