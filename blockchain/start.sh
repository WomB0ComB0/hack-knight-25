#!/bin/bash

touch start.log
chmod +x start.log
LOGFILE="start.log"

# Create or clear the log file
: > $LOGFILE

# Log the start time
echo "Script started at $(date)" | tee -a $LOGFILE

# Create virtual environment
python3 -m venv venv 2>&1 | tee -a $LOGFILE

# Install requirements
source venv/bin/activate
pip install -r requirements.txt 2>&1 | tee -a $LOGFILE

# Install additional healthcare-specific packages
pip install cryptography fernet pyjwt 2>&1 | tee -a $LOGFILE

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export HEALTHCARE_BLOCKCHAIN=true

# Log environment variables
echo "FLASK_APP=$FLASK_APP" | tee -a $LOGFILE
echo "FLASK_ENV=$FLASK_ENV" | tee -a $LOGFILE
echo "HEALTHCARE_BLOCKCHAIN=$HEALTHCARE_BLOCKCHAIN" | tee -a $LOGFILE

# Run the Flask application
flask run 2>&1 | tee -a $LOGFILE