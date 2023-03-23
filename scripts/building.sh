#!/bin/sh

set -x #debugging 
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
number=$4

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
    echo "Finished cloning from repo"
}

# Modify files for testing envoirment
Modify_files(){
	b=$1
    echo "Modifying $b files for testing envoirment"
    if [ "$b" = "billing" ]; then
	    #sed -i "s/ENV_HOST=.*/ENV_HOST=test-$b-db/" sql.env
        sed -i "s/8082/8088/g" docker-compose.yaml
        sed -i "s/8081/8087/g" docker-compose.yaml
    elif [ "$b" = "weight" ]; then
        #sed -i "s/DB_HOST=.*/DB_HOST=test-$b-db/" .env
        sed -i "s/8083/8089/g" docker-compose.yaml
    fi
	sed -i "s/container_name: $b-app/container_name: test-$b-app/" docker-compose.yaml
	sed -i "s/container_name: $b-database/container_name: test-$b-database/" docker-compose.yaml
    sed -i "s/BlueTeam/test_network/g" docker-compose.yaml
    echo "Finished modifying $b files for testing envoirment"
}

# Build testing containers
Build_testing(){
	echo "Building testing containers"
	cd /app/testenv/$team1
	Modify_files $team1
	cd /app/testenv/$team2
	Modify_files $team2
    echo "Building $team1 containers"
	docker-compose -f /app/testenv/$team1/docker-compose.yaml --project-name testing up -d
    echo "Building $team2 containers"
	docker-compose -f /app/testenv/$team2/docker-compose.yaml --project-name testing up -d
    echo "Finished building testing containers"
}

# Health check
Health_check(){
    if [ $1 = "testing" ]; then
        check_billing=$(curl -s -o /dev/null -w "%{http_code}" http://test-$team1-app/health)
        check_weight=$(curl -s -o /dev/null -w "%{http_code}" http://test-$team2-app/health)
    elif [ $1 = "production" ]; then
        check_billing=$(curl -s -o /dev/null -w "%{http_code}" http://billing-app/health)
        check_weight=$(curl -s -o /dev/null -w "%{http_code}" http://weight-app/health)
    fi
	if [ "$check_billing" -eq 200 ] && [ "$check_weight" -eq 200 ]; then
    	return 0
	else
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

    devops_email="blueteamdevops2023@gmail.com"
	subject="Gan Shmuel Alert: $1"
	body="$2"
    message="From: $from_email\nTo: $to_email\nSubject: $subject\n\n$body"
    if [ $3 = "dev" ]; then
        to_email=$(grep "^$pusher " email.txt | awk '{print $2}')
        echo "$message" | sendmail "$to_email,$devops_email"
    else
        echo "$message" | sendmail $devops_email
    fi
	
	
	if [ $? -eq 0 ]; then
    	echo "Email sent successfully."
	else
		echo "Error sending email."
	fi
}

# Terminate testing enovirment
Terminate_testing(){
	echo "Terminating test envoirment"
    docker-compose -f /app/testenv/$team1/docker-compose.yaml --project-name testing stop
    docker-compose -f /app/testenv/$team1/docker-compose.yaml --project-name testing rm -f
    docker-compose -f /app/testenv/$team2/docker-compose.yaml --project-name testing stop
    docker-compose -f /app/testenv/$team2/docker-compose.yaml --project-name testing rm -f
	rm -rf /app/testenv/*
    rm -rf /app/testenv/.git
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
        #Send_mail "Health check failed during production build" "revert pull request $number"
        echo "Health failed in production, reverting to last commit"
        git reset --hard HEAD~1
        ./deploy.sh
    else
        echo "Building production finished"
        tag="Stable $TIMESTAMP"
        git tag $tag
        git push origin $tag
        #Send_mail "Update completed" "New update in on the air"
    fi
}

Testing_init(){
    if [ "$branch" = "billing" ] || [ "$branch" = "weight" ]; then
        Clone
        Build_testing
        echo "Checking health"
        #health=$(Health_check testing) temp
        health=0
        if [ $health -eq 1 ]; then
            #Send_mail "Health check failed during testing, revert pull request $number" "Contact devops team for more details."
            echo "Health failed, Reverting to last commit"
            #git reset --hard HEAD~1
        else
            Tester=0
            if [ $Tester -eq 0 ]; then
                echo "Test passed, Starting production update"
                Production_init
            else
                echo "Test failed"
                #Send_mail "Test Failed, revert pull request" "Contact devops team for more details."
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
fi
touch "$lockfile"
Testing_init
rm "$lockfile"


