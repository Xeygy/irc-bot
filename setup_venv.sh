#!/bin/bash

# Create a virtual environment
python3.9 -m venv venv

if [ ! -d "venv" ]; then
  echo "Failed to create virtual environment. Exiting..."
  exit 1
fi

# Activate the virtual environment
source venv/bin/activate

# Install the required package
pip install urllib3==1.26.6
pip install nltk
pip install pandas
pip install requests 
pip install thefuzz
pip install beautifulsoup4