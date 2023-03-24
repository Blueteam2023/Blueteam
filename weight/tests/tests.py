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
