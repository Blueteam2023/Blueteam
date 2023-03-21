#!/bin/bash

function parse_yaml {
    local prefix=$2
    local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @ | tr @ '\034')
    sed -ne "s|^\($s\):|\1|" \
        -e "s|^\($s\)\($w\)$s:$s[\"']\(.*\)[\"']$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p" $1 |
        awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}

export MYSQL_ROOT_PASSWORD=$(parse_yaml ./config.yaml | grep "database_password" | cut -d"=" -f2 | sed "s/\"//g")
export MYSQL_HOST=$(parse_yaml ./config.yaml | grep "database_host" | cut -d"=" -f2 | sed "s/\"//g")
export MYSQL_DB_NAME=$(parse_yaml ./config.yaml | grep "database_database" | cut -d"=" -f2 | sed "s/\"//g")
export MYSQL_USER=$(parse_yaml ./config.yaml | grep "database_user" | cut -d"=" -f2 | sed "s/\"//g")
docker compose up -d
