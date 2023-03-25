import json
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from http import HTTPStatus
import pytest
from weight import app, reset_database
import json
from datetime import datetime

app.testing = True


OK = "200 OK"
BAD_REQUEST = "400 BAD REQUEST"


def test_get_health():
    with app.test_client() as c:
        response = c.get("/health")
        assert b"OK" in response.data


def test_get_session():
    reset_database()
    with app.test_client() as c:
        # test getting a session that doesn't exist
        session_response = c.get("/session/1")
        assert session_response.status == BAD_REQUEST
        truck_params = {"direction": "in",
                        "truck": "123-12-123",
                        "containers": "C-35434",  # 296 kg
                        "weight": 1000,
                        "unit": "kg",
                        "force": False,
                        "produce": "apples"}
        container_params = {"direction": "none",
                            "truck": "na",
                            "containers": "C-73281",
                            "weight": 500,
                            "unit": "kg",
                            "force": False,
                            "produce": "na"}
        # insert data for testing
        truck_weight_response = c.post("/weight", query_string=truck_params)
        cont_weight_response = c.post("/weight", query_string=container_params)
        # keep session id
        truck_session = json.loads(truck_weight_response.data)["id"]
        container_session = json.loads(cont_weight_response.data)["id"]
        # get truck response from app
        truck_session_response = c.get(f"/session/{truck_session}")
        assert truck_session_response.status == OK

        truck_data = json.loads(truck_session_response.data)
        assert truck_session == truck_data["id"]
        assert truck_data["truck"] == "123-12-123"
        assert truck_data["bruto"] == 1000
        # get container response from app
        container_session_response = c.get(f"/session/{container_session}")
        assert container_session_response.status == OK

        container_data = json.loads(container_session_response.data)
        assert container_session == container_data["id"]
        assert container_data["truck"] == "na"
        assert container_data["bruto"] == 500

        # end truck session
        truck_params = {"direction": "out",
                        "truck": "123-12-123",
                        "containers": "",
                        "weight": 300,
                        "unit": "kg",
                        "force": False,
                        "produce": "na"}
        truck_weight_response = c.post("/weight", query_string=truck_params)
        # get truck response from app
        truck_session_response = c.get(f"/session/{truck_session}")
        assert truck_session_response.status == OK
        truck_data = json.loads(truck_session_response.data)

        assert truck_session == truck_data["id"]
        assert truck_data["truck"] == "123-12-123"
        assert truck_data["bruto"] == 1000
        assert truck_data["truckTara"] == 300
        assert truck_data["neto"] == 1000 - 300 - 296


