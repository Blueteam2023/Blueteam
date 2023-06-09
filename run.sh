#!/bin/sh


echo "Weclome to Gan Shmuel"
printf "Do you want to remove previous Docker containers and images? (y/n): "
read answer

if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    docker rm -f $(docker ps -aq)
    docker rmi -f $(docker images -aq)
fi

if [ ! -f id_ed25519 ]; then
    echo "Fetching github ssh key from host"
    cp ../.ssh/id_ed25519 id_ed25519
fi

if [ ! -f ./scripts/data/stable_versions.txt ]; then
    echo "Creating new stable versions file"
    git fetch --tags 
    git tag --sort=creatordate > ./scripts/data/stable_versions.txt
else
    printf "Create new stable versions file from remote? (y/n): "
    read answer
    if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
        echo "Creating new stable versions file"
        git fetch --tags 
        git tag --sort=creatordate > ./scripts/data/stable_versions.txt
    fi
fi

echo "Starting Gan-Shmuel"
docker-compose up
