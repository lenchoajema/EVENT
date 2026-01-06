#!/bin/bash
# Pull pre-built Docker images for EVENT v1.0.0 from GitHub Container Registry

set -e

VERSION="1.0.0"
REGISTRY="ghcr.io/lenchoajema/event"

echo "📥 Pulling EVENT v${VERSION} pre-built images..."
echo "=================================================="

# Pull all versioned images
docker pull ${REGISTRY}-api:${VERSION}
docker pull ${REGISTRY}-dashboard:${VERSION}
docker pull ${REGISTRY}-scheduler:${VERSION}
docker pull ${REGISTRY}-uav-sim:${VERSION}
docker pull ${REGISTRY}-edge-infer:${VERSION}
docker pull ${REGISTRY}-detection-stub:${VERSION}

# Tag as latest for docker-compose
docker tag ${REGISTRY}-api:${VERSION} event-api:latest
docker tag ${REGISTRY}-dashboard:${VERSION} event-dashboard:latest
docker tag ${REGISTRY}-scheduler:${VERSION} event-scheduler:latest
docker tag ${REGISTRY}-uav-sim:${VERSION} event-uav-sim:latest
docker tag ${REGISTRY}-edge-infer:${VERSION} event-edge-infer:latest
docker tag ${REGISTRY}-detection-stub:${VERSION} event-detection-stub:latest

echo ""
echo "✅ All images pulled and tagged successfully!"
echo ""
echo "You can now start the services with:"
echo "  docker-compose up -d"
