#!/bin/bash
set -e

# Generate satellite alerts for different scenarios

API_URL="${API_URL:-http://localhost:8000}"
SCENARIO="${1:-mixed}"  # sar, border, fire, surveillance, mixed
COUNT="${2:-5}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "============================================================"
echo "Satellite Alert Generator"
echo "============================================================"
echo ""
echo "Scenario: ${SCENARIO}"
echo "Count: ${COUNT}"
echo ""

# Check if API is available
if ! curl -sf ${API_URL}/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  API is not available. Please start the system first.${NC}"
    exit 1
fi

# Run detection stub with batch mode
echo -e "${YELLOW}Generating ${COUNT} ${SCENARIO} alerts...${NC}"
echo ""

docker-compose run --rm \
    -e API_URL=${API_URL} \
    -e SCENARIO=${SCENARIO} \
    -e MODE=batch \
    -e ALERT_COUNT=${COUNT} \
    detection_stub

echo ""
echo -e "${GREEN}✅ Alerts generated successfully!${NC}"
echo ""
echo "View results:"
echo "  Dashboard: http://localhost:3000"
echo "  API: ${API_URL}/api/v1/sat/alerts"
echo ""

