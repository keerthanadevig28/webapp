#!/bin/bash
set -e

echo "=== Starting setup script ==="

# Update system
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

# Install Python 3.12 and pip
sudo apt-get install -y python3.12 python3.12-venv python3-pip

# Install PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Wait for PostgreSQL to be ready
sudo -u postgres psql -c "SELECT 1" > /dev/null 2>&1 || sleep 5

# Create application database user and database
echo "=== Creating database and user ==="
sudo -u postgres psql -c "CREATE USER keerthanadevigovindaraj WITH PASSWORD 'password123';" || true
sudo -u postgres psql -c "CREATE DATABASE webapp_db OWNER keerthanadevigovindaraj;" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE webapp_db TO keerthanadevigovindaraj;" || true

# Create csye6225 user and group
echo "=== Creating csye6225 user ==="
sudo groupadd -f csye6225
sudo useradd -r -g csye6225 -s /usr/sbin/nologin csye6225 || true

# Create application directory
echo "=== Setting up application directory ==="
sudo mkdir -p /opt/webapp
sudo chown csye6225:csye6225 /opt/webapp

# Create virtual environment
echo "=== Creating virtual environment ==="
sudo -u csye6225 python3.12 -m venv /opt/webapp/venv

echo "=== Setup script completed ==="

chmod +x packer/scripts/setup.sh