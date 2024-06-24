#!/bin/bash
echo "Building Docker image..."
docker build -t model .
echo "Running Docker container..."
docker run -it --rm model
