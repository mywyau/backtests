#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Set the PYTHONPATH to include the project root directory
export PYTHONPATH=$(pwd)

# Prompt the user for the directory
read -p "Enter the directory name (e.g., SPY, AAPL, TSLA): " DIR_NAME

# Construct the path to the main.py script in the specified directory
MAIN_SCRIPT="polygon_io/$DIR_NAME/main.py"

# Check if the main.py script exists in the specified directory
if [ ! -f "$MAIN_SCRIPT" ]; then
  echo "main.py not found in directory $DIR_NAME. Please check the directory name."
  exit 1
fi

# Run the main.py script
python3 "$MAIN_SCRIPT"

# Deactivate the virtual environment (optional)
deactivate
