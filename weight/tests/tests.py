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
                        "containers": "C-35434",
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
        c.post("/weight", query_string=truck_params)
        c.post("/weight", query_string=container_params)
    app.test_client().post("/weight",)


def test_post_weight():
    reset_database()
    test_data = {"direction": "in", "truck": "12-12-12",
                   "containers": "C-35434,K-8263,T-17267", "bruto": 50, "truckTara": -1, "neto": -1, "produce": "oranges"}
    with app.test_client() as c:
        response = c.post("/weight",query_string=test_data)
        assert response.status == HTTPStatus.OK
        assert response.data == {"id":10001,"truck":"12-12-12","bruto":"50","truckTara":-1,"neto":-1}
