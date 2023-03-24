import json
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from http import HTTPStatus
import pytest
from weight import app, reset_database

app.testing = True


def test_get_health():
    with app.test_client() as c:
        response = c.get("/health")
        assert b"OK" in response.data


def test_get_session():
    reset_database()
    with app.test_client() as c:
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
        assert truck_session_response.status == "200 OK"

        truck_data = json.loads(truck_session_response.data)
        assert truck_session == truck_data["id"]
        assert truck_data["truck"] == "123-12-123"
        assert truck_data["bruto"] == 1000
        # get container response from app
        container_session_response = c.get(f"/session/{container_session}")
        assert container_session_response.status == "200 OK"

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
        assert truck_session_response.status == "200 OK"
        truck_data = json.loads(truck_session_response.data)

        assert truck_session == truck_data["id"]
        assert truck_data["truck"] == "123-12-123"
        assert truck_data["bruto"] == 1000
        assert truck_data["truckTara"] == 300
        assert truck_data["neto"] == 1000 - 300 - 296
