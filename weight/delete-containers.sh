#!/bin/bash

docker rm -f $(docker ps -aq)
docker rmi weight-app
