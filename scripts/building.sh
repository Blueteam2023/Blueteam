#!/bin/sh

set -x #debugging 
#set -e #exit if a command fails

GIT_REPO=Blueteam
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
branch=$1
pusher=$2
url=$3
number=$4
team1_port=8082
team2_port=8084
DEVOPS_MAIL="blueteamdevops2023@gmail.com"
team1="billing"
team2="weight"
lockfile=/tmp/building.lock
error_msg=""
health_result=1


# Clone to test envoirment
clone_testing(){
	echo "Getting new version for testing from $branch"
	if [ -d "/app/testenv" ]; then
		cd /app/testenv
	else
		mkdir /app/testenv
		cd /app/testenv
	fi
	git clone 'https://github.com/Blueteam2023/Blueteam.git' .
    echo "Finished cloning test environment from repo"
}

# Modify files for testing envoirment
modify_files(){
	b=$1
    echo "Modifying $b files for testing environment"
    if [ "$b" = "billing" ]; then
	    sed -i "s/ENV_HOST=.*/ENV_HOST=test-$b-database/" sql.env
    elif [ "$b" = "weight" ]; then
        sed -i "s/ENV_HOST=.*/ENV_HOST=test-$b-database/" .env
    fi
	sed -i "s/container_name: $b-app/container_name: test-$b-app/" docker-compose.yaml
	sed -i "s/container_name: $b-database/container_name: test-$b-database/" docker-compose.yaml
    sed -i "s/BlueTeam/test_network/g" docker-compose.yaml
    sed -i "s|'/home/ubuntu/app/'|'/home/ubuntu/app/testenv/'|" docker-compose.yaml
    echo "Finished modifying $b files for testing environment"
}

# Build testing containers
build_testing(){
    echo "Building testing containers"
    cd /app/testenv/$team1
    modify_files $team1
    cd /app/testenv/$team2
    modify_files $team2
    echo "Building $team1 containers"
    docker-compose -f /app/testenv/$team1/docker-compose.yaml --project-name testing up -d
    echo "Building $team2 containers"
    docker-compose -f /app/testenv/$team2/docker-compose.yaml --project-name testing up -d
    echo "Finished building testing containers"
}

# Health check

