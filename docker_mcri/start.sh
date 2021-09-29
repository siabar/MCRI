#!/bin/sh
cd /metamap/public_mm
./metamap/public_mm/bin/skrmedpostctl start
cd /MCRI/src
python3 predict.py
