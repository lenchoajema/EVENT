#!/bin/bash
# Push Docker images to GitHub Container Registry
# Requires authentication: docker login ghcr.io -u USERNAME

set -e

VERSION="1.0.0"
REGISTRY="ghcr.io/lenchoajema/event"

echo "📦 Pushing EVENT v${VERSION} images to GitHub Container Registry..."
echo "===================================================================="

# Check if logged in
if ! docker info | grep -q "Username:"; then
    echo "⚠️  Not logged in to Docker registry"
    echo "Please run: docker login ghcr.io -u <your-github-username>"
    exit 1
fi

# Push all images (versioned and latest tags)
echo "Pushing images..."

docker push ${REGISTRY}-api:${VERSION}
docker push ${REGISTRY}-api:latest

docker push ${REGISTRY}-dashboard:${VERSION}
docker push ${REGISTRY}-dashboard:latest

docker push ${REGISTRY}-scheduler:${VERSION}
docker push ${REGISTRY}-scheduler:latest

docker push ${REGISTRY}-uav-sim:${VERSION}
docker push ${REGISTRY}-uav-sim:latest

docker push ${REGISTRY}-edge-infer:${VERSION}
docker push ${REGISTRY}-edge-infer:latest

docker push ${REGISTRY}-detection-stub:${VERSION}
docker push ${REGISTRY}-detection-stub:latest

echo ""
echo "✅ All images pushed successfully!"
echo ""
echo "Images available at:"
echo "  ${REGISTRY}-api:${VERSION}"
echo "  ${REGISTRY}-dashboard:${VERSION}"
echo "  ${REGISTRY}-scheduler:${VERSION}"
echo "  ${REGISTRY}-uav-sim:${VERSION}"
echo "  ${REGISTRY}-edge-infer:${VERSION}"
echo "  ${REGISTRY}-detection-stub:${VERSION}"
