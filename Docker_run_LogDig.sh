#!/usr/bin/env bash

if [ -z "$1" ]
then 
	echo "No BML-file (without .py extension) supplied"
	exit
fi
if [ -z "$2" ]
then 
	echo "No logfiles directory (under ${HOST_LA_PATH}/LogFile/PreProsessed/) supplied"
	exit
fi
BML_FILE=$1
LOGFILES_DIR=$2
#BML_FILE="ITS_4_back"

#HOST_LA_PATH="/home/esa/projects/LA"
HOST_LA_PATH="${PWD}"
CONTAINER_LA_PATH="/home/LA"

#docker volume create logdig-results

echo "Runs the logdig container"
echo ""

#docker run  --rm --name logdig \
docker run  --name logdig \
			-v ${HOST_LA_PATH}/LogFile/PreProsessed/${LOGFILES_DIR}:${CONTAINER_LA_PATH}/LogFile \
			-v ${HOST_LA_PATH}/LogAna/${BML_FILE}.py:${CONTAINER_LA_PATH}/LogAna/${BML_FILE}.py \
		    logdig:v1 \
		    ${CONTAINER_LA_PATH}/LogDig/start.sh $BML_FILE

			#--mount source=logdig-results,target=${CONTAINER_LA_PATH}/LogRes 

echo ""
echo "Copy ${BML_FILE} results from the logdig container to host path: ${HOST_LA_PATH}/LogRes/"
docker cp logdig:${CONTAINER_LA_PATH}/LogRes ${HOST_LA_PATH}

#docker volume rm logdig-results

echo "Stops the logdig container"
docker container stop logdig
echo "Removes the logdig container"
docker container rm logdig
