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

if [ "$branch" = "billing" ]; then
	sec_branch="weight"
elif [ "$branch" = "weight" ]; then
	sec_branch="billing"
fi


clearExists(){
	if docker ps -a | grep test-$branch-app > /dev/null; then
		docker rm -f test-$branch-app
	fi
	if docker ps -a | grep test-$branch-db > /dev/null; then
		docker rm -f test-$branch-db
	fi
}

# Clone
Clone(){
	echo "Cloning repo from $branch"
	if [ -d "/app/testenv" ]; then
		cd /app/testenv
	else
		mkdir /app/testenv
		cd /app/testenv
	fi
	git clone -b $branch 'https://github.com/Blueteam2023/Blueteam.git' .
	
}

Modify_files(){
	b=$1
	sed -i "s/DB_HOST=*/DB_HOST=test-$b-db/" .env
	sed -i "s//container_name: $b-app: container_name: test-$b-app/" docker-compose.yml
	sed -i "s//container_name: $b-database: container_name: test-$b-database/" docker-compose.yml
	#add network and ports
}


# Docker-compose
build(){
	echo "Building testing containers"
	cd /app/testenv/$branch
	Modify_files $branch
	cd /app/testenv/$sec_branch
	Modify_files $sec_branch
	docker-compose -f /app/testenv/$branch/docker-compose.* up
	docker-compose -f /app/testenv/$sec_branch/docker-compose.* up
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

# Run tests
Test(){
	echo "running E2E tests"
	return 0
}

# Approve(){
# 	curl --request POST \
#      --url "$url/reviews" \
#      --header "Authorization: Bearer $GITHUB_TOKEN" \
#      --header "Content-Type: application/json" \
#      --data '{
#        "event": "APPROVE",
#        "body": "LGTM"
#      }'
# }

Terminate_testing(){
	echo "Terminating test envoirment"
	docker-compose -f /app/testenv/$branch/docker-compose.yml down --rmi all
	docker-compose -f /app/testenv/$sec_branch/docker-compose.yml down --rmi all
	rm -r /app/testenv/*
}

if [ "$branch" = "billing" ] || [ "$branch" = "weight" ]; then
	Clone
	cp -r /app/$sec_branch /app/testenv
	Build
	result=$(Test)
	if Test; then
		echo "Test passed, approving request"
		#send mail to devops team
	else
		echo "Test failed"
		#send mail to devs
	fi
	Terminate_testing	
fi


