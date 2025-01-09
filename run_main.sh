#!/bin/bash

# Wait for 30 seconds to allow other services to initialize
sleep 30

# Navigate to the project directory
cd /ricochet-dev || exit

# Pull the latest changes from the GitHub repository
git pull origin main

# Run the main.py script
python3 main.py
