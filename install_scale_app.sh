#!/bin/bash
set -e

echo "Updating system..."
sudo apt update

echo "Installing system packages..."
sudo apt install -y python3-venv python3-tk python3-rpi-lgpio

echo "Creating project folder..."
mkdir -p /home/pi/scale_project

echo "Copying files..."
cp scale_app.py /home/pi/scale_project/scale_app.py
cp scale-app.desktop /home/pi/.config/autostart/scale-app.desktop

echo "Creating virtual environment..."
cd /home/pi/scale_project
python3 -m venv --system-site-packages env

echo "Activating environment and installing HX711..."
source env/bin/activate
pip install --upgrade pip
pip install hx711

echo "Making script executable..."
chmod +x /home/pi/scale_project/scale_app.py

echo "Installation complete!"
echo "Reboot the Pi to test:"
echo "sudo reboot"