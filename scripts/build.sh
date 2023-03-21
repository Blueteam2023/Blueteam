#!/bin/sh

set -e #exit if a command fails

GIT_REPO=Blueteam

branch=$1
billing_port=8087
weight_port=8088


#Function to search and delete directory 
deleteDirectory() {
	if [ -d "$GIT_REPO" ]; then
		echo "Deleting existing directory ..."
		rm -rf "$GIT_REPO"
	fi
}

clearExists(){
	if docker ps -a | grep test-$branch-app > /dev/null; then
		docker rm -f test-$branch-app
	fi
	if docker ps -a | grep test-$branch-db > /dev/null; then
		docker rm -f test-$branch-db
	fi
}

# Clone
deploy(){
	echo "Cloning repo from $branch"
	cd testenv/$branch
	deleteDirectory
	git clone -b $branch 'https://github.com/Blueteam2023/Blueteam.git'
}


# Docker-compose
build(){
	echo "Building $branch images"
	echo /app/testenv/$branch/$GIT_REPO/$branch/prod.env > /app/testenv/$branch/$GIT_REPO/$branch/test.env
	sed -i "s/DB_HOST=*/DB_HOST=test-$branch-db/" test.env
	#sed -i 's//container_name: new_container_name/' docker-compose.yml
	docker-compose --env-file test.env -f /app/testenv/$branch/$GIT_REPO/$branch/docker-compose.* up --build
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
test(){
	echo "running E2E tests"
}

if [ "$branch" = "billing" ] || [ "$branch" = "weight" ]; then
    echo "building $branch image"
	deploy
	build
	#health_check
	test
elif [ "$branch" = "devops" ]; then  # testing porpuses
    echo "building devops image"
	deploy
	build
	#health_check
	test
fi


