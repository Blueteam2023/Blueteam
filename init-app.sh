#!/bin/bash



docker rmi -f test



# Build the image
docker build -t gan-shmuel .

# Run the container
docker run -v "./testenv:/app/testenv" -p 8080:8080 -d gan-shmuel:latest
