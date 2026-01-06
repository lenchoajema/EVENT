#!/bin/bash
# Build and tag Docker images for release v1.0.0
# This script builds all service images and tags them for GitHub Container Registry

set -e

VERSION="1.0.0"
REGISTRY="ghcr.io/lenchoajema/event"

echo "🚀 Building EVENT v${VERSION} Docker images..."
echo "================================================"

# Build all images using docker-compose
echo "Building images with docker-compose..."
docker-compose build

# Tag images for GitHub Container Registry
echo ""
echo "Tagging images for registry: ${REGISTRY}"

# API Service
docker tag event-api:latest ${REGISTRY}-api:${VERSION}
docker tag event-api:latest ${REGISTRY}-api:latest

# Dashboard Service
docker tag event-dashboard:latest ${REGISTRY}-dashboard:${VERSION}
docker tag event-dashboard:latest ${REGISTRY}-dashboard:latest

# Scheduler Service
docker tag event-scheduler:latest ${REGISTRY}-scheduler:${VERSION}
docker tag event-scheduler:latest ${REGISTRY}-scheduler:latest

# UAV Simulator Service
docker tag event-uav-sim:latest ${REGISTRY}-uav-sim:${VERSION}
docker tag event-uav-sim:latest ${REGISTRY}-uav-sim:latest

# Edge Inference Service
docker tag event-edge-infer:latest ${REGISTRY}-edge-infer:${VERSION}
docker tag event-edge-infer:latest ${REGISTRY}-edge-infer:latest

# Detection Stub Service
docker tag event-detection-stub:latest ${REGISTRY}-detection-stub:${VERSION}
docker tag event-detection-stub:latest ${REGISTRY}-detection-stub:latest

echo ""
echo "✅ All images built and tagged successfully!"
echo ""
echo "Tagged images:"
echo "  - ${REGISTRY}-api:${VERSION}"
echo "  - ${REGISTRY}-dashboard:${VERSION}"
echo "  - ${REGISTRY}-scheduler:${VERSION}"
echo "  - ${REGISTRY}-uav-sim:${VERSION}"
echo "  - ${REGISTRY}-edge-infer:${VERSION}"
echo "  - ${REGISTRY}-detection-stub:${VERSION}"
echo ""
echo "To push to GitHub Container Registry, run:"
echo "  docker login ghcr.io -u USERNAME"
echo "  ./scripts/push_images.sh"
