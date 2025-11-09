#!/usr/bin/env python3
"""
Satellite Detection Stub Service

Simulates satellite alerts for testing the UAV event analysis system.
Generates realistic alerts for different scenarios:
- Search and Rescue (SAR)
- Border surveillance
- Wildfire detection
- Illegal activity monitoring
"""

import os
import sys
import time
import random
import requests
import psycopg2
from datetime import datetime
from typing import List, Dict

API_URL = os.getenv("API_URL", "http://api:8000")
DATABASE_URL = os.getenv("DATABASE_URL")
SCENARIO = os.getenv("SCENARIO", "mixed")  # mixed, sar, border, fire
ALERT_COUNT = int(os.getenv("ALERT_COUNT", "10"))
INTERVAL = int(os.getenv("ALERT_INTERVAL", "30"))  # seconds

# Event type configurations
EVENT_TYPES = {
    "sar": {
        "types": ["person_detected", "camp_detected", "signal_detected"],
        "priorities": [8, 7, 9],
        "confidences": [0.7, 0.9],
    },
    "border": {
        "types": ["vehicle_detected", "group_detected", "movement_detected"],
        "priorities": [9, 8, 7],
        "confidences": [0.75, 0.95],
    },
    "fire": {
        "types": ["fire_detected", "smoke_detected", "thermal_anomaly"],
        "priorities": [10, 8, 9],
        "confidences": [0.8, 0.95],
    },
    "surveillance": {
        "types": ["person_detected", "vehicle_detected", "structure_detected"],
        "priorities": [6, 7, 5],
        "confidences": [0.6, 0.9],
    }
}


def get_available_tiles() -> List[Dict]:
    """Fetch available tiles from database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tile_id, center_lat, center_lon, priority, status
            FROM tiles
            WHERE status IN ('unmonitored', 'monitored')
            ORDER BY RANDOM()
            LIMIT 50
        """)
        
        tiles = []
        for row in cursor.fetchall():
            tiles.append({
                "tile_id": row[0],
                "center_lat": row[1],
                "center_lon": row[2],
                "priority": row[3],
                "status": row[4]
            })
        
        cursor.close()
        conn.close()
        
        return tiles
    
    except Exception as e:
        print(f"❌ Error fetching tiles: {e}")
        return []


def generate_alert(tile: Dict, scenario: str) -> Dict:
    """Generate a realistic satellite alert."""
    
    # Select event type based on scenario
    if scenario == "mixed":
        scenario = random.choice(list(EVENT_TYPES.keys()))
    
    event_config = EVENT_TYPES[scenario]
    event_type = random.choice(event_config["types"])
    priority_idx = event_config["types"].index(event_type)
    priority = event_config["priorities"][priority_idx]
    
    # Generate confidence
    min_conf, max_conf = event_config["confidences"]
    confidence = random.uniform(min_conf, max_conf)
    
    # Add some random offset to position
    lat_offset = random.uniform(-0.01, 0.01)
    lon_offset = random.uniform(-0.01, 0.01)
    
    alert = {
        "tile_id": tile["tile_id"],
        "event_type": event_type,
        "priority": priority,
        "confidence": round(confidence, 3),
        "latitude": tile["center_lat"] + lat_offset,
        "longitude": tile["center_lon"] + lon_offset,
        "severity": "high" if priority >= 8 else "medium" if priority >= 5 else "low",
        "metadata": {
            "scenario": scenario,
            "satellite": f"SAT-{random.randint(1, 5)}",
            "timestamp": datetime.utcnow().isoformat(),
            "resolution_m": random.randint(1, 5),
            "cloud_cover": random.randint(0, 30),
        }
    }
    
    return alert


def post_alert(alert: Dict) -> bool:
    """Post alert to API."""
    try:
        response = requests.post(
            f"{API_URL}/api/v1/sat/alerts",
            json=alert,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Alert posted: {alert['event_type']} at {alert['tile_id']} (priority={alert['priority']})")
            return True
        else:
            print(f"❌ Failed to post alert: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error posting alert: {e}")
        return False


def run_continuous_mode():
    """Run in continuous mode, generating alerts at intervals."""
    print("=" * 60)
    print("Satellite Detection Stub - Continuous Mode")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print(f"Scenario: {SCENARIO}")
    print(f"Alert Interval: {INTERVAL}s")
    print()
    
    # Wait for API to be ready
    print("Waiting for API to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API is ready")
                break
        except:
            pass
        
        if i == max_retries - 1:
            print("❌ API not available after 30 attempts")
            sys.exit(1)
        
        time.sleep(2)
    
    # Get available tiles
    print("\nFetching available tiles...")
    tiles = get_available_tiles()
    
    if not tiles:
        print("❌ No tiles available")
        sys.exit(1)
    
    print(f"✅ Found {len(tiles)} tiles")
    print()
    
    # Generate alerts continuously
    alert_num = 0
    while True:
        tile = random.choice(tiles)
        alert = generate_alert(tile, SCENARIO)
        
        if post_alert(alert):
            alert_num += 1
        
        print(f"Alerts posted: {alert_num}")
        print(f"Next alert in {INTERVAL}s...")
        print()
        
        time.sleep(INTERVAL)


def run_batch_mode():
    """Run in batch mode, generating a fixed number of alerts."""
    print("=" * 60)
    print("Satellite Detection Stub - Batch Mode")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print(f"Scenario: {SCENARIO}")
    print(f"Alert Count: {ALERT_COUNT}")
    print()
    
    # Wait for API
    print("Waiting for API to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API is ready")
                break
        except:
            pass
        
        if i == max_retries - 1:
            print("❌ API not available")
            sys.exit(1)
        
        time.sleep(2)
    
    # Get tiles
    print("\nFetching tiles...")
    tiles = get_available_tiles()
    
    if not tiles:
        print("❌ No tiles available")
        sys.exit(1)
    
    print(f"✅ Found {len(tiles)} tiles")
    print()
    
    # Generate batch
    print(f"Generating {ALERT_COUNT} alerts...")
    success_count = 0
    
    for i in range(ALERT_COUNT):
        tile = random.choice(tiles)
        alert = generate_alert(tile, SCENARIO)
        
        if post_alert(alert):
            success_count += 1
        
        time.sleep(1)  # Small delay between alerts
    
    print()
    print("=" * 60)
    print(f"✅ Batch complete: {success_count}/{ALERT_COUNT} alerts posted successfully")
    print("=" * 60)


def main():
    """Main execution."""
    mode = os.getenv("MODE", "batch")  # batch or continuous
    
    if mode == "continuous":
        run_continuous_mode()
    else:
        run_batch_mode()


if __name__ == "__main__":
    main()