check_health(){
  service="$1"
  port="$2"
  health=$(curl -s -o /dev/null -w "%{http_code}" http://$service:$port/health)
  echo $health
}

health_test(){
    timeout=30
    interval=5
    attempts=$((timeout / interval))
    success=false
    for i in $(seq 1 $attempts); do
        if [ "$1" = "testing" ]; then
            check_billing=$(check_health "test-$team1-app" 80)
            check_weight=$(check_health "test-$team2-app" 8000)
        elif [ "$1" = "production" ]; then
            check_billing=$(check_health "$team1-app" 80)
            check_weight=$(check_health "$team2-app" 8000)
        fi
        if [ "$check_billing" = "200" ] && [ "$check_weight" = "200" ]; then
            success=true
            break
        else
            echo "Health check failed, retrying in $interval seconds..."
            sleep $interval
        fi
    done
    if [ "$success" = true ]; then
        health_result=0
    else
        health_result=1
    fi
}

# Run devs E2E tests
run_e2e_tests(){
    b=$1
    echo "Running E2E tests for $b"
    if [ "$b" = "weight" ]; then # Weight app tests
        test_result=$(docker exec -i weight-app pytest tests.py 2>&1)
        passed_count=$(echo "$test_result" | grep -E -o '([0-9]+) passed' | cut -d' ' -f1)
        failed_count=$(echo "$test_result" | grep -E -o '([0-9]+) failed' | cut -d' ' -f1)
        echo "Total Passed: $passed_count"
        echo "Total Failed: $failed_count"
        if [ -z $failed_count ]; then
            return 0
        else
            return 1
        fi
    elif [ "$b" = "billing" ]; then
        return 0
    fi
}

# Sending mails function
send_mail(){
	subject="Gan Shmuel CI\CD: $1"
	body="$2"
    if [ "$3" = "dev" ]; then
        dev_email=$(grep "^$pusher " /app/scripts/data/emails.txt | awk '{print $2}')
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

# Terminate testing environment
terminate_testing(){
	echo "Terminating test environment"
    docker-compose -f /app/testenv/$team1/docker-compose.yaml --project-name testing stop
    docker-compose -f /app/testenv/$team1/docker-compose.yaml --project-name testing rm -f
    docker-compose -f /app/testenv/$team2/docker-compose.yaml --project-name testing stop
    docker-compose -f /app/testenv/$team2/docker-compose.yaml --project-name testing rm -f
	rm -rf /app/testenv/*
    rm -rf /app/testenv/.git
}

stop_production(){
    echo "Stopping production for update"
    docker-compose -f /app/$team1/docker-compose.yaml stop
    docker-compose -f /app/$team1/docker-compose.yaml rm -f
    docker-compose -f /app/$team2/docker-compose.yaml stop
    docker-compose -f /app/$team2/docker-compose.yaml rm -f  
    echo "Production environment is offline" 
}

build_production(){
    echo "Building new version"
    docker-compose -f /app/$team1/docker-compose.yaml up --build -d
    docker-compose -f /app/$team2/docker-compose.yaml up --build -d
    echo "New version is builed"
}

production_init(){
    stop_production
    echo "Pulling new version from the remote repo"
    cd /app
    git pull
    build_production
    echo "Starting health check"
    health_test production
    #health=0 # for testing
    if [ $health_result -eq 1 ]; then
        echo "Health failed in production, rerolling to the previous version"
        stop_production
        version=$(tail -n 1 "/app/scripts/data/stable_versions.txt")
        if [ -z "$version" ]; then
            echo "ERROR: No stable versions found."
            echo "Sending alert to devops team"
            send_mail "ERROR: no production online. Health check failed and non stable versions found" "Request $number: Health check failed and non stable versions found"
            # can add option to revert to last commit for unstable version
            return 1 
        fi
        git checkout tags/"$version"
        send_mail "ERROR: production health check failed. Version Rolled back to $version" "The application has been Rolled back to version $version."
        echo "Staring the previous version production"
        build_production # deploy previous version
    else
        echo "Building production finished successfully"
        send_mail "Version update is successfully" "The new version is currently online" dev
        tag="Stable-$TIMESTAMP"
        echo $tag >> /app/scripts/data/stable_versions.txt
        git tag $tag
        git push origin $tag
        echo "$tag version tagged as stabled"
    fi
}

testing_init(){
    if [ "$branch" = "billing" ] || [ "$branch" = "weight" ]; then
        clone_testing
        build_testing
        echo "Starting health check"
        health_test testing
        if [ $health_result -eq 1 ]; then
            send_mail "New version deploy failed, Healthcheck test failed during testing" "Request number: $number\nContact devops team for more details" dev
            echo "Health failed, Stopping update process."
            terminate_testing
            return 1
            #git reset --hard HEAD~1
        elif [ $health_result -eq 0 ]; then
            echo "running E2E tests"
            run_e2e_tests weight
            weight_tester=$?
            run_e2e_tests billing
            billing_tester=$?

            if [ $weight_tester -eq 0 ] && [ $billing_tester -eq 0 ]; then
                echo "E2E Tests passed successfully, Starting production update"
                terminate_testing
                return 0
            elif [ $tester -eq 1 ]; then
                send_mail "New version deploy failed, E2E tests failed during testing" "Request number: $number\nContact devops team for more details" dev
                echo "E2E Tests failed, Stopping update process"
                terminate_testing
                return 1
            fi
        fi  	
    fi
}

main(){
    if [ -f "$lockfile" ]; then
        echo "Previous process is still running, Waiting to finish"
        while [ -f "$lockfile" ]; do
            sleep 30
        done
    fi
    touch "$lockfile"
    testing_init
    testing_result=$?
    if [ $testing_result -eq 0 ]; then
        production_init
    else
        echo "Testing Failed" 
    fi
    rm "$lockfile"
}

main


