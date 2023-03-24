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
    app.test_client().post("/weight", )
