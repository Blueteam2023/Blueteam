#!/bin/sh

set -e #exit if a command fails

GIT_REPO=Blueteam

branch=$1

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
	cd /app/testenv/$branch/$GIT_REPO/$branch/
	sed -i "s/blueteam/container_name:testing/" docker-compose.*
	docker-compose -f /app/testenv/$branch/$GIT_REPO/$branch/docker-compose.* up 
	return $?
}

# Run tests
test(){
	echo "running E2E tests"
}

if [ "$branch" = "billing" ] || [ "$branch" = "weight" ]; then
    echo "building $branch image"
	deploy
	build
	test
elif [ "$branch" = "devops" ]; then  # testing porpuses
    echo "building devops image"
	deploy
	build
	test
fi


