#!/bin/bash

# This script creates a Python virtual environment and installs the required packages

# Set the virtual environment name
VENV_NAME="venv_v4"
DIR="/home/pi"

# Create the virtual environment
cd $DIR

# Remove the env if it already exists
[ ! -d './$VENV_NAME' ] && rm -Rf "$DIR/$VENV_NAME"

echo "Initializing Python virtual environment in ${DIR}/${VENV_NAME}"
python3 -m venv "$VENV_NAME"

# Activate the venv and install some dependencies
echo 'Installing pip setuptools into the virtual environment'
source "$VENV_NAME/bin/activate"
export CFLAGS=-fcommon
pip install setuptools | sed 's/^/     /'

# Install requirements.txt pip packages
echo 'Installing requirements.txt dependencies into the Virtual Environment'
source "$VENV_NAME/bin/activate"
pip install -r sg1_v4/requirements.txt | sed 's/^/     /'

echo 'Deactivating the virtual environment'
deactivate