#!/bin/bash

# Stop and clean up all services

echo "Stopping all services..."
docker-compose down

echo "Removing volumes (this will delete all data)..."
docker-compose down -v

echo "Cleanup complete!"
