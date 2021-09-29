#!/usr/bin/env bash
if [ -z "$1" ] || [ -z "$2" ]
  then
    echo "No arguments supplied"
    echo "Enter one path for RFV directory as an input and one path for ouput directory"
    echo "For example: bash run-docker.sh $HOME/data/RFV $HOME/data/output"
else
  export INPUT_DIR=$1 #RFV Directory
  export OUTPUT_DIR=$2 #OUTPUT Directory
  docker run --rm -it -v $INPUT_DIR:/MCRI/data/ -v $OUTPUT_DIR:$OUTPUT_DIR/MCRI/output readbiomed/mcri /start.sh
fi