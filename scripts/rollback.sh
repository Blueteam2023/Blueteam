#!/bin/sh

set -x #debugging 

team1="billing"
team2="weight"

# Check if an argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: rollback <valid_tag_name>"
    exit 1
fi

TAG_NAME="$1"

echo "Rollback in process" >> ./data/stable_versions.txt


stop_production(){
    echo "Stopping production for rollback to version $TAG_NAME"
    docker-compose -f /app/$team1/docker-compose.yaml stop
    docker-compose -f /app/$team1/docker-compose.yaml rm -f
    docker-compose -f /app/$team2/docker-compose.yaml stop
    docker-compose -f /app/$team2/docker-compose.yaml rm -f  
    echo "Production environment is offline" 
}

start_production(){
    echo "Starting $team1 container"
    docker-compose -f /app/$team1/docker-compose.yaml up -d
    echo "Starting $team2 container"
    docker-compose -f /app/$team2/docker-compose.yaml up -d
}


stop_production
cd /app
git checkout tags/"$TAG_NAME"
start_production

echo $TAG_NAME >> ./data/stable_versions.txt
send_mail "Version Rerolled: $TAG_NAME" "The application has been rerolled to version $TAG_NAME. Please review and verify the changes."
echo "Rerolled to version $TAG_NAME and sent an email to the devops team."