#!/bin/sh

set -e #exit if a command fails

GIT_REPO=Blueteam

branch=$1
pusher=$2

if [ "$branch" = "billing" ]; then
	sec_branch="weight"
elif [ "$branch" = "weight" ]; then
	sec_branch="billing"
fi

# PRODIR=

# TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)

# COM_DIR=

Stop_production(){
    echo "Stopping production for update"
    docker-compose -f /app/$branch/docker-compose.* down --rmi all
    docker stop $sec_branch-app
}

Build(){
    echo "Building new version"
    docker-compose -f /app/$branch/docker-compose.* up --build
    docker start $sec_branch-app
}

Stop_production
cd /app/
git pull 
Build
# Test health
echo "Deploy succses"
# Mail to devops sucssed



# health_check(){
# 	if [[ $branch == "billing" ]]; then
# 		port=8081
# 	elif [[ $branch == "weight" ]]; then
# 		port=8082
# 	else
# 		echo "branch not found"
# 	fi
# 	response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health)
# 	if [ "$response" -eq 200 ]; then
#     	return 0
# 	else
# 		return 1
# 	fi
# }
