#!/bin/bash
set -e

echo "Updating system..."
sudo apt update

echo "Installing system packages..."
sudo apt install -y python3-venv python3-tk python3-rpi-lgpio

echo "Creating project folder..."
mkdir -p "$HOME/scale_project"
mkdir -p "$HOME/.config/autostart"

echo "Copying files..."
cp scale_app.py "$HOME/scale_project/scale_app.py"
cp calibrate_raw.py "$HOME/scale_project/calibrate_raw.py"
cp scale-app.desktop "$HOME/.config/autostart/scale-app.desktop"

echo "Creating virtual environment..."
cd "$HOME/scale_project"
python3 -m venv --system-site-packages env

echo "Activating environment and installing HX711..."
source env/bin/activate
pip install --upgrade pip
pip install hx711

echo "Making scripts executable..."
chmod +x "$HOME/scale_project/scale_app.py"
chmod +x "$HOME/scale_project/calibrate_raw.py"

echo "Installation complete!"
echo "Run with:"
echo "cd ~/scale_project && source env/bin/activate && python scale_app.py"
