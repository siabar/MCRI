#!/usr/bin/env bash
if [ -z "$1" ] || [ -z "$2" ]
  then
    echo "No arguments supplied"
    echo "Enter one path for RFV directory as an input and one path for ouput directory"
    echo "For example: bash run-docker.sh /data/RFV /data/output"
else
  export INPUT_DIR=$1 #RFV Directory
  export OUTPUT_DIR=$2 #OUTPUT Directory
  docker run --network mcri_ontoserver --name rfv_predict -t -d -v $INPUT_DIR:/MCRI/input/ -v $OUTPUT_DIR:/MCRI/output readbiomed/mcri_rfv
fi