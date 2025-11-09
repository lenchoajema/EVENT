#!/usr/bin/env python3
"""
Seed initial geographic tiles for satellite monitoring.
This creates a grid of tiles covering areas of interest for defense, surveillance, and SAR operations.
"""

import os
import sys
import psycopg2
from psycopg2.extras import execute_values
import random
from datetime import datetime

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'postgres'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'mvp'),
    'user': os.getenv('POSTGRES_USER', 'mvp'),
    'password': os.getenv('POSTGRES_PASSWORD', 'mvp')
}

# Sample geographic areas of interest (AOIs)
AREAS_OF_INTEREST = [
    # Border surveillance zones
    {'name': 'Border Zone Alpha', 'center': (31.7683, -106.4850), 'size': 0.1},  # US-Mexico border
    {'name': 'Border Zone Bravo', 'center': (32.5331, -117.0183), 'size': 0.1},
    
    # Forest/wilderness areas (SAR operations)
    {'name': 'Pacific Northwest Forest', 'center': (47.7511, -120.7401), 'size': 0.2},
    {'name': 'Sierra Nevada Range', 'center': (37.7749, -119.4179), 'size': 0.2},
    {'name': 'Appalachian Forest', 'center': (35.6532, -83.5070), 'size': 0.15},
    
    # Coastal zones (maritime surveillance)
    {'name': 'Gulf Coast Zone', 'center': (29.7604, -95.3698), 'size': 0.15},
    {'name': 'Atlantic Coast Zone', 'center': (38.9072, -77.0369), 'size': 0.15},
    
    # Desert regions (border/illegal activity)
    {'name': 'Sonoran Desert', 'center': (32.2540, -110.9742), 'size': 0.2},
    {'name': 'Mojave Desert', 'center': (35.0456, -115.4734), 'size': 0.2},
    
    # Mountain regions (SAR)
    {'name': 'Rocky Mountains', 'center': (39.7392, -104.9903), 'size': 0.2},
]

def create_tile_grid(center_lat, center_lon, tile_size, grid_size=3):
    """
    Create a grid of tiles around a center point.
    
    Args:
        center_lat: Center latitude
        center_lon: Center longitude
        tile_size: Size of each tile in degrees
        grid_size: Number of tiles in each direction (e.g., 3x3 grid)
    
    Returns:
        List of tile dictionaries
    """
    tiles = []
    half_grid = grid_size // 2
    
    for i in range(-half_grid, half_grid + 1):
        for j in range(-half_grid, half_grid + 1):
            lat_offset = i * tile_size
            lon_offset = j * tile_size
            
            tile_lat = center_lat + lat_offset
            tile_lon = center_lon + lon_offset
            
            # Create polygon corners (clockwise from SW)
            sw = (tile_lon - tile_size/2, tile_lat - tile_size/2)
            se = (tile_lon + tile_size/2, tile_lat - tile_size/2)
            ne = (tile_lon + tile_size/2, tile_lat + tile_size/2)
            nw = (tile_lon - tile_size/2, tile_lat + tile_size/2)
            
            # Create WKT polygon
            polygon_wkt = f"POLYGON(({sw[0]} {sw[1]}, {se[0]} {se[1]}, {ne[0]} {ne[1]}, {nw[0]} {nw[1]}, {sw[0]} {sw[1]}))"
            
            tiles.append({
                'center_lat': tile_lat,
                'center_lon': tile_lon,
                'polygon': polygon_wkt,
                'priority': random.randint(1, 5)
            })
    
    return tiles

def seed_tiles(conn):
    """Seed tiles into the database."""
    cursor = conn.cursor()
    
    # Clear existing tiles
    print("Clearing existing tiles...")
    cursor.execute("DELETE FROM tiles")
    
    all_tiles = []
    tile_counter = 1
    
    # Generate tiles for each area of interest
    for aoi in AREAS_OF_INTEREST:
        print(f"Generating tiles for {aoi['name']}...")
        center_lat, center_lon = aoi['center']
        tile_size = aoi['size']
        
        tiles = create_tile_grid(center_lat, center_lon, tile_size)
        
        for tile in tiles:
            tile_id = f"TILE_{tile_counter:04d}"
            all_tiles.append((
                tile_id,
                tile['polygon'],
                tile['center_lat'],
                tile['center_lon'],
                tile['priority'],
                'unmonitored'
            ))
            tile_counter += 1
    
    # Insert tiles
    print(f"Inserting {len(all_tiles)} tiles...")
    insert_query = """
        INSERT INTO tiles (tile_id, geometry, center_lat, center_lon, priority, status)
        VALUES %s
    """
    
    execute_values(
        cursor,
        insert_query,
        all_tiles,
        template="(%s, ST_GeomFromText(%s, 4326), %s, %s, %s, %s)"
    )
    
    conn.commit()
    print(f"✅ Successfully seeded {len(all_tiles)} tiles")
    
    # Print summary
    cursor.execute("SELECT status, COUNT(*) FROM tiles GROUP BY status")
    results = cursor.fetchall()
    print("\nTile Summary:")
    for status, count in results:
        print(f"  {status}: {count}")
    
    cursor.close()

def seed_sample_uavs(conn):
    """Seed sample UAVs for testing."""
    cursor = conn.cursor()
    
    # Clear existing UAVs
    print("\nClearing existing UAVs...")
    cursor.execute("DELETE FROM uavs")
    
    # Create sample UAVs distributed across AOIs
    sample_uavs = []
    for i in range(10):
        uav_id = f"UAV_{i+1:03d}"
        
        # Randomly assign to an AOI
        aoi = random.choice(AREAS_OF_INTEREST)
        lat, lon = aoi['center']
        
        # Add some random offset
        lat += random.uniform(-0.05, 0.05)
        lon += random.uniform(-0.05, 0.05)
        
        sample_uavs.append((
            uav_id,
            f"{aoi['name']} UAV {i+1}",
            lat,
            lon,
            random.uniform(50, 100),  # battery level
            'available'
        ))
    
    insert_query = """
        INSERT INTO uavs (uav_id, name, latitude, longitude, battery_level, status)
        VALUES %s
    """
    
    execute_values(
        cursor,
        insert_query,
        sample_uavs,
        template="(%s, %s, %s, %s, %s, %s)"
    )
    
    # Update positions using PostGIS
    cursor.execute("""
        UPDATE uavs 
        SET position = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
        WHERE position IS NULL
    """)
    
    conn.commit()
    print(f"✅ Successfully seeded {len(sample_uavs)} UAVs")
    
    # Print summary
    cursor.execute("SELECT status, COUNT(*), AVG(battery_level) FROM uavs GROUP BY status")
    results = cursor.fetchall()
    print("\nUAV Fleet Summary:")
    for status, count, avg_battery in results:
        print(f"  {status}: {count} UAVs (avg battery: {avg_battery:.1f}%)")
    
    cursor.close()

def main():
    """Main execution function."""
    print("=" * 60)
    print("UAV-Satellite Event Analysis - Tile Seeding Script")
    print("=" * 60)
    print()
    
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Connected successfully")
        
        # Seed tiles
        seed_tiles(conn)
        
        # Seed sample UAVs
        seed_sample_uavs(conn)
        
        conn.close()
        print("\n" + "=" * 60)
        print("✅ Seeding completed successfully!")
        print("=" * 60)
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