def test_post_weight():
    reset_database()
    with app.test_client() as c:
        # 0k 200 expected; truck weighing in first time:
        test_data = {"direction": "in",
                     "truck": "12-12-12",
                     "containers": "C-35434,K-8263",
                     "weight": 7777,
                     "unit": "kg",
                     "force": False,
                     "produce": "oranges"}
        response = c.post("/weight", query_string=test_data)

        data = json.loads(response.data)
        assert response.status == OK
        assert data["id"] == 10001
        assert data["truck"] == "12-12-12"
        assert data["bruto"] == 7777

        # Bad request expected; same truck. in after in test. force = false:
        test_data = {"direction": "in",
                     "truck": "12-12-12",
                     "containers": "C-35434,K-8263,T-17267",
                     "weight": 10000,
                     "unit": "kg",
                     "force": False,
                     "produce": "oranges"}
        response = c.post("/weight", query_string=test_data)
        assert response.status == BAD_REQUEST
        assert b"Truck already in. To override current 'in', request with force=True" in response.data

        # 0k 200 expected; override last in transaction,force = true:
        test_data = {"direction": "in",
                     "truck": "12-12-12",
                     "containers": "C-35434,K-8263,T-17267",
                     "weight": 10000,
                     "unit": "kg",
                     "force": True,
                     "produce": "oranges"}
        response = c.post("/weight", query_string=test_data)
        data = json.loads(response.data)
        assert response.status == OK
        assert data["id"] == 10001
        assert data["truck"] == "12-12-12"
        assert data["bruto"] == 10000

        # Bad request expected; out, produce value not empty(diff from "na"):
        test_data = {"direction": "out",
                     "truck": "12-12-12",
                     "containers": "",
                     "weight": 100,
                     "unit": "kg",
                     "force": False,
                     "produce": "oranges"
                     }
        response = c.post("/weight", query_string=test_data)
        assert response.status == BAD_REQUEST
        assert b"Truck must be empty while getting out" in response.data

        # Bad request expected; out, containers value not empty:
        test_data = {"direction": "out",
                     "truck": "12-12-12",
                     "containers": "C-35434,K-8263",
                     "weight": 100,
                     "unit": "kg",
                     "force": False,
                     "produce": "oranges"
                     }
        response = c.post("/weight", query_string=test_data)
        assert response.status == BAD_REQUEST
        assert b"Truck must be empty while getting out" in response.data

        # 0k 200 expected; truck weighing out after in test:
        test_data = {"direction": "out",
                     "truck": "12-12-12",
                     "containers": "",
                     "weight": 100,
                     "unit": "kg",
                     "force": False,
                     "produce": "na"}
        response = c.post("/weight", query_string=test_data)
        assert response.status == OK
        data = json.loads(response.data)
        assert data["id"] == 10002
        assert data["truck"] == "12-12-12"
        assert data["bruto"] == 100
        assert data["truckTara"] == 100
        assert data["neto"] == 9056

        # Bad request expected; same truck, out after out test,force = false:
        test_data = {"direction": "out",
                     "truck": "12-12-12",
                     "containers": "",
                     "weight": 100,
                     "unit": "kg",
                     "force": False,
                     "produce": "na"}
        response = c.post("/weight", query_string=test_data)
        assert response.status == BAD_REQUEST
        assert b"Truck cannot get out if not inside to override last transaction change force to true." in response.data

        # OK 200; override last out transaction,force = true:
        test_data = {"direction": "out",
                     "truck": "12-12-12",
                     "containers": "",
                     "weight": 50,
                     "unit": "kg",
                     "force": True,
                     "produce": "na"}
        response = c.post("/weight", query_string=test_data)
        assert response.status == OK
        data = json.loads(response.data)
        assert data["id"] == 10002
        assert data["truck"] == "12-12-12"
        assert data["bruto"] == 50
        assert data["truckTara"] == 50
        assert data["neto"] == 9106

        # Bad request expected; out for unexisting truck:
        test_data = {"direction": "out",
                     "truck": "123-123-123",
                     "containers": "",
                     "weight": 100,
                     "unit": "kg",
                     "force": False,
                     "produce": "na"}
        response = c.post("/weight", query_string=test_data)
        assert response.status == BAD_REQUEST
        assert b"Truck has not been weighed yet" in response.data

        # Bad request expected; check all wrong insertions scenarios:
        response = c.post("/weight", query_string=test_data)
        test_data = {"direction": "fhe",
                     "truck": "12-12-12a",
                     "containers": "C-35434,K-8263",
                     "weight": -7777,
                     "unit": "feofe",
                     "force": "jfeoiw",
                     "produce": "oranges123"}
        response = c.post("/weight", query_string=test_data)
        assert response.status == BAD_REQUEST
        bad_response = b"Truck lisence must be in numbers divided by dashes\nDirection must be in/out/none\nWeight must be positive integer.\nUnit value must be Kg/Lbs\nForce value must be True/False\nProduce must be letters string"
        assert bad_response in response.data


def test_get_item():
    reset_database()

    with app.test_client() as c:
        container_params = {"direction": "none",
                            "truck": "na",
                            "containers": "C-73281",
                            "weight": 500,
                            "unit": "kg",
                            "force": False,
                            "produce": "na"}
        cont_weight_response = c.post("/weight", query_string=container_params)
        # keep session id
        container_session = json.loads(cont_weight_response.data)["id"]
        today = datetime.today()
        year = today.year
        # guarantee double digits
        month = today.month if today.month > 9 else f"0{today.month}"
        day = today.day if today.day > 9 else f"0{today.day}"
        start = f"{year}{month}{day}000000"

        hour = today.hour if today.hour > 9 else f"0{today.hour}"
        minute = today.minute if today.minute > 9 else f"0{today.minute}"
        second = today.second if today.second > 9 else f"0{today.second}"
        end = f"{year}{month}{day}{hour}{minute}{second}"

        request_params = {"from": start, "to": end, "id": "C-73281"}
        result_response = c.get("/item", query_string=request_params)
        result_response.text
        assert result_response.status == OK
        result_body = json.loads(result_response.data)

        assert result_body["tara"] == "na"
        assert result_body["sessions"][0] == container_session

        # test getting an item that doesn't exist
        request_params["id"] = "a made up id"
        result_response = c.get("/item", query_string=request_params)
        assert result_response.status == OK
        assert json.loads(result_response.data)["tara"] == "na"
        assert "sessions" not in json.loads(result_response.data)


def test_get_weight():
    reset_database()
    with app.test_client() as c:
        today = datetime.today()
        year = today.year
        # guarantee double digits
        month = today.month if today.month > 9 else f"0{today.month}"
        day = today.day if today.day > 9 else f"0{today.day}"
        start = f"{year}{month}{day}000000"

        hour = today.hour if today.hour > 9 else f"0{today.hour}"
        minute = today.minute if today.minute > 9 else f"0{today.minute}"
        second = today.second if today.second > 9 else f"0{today.second}"
        end = f"{year}{month}{day}{hour}{minute}{second}"
        request_params = {"from": start, "to": end, "filter": "in,out,none"}
        # test getting no weights
        request_response = c.get("/weight", query_string=request_params)
        assert request_response.status == OK
        assert not json.loads(request_response.data)
