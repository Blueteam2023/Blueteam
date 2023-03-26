#!/bin/python3
import pycurl
import certifi
from io import BytesIO

def test_get(route):
	print(f"Testing {route}")
	try:
		# Creating a buffer as the cURL is not allocating a buffer for the network response
		buffer = BytesIO()
		c = pycurl.Curl()
		#initializing the request URL
		c.setopt(c.URL, route)
		#setting options for cURL transfer  
		c.setopt(c.WRITEDATA, buffer)
		#setting the file name holding the certificates
		c.setopt(c.CAINFO, certifi.where())
		# perform file transfer
		c.perform()
				# page response code, Ex. 200 or 404.
		print('Response Code: %d' % c.getinfo(c.RESPONSE_CODE))
		#Ending the session and freeing the resources
		c.close()
		#retrieve the content BytesIO
		body = buffer.getvalue()
		#decoding the buffer 
		#print(body.decode('iso-8859-1'))
	except:
		print(f"Bad response from {route}")

test_get('172.19.0.3:80/health')
test_get('172.19.0.3:80/provider')
test_get('172.19.0.3:80/providerlist')
test_get('172.19.0.3:80/provider/1')
test_get('172.19.0.3:80/truck')
test_get('172.19.0.3:80/bill/10001')
test_get('172.19.0.3:80/bill/10001?from=20230101103025&to=202301030103025')

#if curl 172.19.0.3:80/; then 
#curl 172.19.0.3:80/health
#curl 172.19.0.3:80/provider
#curl 172.19.0.3:80/providerlist
#curl 172.19.0.3:80/provider/10001
#curl 172.19.0.3:80/provider/1
#curl 172.19.0.3:80/truck
#curl 172.19.0.3:80/bill/10001
