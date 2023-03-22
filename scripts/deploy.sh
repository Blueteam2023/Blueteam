#!/bin/sh
team1="billing"
team2="weight"


if [ -z "$(docker ps -q -f name=weight-app)" ] || [ -z "$(docker ps -q -f name=billing-app)" ]; then
    echo "Running Production Envoirment"
    if [ -z "$(docker ps -q -f name=weight-app)" ]; then
        echo "Starting $team1 container"
        docker-compose -f /app/$team1/docker-compose.yaml up -d
    fi
    if [ -z "$(docker ps -q -f name=billing-app)" ]; then
        echo "Starting $team2 container"
        docker-compose -f /app/$team2/docker-compose.yaml up -d
    fi   
else
    echo "Proudction containers already up"
fi