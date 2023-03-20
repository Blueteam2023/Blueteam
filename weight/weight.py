from flask import Flask, render_template,request
import datetime
from flask_mysqldb import MySQL
import yaml
from http import HTTPStatus

app = Flask(__name__)

db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

@app.route("/weight",methods=["POST"])
def weight():
    return True


@app.route("/batch-weight",methods=["POST"])
def batchWeight():
    return True

@app.route("/unknown",methods=["GET"])
def unknown():
    return True

@app.route("/weight",methods=["GET"])
def Pweight():
    return True

@app.route("/item/<id>",methods=["GET"])
def item():
    return True

@app.route("/session/<id>",methods=["GET"])
def session():
    return True

@app.route("/health",methods=["GET"])
def health():
    return True

    
if __name__ == "__main__":

    app.run(debug=True)