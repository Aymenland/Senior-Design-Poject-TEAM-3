	#!/usr/bin/bash

python3 -m venv env
source ./env/bin/activate 
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
