#!/bin/sh

set -e #exit if a command fails

GIT_REPO=Blueteam

branch=$1

# PRODIR=

# TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)

# COM_DIR=


git pull 

docker-compose -f /app/$branch/docker-compose.* up --build

# health_check(){
# 	if [[ $branch == "billing" ]]; then
# 		port=8087
# 	elif [[ $branch == "weight" ]]; then
# 		port=8088
# 	elif [[ $branch == "devops" ]]; then
# 		port=8089
# 	else
# 		echo "branch not found"
# 	fi
# 	response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health)
# 	if [ "$response" -eq 200 ]; then
#     	return True
# 	else
# 		return False
# 	fi
# }
