#!/bin/sh
team1="billing"
team2="weight"


if [ -z $(docker ps | grep "weight-app") ] && [ -z $(docker ps | grep "billing-app") ]; then
    echo "Running Production Envoirment"
    docker-compose -f /app/$team1/docker-compose.yaml up -d
    docker-compose -f /app/$team2/docker-compose.yaml up -d
else
    echo "Proudction containers already up"
fi