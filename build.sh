#!/bin/sh

# TEAM_1=weight
# TEAM_2=biling
GIT_REPO=Blueteam

branch=$1

Clone(){
	echo "Cloning repo ..."
	git clone -b $branch 'https://github.com/Blueteam2023/Blueteam.git'
	cd $GIT_REPO
}

Build(){
	echo "Building images ..."
	docker-compose  up 
	return $?
}

if [ "$branch" = "billing" ]; then
    echo "building billing image"
elif [ "$branch" = "weight" ]; then
    echo "building weight image"
elif [ "$branch" = "devops" ]; then 
    echo "building devops image"
	Clone
fi


###Create Dir###
# CreateDir(){
# 	MY_PATH=$1
# 	mkdir -p $MY_PATH
# 	cd $MY_PATH
# }

###Clone  branch repo###

# Clone(){

#     echo "Cloning repo ..."
# 	git clone -b $1 'https://github.com/Blueteam2023/Blueteam.git'
# 	cd $GIT_REPO
# }

# Build(){
# 	echo "Building images ..."
# 	docker-compose -f $TEAM_1/docker-compose.yml up -d 
# 	return $?
# }
