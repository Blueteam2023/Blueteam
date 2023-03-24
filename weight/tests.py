from flask import Flask
import pytest
from weight import app


@pytest.fixture()
def create_test_app():
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture()
def client(app_instance: Flask):
    return app_instance.test_client()


@pytest.fixture()
def runner(app_instance: Flask):
    return app.test_cli_runner()
