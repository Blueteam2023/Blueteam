#!/bin/sh

set -e #exit if a command fails

GIT_REPO=Blueteam
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
branch=$1
pusher=$2
billing_port=8087
weight_port=8088
url=$3
GITHUB_TOKEN=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
DEVOPS_MAIL="blueteamdevops2023@gmail.com"
team1= "billing"
team2- "weight"

# Clone
Clone(){
	echo "Cloning repo with last commit"
	if [ -d "/app/testenv" ]; then
		cd /app/testenv
	else
		mkdir /app/testenv
		cd /app/testenv
	fi
	git clone 'https://github.com/Blueteam2023/Blueteam.git' .
}

# Modify files for testing envoirment
Modify_files(){
	b=$1
	sed -i "s/DB_HOST=*/DB_HOST=test-$b-db/" .env
	sed -i "s//container_name: $b-app: container_name: test-$b-app/" docker-compose.yml
	sed -i "s//container_name: $b-database: container_name: test-$b-database/" docker-compose.yml
	#add network and ports
}

# Docker-compose
Build(){
	echo "Building testing containers"
	cd /app/testenv/$team1
	Modify_files $team1
	cd /app/testenv/$team2
	Modify_files $team2
	docker-compose -f /app/testenv/$team1/docker-compose.* up
	docker-compose -f /app/testenv/$team2/docker-compose.* up
}

# Health check
health_check(){
	if [[ $branch == "billing" ]]; then
		port=8087
	elif [[ $branch == "weight" ]]; then
		port=8088
	elif [[ $branch == "devops" ]]; then
		port=8089
	else
		echo "branch not found"
	fi
	response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health)
	if [ "$response" -eq 200 ]; then
    	return True
	else
		return False
	fi
}

# Run E2E tests
Test(){
	echo "running E2E tests"
	return 0
}

# Sending mails function
Send_mail(){
	to_email=$(grep "^$pusher " email.txt | awk '{print $2}')
	subject="Gan Shmuel Alert: $1"
	body="$2"
	message="From: $from_email\nTo: $to_email\nSubject: $subject\n\n$body"
	echo "$message" | sendmail $to_email
	if [ $? -eq 0 ]; then
    	echo "Email sent successfully."
	else
		echo "Error sending email."
	fi
}

# Terminate testing enovirment
Terminate_testing(){
	echo "Terminating test envoirment"
	docker-compose -f /app/testenv/$branch/docker-compose.yml down --rmi all
	docker-compose -f /app/testenv/$sec_branch/docker-compose.yml down --rmi all
	rm -r /app/testenv/*
}

Revert_main(){
    git revert HEAD
    git push origin main
}

Production_init(){

}

Testing_init(){
    if [ "$branch" = "billing" ] || [ "$branch" = "weight" ]; then
        Clone
        Build
        #health_check
        if Test; then
            echo "Test passed, approving request"
            Production_init
            Send_mail "Test Passed, Waiting for approve" "You'll get alert once the merged to productin."
        else
            echo "Test failed"
            Revert_main
            Send_mail "Test Failed, Please review errors" "Contact devops team for more details."
        fi
        Terminate_testing	
    fi
}

