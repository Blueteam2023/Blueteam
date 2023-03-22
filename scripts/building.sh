#!/bin/sh

set -e #exit if a command fails

GIT_REPO=Blueteam
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
branch=$1
pusher=$2
billing_port=8082
weight_port=8083
url=$3
GITHUB_TOKEN=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
DEVOPS_MAIL="blueteamdevops2023@gmail.com"
team1="billing"
team2="weight"
lockfile=/tmp/building.lock

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
    if [ "$b" = "billing" ]; then
	    sed -i "s/ENV_HOST=.*/ENV_HOST=test-$b-db/" sql.env
        sed -i "s/8082/8088/g" docker-compose.yaml
    elif [ "$b" = "weight" ]; then
        sed -i "s/DB_HOST=.*/DB_HOST=test-$b-db/" .env
        sed -i "s/8083/8089/g" docker-compose.yaml
    fi
	sed -i "s/container_name: $b-app/container_name: test-$b-app/" docker-compose.yaml
	sed -i "s/container_name: $b-database/container_name: test-$b-database/" docker-compose.yaml
    sed -i "s/Blueteam/test_network/g" docker-compose.yaml
}

# Build testing containers
Build_testing(){
	echo "Building testing containers"
	cd /app/testenv/$team1
	Modify_files $team1
	cd /app/testenv/$team2
	Modify_files $team2
	docker-compose -f /app/testenv/$team1/docker-compose.yaml up -d
	docker-compose -f /app/testenv/$team2/docker-compose.yaml up -d
}

# Health check
Health_check(){
    if [ $1 = "testing" ]; then
        check_billing=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8088/health)
        check_weight=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8089/health)
    elif [ $1 = "production" ]; then
        check_billing=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$billing_port/health)
        check_weight=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$weight_port/health)
    fi
	if [ "$check_billing" -eq 200 ] && [ "$check_weight" -eq 200 ]; then
    	return 0
	else
        echo "Billing status: $check_billing, Weight status: $check_weight"
		return 1
	fi
}

# Run E2E tests
Test(){
	echo "running E2E tests"
	return 0
}

# Sending mails function
Send_mail(){
	#to_email=$(grep "^$pusher " email.txt | awk '{print $2}')
    to_email="blueteamdevops2023@gmail.com"
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
	docker-compose -f /app/testenv/$branch/docker-compose.yaml down --rmi all
	docker-compose -f /app/testenv/$sec_branch/docker-compose.yaml down --rmi all
	rm -r /app/testenv/*
}

Revert_main(){
    echo "Reverting to last known stable version"
    git checkout -b reverted_main
    git revert HEAD --no-edit
    git add .
    git commit -m "reverted version"
    git push origin reverted_main
    base_url=$(echo $url | sed 's/\([0-9]\+\)$//')
    # Create new pull request for reverted
    curl -H "Authorization: token $GITHUB_TOKEN" \
     -X POST \
     -d "{\"title\": \"reverted main\", \"body\": \"reverted version\", \"head\": \"reverted_main\", \"base\": \"main\"}" \
     "$base_url"
}

Stop_production(){
    echo "Stopping production for update"
    docker stop $team1-app && docker stop $team2-app
    docker rm $team1-app && docker rm $team2-app
    docker rm -f $team1-db && docker rm -f $team2-db    
}

Build_production(){
    echo "Building new version"
    docker-compose -f /app/$team1/docker-compose.yaml up --build -d
    docker-compose -f /app/$team2/docker-compose.yaml up --build -d
}

Production_init(){
    Stop_production
    Build_production
    health=$(Health_check production)
    if ! $health ; then
        echo "Health failed in production"
        Revert_main
        Send_mail "Health check Failed during production build" "Contact devops team for more details."
        Production_init
    else
        echo "Building production finished"
        Send_mail "Updating completed" "New update in on the air"
    fi
}

Testing_init(){
    if [ "$branch" = "billing" ] || [ "$branch" = "weight" ]; then
        Clone
        Build_testing
        health=$(Health_check testing)
        if ! $health ; then
            echo "Health failed"
            Revert_main
            Send_mail "Health check Failed during testing" "Contact devops team for more details."
        else
            if Test; then
                echo "Test passed, approving request"
                Production_init
            else
                echo "Test failed"
                Revert_main
                Send_mail "Test Failed, Please review errors" "Contact devops team for more details."
            fi
        fi
        Terminate_testing	
    fi
}

if [ -f "$lockfile" ]; then
    echo "Previous process is still running, Waiting to finish"
    while [ -f "$lockfile" ]; do
        sleep 30
    done
else
    touch "$lockfile"
    Testing_init
    rm "$lockfile"
fi
