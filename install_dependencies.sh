#!/bin/bash

echo "Creating virtual environment..."
python -m venv env

echo "Activating virtual environment..."
source env/bin/activate

echo "Updating pip inside the virtual environment..."
pip install --upgrade pip

echo "Installing API requirements..."
pip install -r requirements.txt

echo "Installation completed."
read -p "Press Enter to exit..."

