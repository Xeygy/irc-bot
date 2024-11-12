#!/bin/bash

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the required package
pip install -U google-generativeai
pip install urllib3==1.26.6
