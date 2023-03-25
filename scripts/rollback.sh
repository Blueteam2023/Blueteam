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

# Sending mails function
send_mail(){
	subject="Gan Shmuel CI\CD: $1"
	body="$2"
    if [ "$3" = "dev" ]; then
        dev_email=$(grep "^$pusher " ./data/emails.txt | awk '{print $2}')
        message="To: $DEVOPS_MAIL\nSubject: $subject\n\n$body"
        echo -e "$message" | ssmtp $dev_email,$DEVOPS_MAIL
    else
        message="To: $DEVOPS_MAIL\nSubject: $subject\n\n$body"
        echo -e "$message" | ssmtp $DEVOPS_MAIL
    fi
    if [ $? -eq 0 ]; then
        echo "Email sent successfully."
    else
        echo "Error sending email."
    fi
}

stop_production
cd /app
git checkout tags/"$TAG_NAME"
start_production

echo $TAG_NAME >> ./data/stable_versions.txt
send_mail "Version Rolled back: $TAG_NAME" "The application has been rolled back to version $TAG_NAME. Please review and verify the changes."
echo "Rolled back to version $TAG_NAME and sent an email to the devops team for manually adjusting."