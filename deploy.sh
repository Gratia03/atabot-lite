#!/bin/bash

# Build and run with Docker
echo "Building Atabot-Lite..."
docker-compose build

echo "Starting Atabot-Lite..."
docker-compose up -d

echo "Atabot-Lite is running at http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"