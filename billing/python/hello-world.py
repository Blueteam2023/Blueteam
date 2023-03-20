#!/bin/python3

import mysql.connector

connection=mysql.connector.connect(
	user='root', password='root', host='mysql', port="3306", database='db')
print("DB connected")

cursor=connection.cursor()
cursor.execute('select * from provider;')
provider=cursor.fetchall()
connection.close()

print(f"res:{provider}")
