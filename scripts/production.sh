#!/bin/sh

set -e #exit if a command fails

GIT_REPO=Blueteam

branch=$1

PRODIR=

TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)

COM_DIR=


clearExists(){
	if docker ps -a | grep production-$branch-app > /dev/null; then
		docker rm -f production-$branch-app
	fi
	if docker ps -a | grep production-$branch-db > /dev/null; then
		docker rm -f production-$branch-db
	fi
}

build(){
    echo "Building $branch


}
