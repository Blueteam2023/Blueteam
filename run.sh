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
    cp /path/to/your/ssh_key id_ed25519
fi


echo "Starting Gan-Shmuel"
docker-compsoe up
