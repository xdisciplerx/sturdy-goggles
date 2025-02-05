#!/bin/bash

# Update and upgrade the system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required dependencies
echo "Installing required dependencies..."
sudo apt install -y python3 python3-pip python3-venv git ffmpeg

# Clone the repository
echo "Cloning the Travel Twitter Bot repository..."
git clone https://github.com/xdisciplerx/sturdy-goggles.git
cd sturdy-goggles

# Create a virtual environment and activate it
echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file for credentials
echo "Configuring environment variables..."
cat <<EOT > .env
API_KEY=
API_SECRET=
ACCESS_TOKEN=
ACCESS_SECRET=
OPENAI_API_KEY=
UNSPLASH_ACCESS_KEY=
EOT

echo "Environment variables set. Please edit the .env file and add your API credentials."

# Run the Flask application
echo "Starting the web interface..."
python app.py &

# Print final message
echo "Installation complete. Access the dashboard at: http://127.0.0.1:5000"
