#! /bin/bash

echo ">>> Installing virtual environment tool ..."
python -m pip install --user virtualenv

echo ">>> Creating virtual environment on /env ..."
python -m venv env

echo ">>> Activating virtual environment ..."
. env/bin/activate

echo ">>> Installing dependencies (./requirements.txt) ..."
pip install -r requirements.txt

echo ">>> All set!"
