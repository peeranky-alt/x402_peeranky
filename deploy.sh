#!/bin/bash
echo "Starting deployment..."

# move into project directory (Render auto sets it)
cd $(dirname "$0")

# install dependencies
pip install -r requirements.txt

# run main app
python3 app.py
