#!/bin/sh



if [ -z "$(docker ps -q -f name=weight-app)" ] || [ -z "$(docker ps -q -f name=billing-app)" ]; then
    while [ -z "$(docker ps -q -f name=weight-app)" ] || [ -z "$(docker ps -q -f name=billing-app)" ]; do
            sleep 10
    done
fi

exec nginx -g 'daemon off;'
