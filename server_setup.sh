#!/bin/bash
# Server Setup Script for EOD Reports
# Run this on the EC2 instance

set -e
echo "=========================================="
echo "EOD Reports Server Setup"
echo "=========================================="
echo ""

# Update system
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install Python and dependencies
echo "🐍 Installing Python 3.8 and dependencies..."
sudo apt install -y python3.8 python3.8-venv python3.8-dev python3-pip
sudo apt install -y build-essential libssl-dev libffi-dev

# Install PostgreSQL
echo "🐘 Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib libpq-dev

# Install Nginx
echo "🌐 Installing Nginx..."
sudo apt install -y nginx

# Install Git
echo "📂 Installing Git..."
sudo apt install -y git

# Verify installations
echo ""
echo "✅ Verifying installations..."
python3.8 --version
psql --version
nginx -v
git --version

echo ""
echo "✅ System setup complete!"
echo ""
