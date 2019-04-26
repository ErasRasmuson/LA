#!/usr/bin/env bash
#export HOST_UID=$UID
docker build -f Dockerfile_LogDig -t logdig:v1 .
