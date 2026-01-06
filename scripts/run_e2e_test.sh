#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting End-to-End Test Sequence${NC}"

# 1. Build and Start Services
echo "Building and starting services..."
docker compose build api dashboard
docker compose up -d postgres redis mosquitto api

# 2. Wait for API Health
echo "Waiting for API to be healthy..."
RETRIES=30
while [ $RETRIES -gt 0 ]; do
    if curl -s http://localhost:8000/health | grep "healthy" > /dev/null; then
        echo -e "${GREEN}API is healthy!${NC}"
        break
    fi
    echo -n "."
    sleep 2
    RETRIES=$((RETRIES-1))
done

if [ $RETRIES -eq 0 ]; then
    echo -e "${RED}API failed to become healthy.${NC}"
    docker compose logs api
    exit 1
fi

# 3. initialize DB (if needed, usually handled by init container or app startup)
# docker compose exec -T api python scripts/init_db.py

# 4. Run E2E Tests
echo "Running E2E Tests..."
# We run the test script using the python environment in the api container
# or locally if we have dependencies installed.
# Using 'docker compose exec' ensures network visibility typically, 
# but here the test script is local.
# We'll run pytest locally, pointing to localhost:8000
export API_URL=http://localhost:8000
pytest tests/test_e2e_full.py -v

TEST_EXIT_CODE=$?

# 5. Cleanup (Optional)
if [ "$1" == "--cleanup" ]; then
    echo "Cleaning up..."
    docker compose down
fi

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}E2E Tests Passed!${NC}"
    exit 0
else
    echo -e "${RED}E2E Tests Failed!${NC}"
    exit 1
fi
