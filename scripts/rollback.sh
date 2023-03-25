#!/bin/sh

set -x #debugging 

# Check if an argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: rollback <valid_tag_name>"
    exit 1
fi

TAG_NAME="$1"

stop_production(){
    echo "Stopping production for rollback to version $TAG_NAME"
    docker-compose -f /app/$team1/docker-compose.yaml stop
    docker-compose -f /app/$team1/docker-compose.yaml rm -f
    docker-compose -f /app/$team2/docker-compose.yaml stop
    docker-compose -f /app/$team2/docker-compose.yaml rm -f  
    echo "Production environment is offline" 
}

stop_production
cd /app
git checkout tags/"$TAG_NAME"
stop_production
exec /app/scripts/deploy.sh

echo $TAG_NAME >> ./data/stable_versions.txt
send_mail "Version Rerolled: $TAG_NAME" "The application has been rerolled to version $TAG_NAME. Please review and verify the changes."
echo "Rerolled to version $TAG_NAME and sent an email to the devops team."