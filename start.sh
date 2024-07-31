#!/bin/bash

export FLASK_APP=main.py

# start python script
python3 /python-docker/get_hospo_data_from_api.py
python3 -m flask run --host=0.0.0.0