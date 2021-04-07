#!/bin/bash
if [ $1 != "" ]
    then
        docker run --rm -v "${PWD}":/config -it esphome/esphome "$1" run --no-logs
    else
        echo "no device config given"
fi