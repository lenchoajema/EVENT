#!/bin/bash

# Initialize the event analysis system

echo "Initializing UAV-Satellite Event Analysis System..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
fi

# Build all Docker images
echo "Building Docker images..."
docker-compose build

# Start the system
echo "Starting all services..."
docker-compose up -d

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 15

# Check API health
echo "Checking API health..."
curl -f http://localhost:8000/health

# Initialize UAVs in the database
echo "Initializing UAVs..."
for i in {1..3}; do
    curl -X POST http://localhost:8000/api/uavs \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"UAV-$i\", \"current_latitude\": 37.7749, \"current_longitude\": -122.4194}"
done

echo ""
echo "System initialized successfully!"
echo "Dashboard: http://localhost:3000"
echo "API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
