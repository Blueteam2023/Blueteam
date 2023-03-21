from flask import Flask, render_template, request
import datetime
from flask_mysqldb import MySQL
from http import HTTPStatus
from os import environ

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/weight", methods=["POST"])
def weight():
    return "True"


@app.route("/batch-weight", methods=["POST"])
def batch_weight():
    raise NotImplementedError


@app.route("/unknown", methods=["GET"])
def unknown():
    raise NotImplementedError


@app.route("/weight", methods=["GET"])
def Pweight():
    raise NotImplementedError


@app.route("/item/<id>", methods=["GET"])
def item():
    raise NotImplementedError


@app.route("/session/<id>", methods=["GET"])
def session():
    raise NotImplementedError


@app.route("/health", methods=["GET"])
def health():
    raise NotImplementedError


if __name__ == "__main__":
    app.run(debug=True)
