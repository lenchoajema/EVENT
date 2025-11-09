-- Initialize PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create tables for UAV Event Analysis System

-- Tiles Table (Geographic areas for satellite monitoring)
CREATE TABLE IF NOT EXISTS tiles (
    id SERIAL PRIMARY KEY,
    tile_id VARCHAR(50) UNIQUE NOT NULL,
    geometry GEOMETRY(POLYGON, 4326) NOT NULL,
    center_lat DOUBLE PRECISION NOT NULL,
    center_lon DOUBLE PRECISION NOT NULL,
    priority INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'unmonitored',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial index on tiles
CREATE INDEX IF NOT EXISTS idx_tiles_geometry ON tiles USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_tiles_status ON tiles (status);
CREATE INDEX IF NOT EXISTS idx_tiles_priority ON tiles (priority DESC);

-- UAVs Table
CREATE TABLE IF NOT EXISTS uavs (
    id SERIAL PRIMARY KEY,
    uav_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    position GEOMETRY(POINT, 4326),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    altitude DOUBLE PRECISION DEFAULT 0,
    battery_level DOUBLE PRECISION DEFAULT 100.0,
    status VARCHAR(20) DEFAULT 'available',
    mission_id INTEGER,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial index on UAVs
CREATE INDEX IF NOT EXISTS idx_uavs_position ON uavs USING GIST (position);
CREATE INDEX IF NOT EXISTS idx_uavs_status ON uavs (status);
CREATE INDEX IF NOT EXISTS idx_uavs_battery ON uavs (battery_level);

-- Missions Table
CREATE TABLE IF NOT EXISTS missions (
    id SERIAL PRIMARY KEY,
    mission_id VARCHAR(50) UNIQUE NOT NULL,
    uav_id VARCHAR(50) REFERENCES uavs(uav_id),
    tile_id VARCHAR(50) REFERENCES tiles(tile_id),
    status VARCHAR(20) DEFAULT 'pending',
    priority INTEGER DEFAULT 0,
    waypoints JSON,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    estimated_duration INTEGER,
    actual_duration INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_missions_status ON missions (status);
CREATE INDEX IF NOT EXISTS idx_missions_uav ON missions (uav_id);
CREATE INDEX IF NOT EXISTS idx_missions_tile ON missions (tile_id);

-- Satellite Alerts Table
CREATE TABLE IF NOT EXISTS sat_alerts (
    id SERIAL PRIMARY KEY,
    alert_id VARCHAR(50) UNIQUE NOT NULL,
    tile_id VARCHAR(50) REFERENCES tiles(tile_id),
    alert_type VARCHAR(50) NOT NULL,
    event_type VARCHAR(50),
    confidence DOUBLE PRECISION,
    position GEOMETRY(POINT, 4326),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    severity VARCHAR(20) DEFAULT 'medium',
    priority INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'new',
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alerts_position ON sat_alerts USING GIST (position);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON sat_alerts (status);
CREATE INDEX IF NOT EXISTS idx_alerts_priority ON sat_alerts (priority DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_type ON sat_alerts (alert_type);

-- Detections Table (from UAV edge inference)
CREATE TABLE IF NOT EXISTS detections (
    id SERIAL PRIMARY KEY,
    detection_id VARCHAR(50) UNIQUE NOT NULL,
    uav_id VARCHAR(50) REFERENCES uavs(uav_id),
    mission_id VARCHAR(50) REFERENCES missions(mission_id),
    detection_type VARCHAR(50) NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    position GEOMETRY(POINT, 4326),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    bbox JSON,
    image_url VARCHAR(500),
    metadata JSON,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_detections_position ON detections USING GIST (position);
CREATE INDEX IF NOT EXISTS idx_detections_type ON detections (detection_type);
CREATE INDEX IF NOT EXISTS idx_detections_uav ON detections (uav_id);
CREATE INDEX IF NOT EXISTS idx_detections_mission ON detections (mission_id);
CREATE INDEX IF NOT EXISTS idx_detections_confidence ON detections (confidence DESC);

-- Telemetry Table (UAV real-time data)
CREATE TABLE IF NOT EXISTS telemetry (
    id SERIAL PRIMARY KEY,
    uav_id VARCHAR(50) REFERENCES uavs(uav_id),
    position GEOMETRY(POINT, 4326),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    altitude DOUBLE PRECISION,
    battery_level DOUBLE PRECISION,
    speed DOUBLE PRECISION,
    heading DOUBLE PRECISION,
    status VARCHAR(20),
    metadata JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_telemetry_uav ON telemetry (uav_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry (timestamp DESC);

-- Evidence Storage Table (links to MinIO)
CREATE TABLE IF NOT EXISTS evidence (
    id SERIAL PRIMARY KEY,
    evidence_id VARCHAR(50) UNIQUE NOT NULL,
    detection_id VARCHAR(50) REFERENCES detections(detection_id),
    mission_id VARCHAR(50) REFERENCES missions(mission_id),
    evidence_type VARCHAR(50) NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    checksum VARCHAR(100),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_evidence_detection ON evidence (detection_id);
CREATE INDEX IF NOT EXISTS idx_evidence_mission ON evidence (mission_id);
CREATE INDEX IF NOT EXISTS idx_evidence_type ON evidence (evidence_type);

-- Create a function to update last_updated timestamp
CREATE OR REPLACE FUNCTION update_last_updated_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for auto-updating timestamps
CREATE TRIGGER update_tiles_last_updated BEFORE UPDATE ON tiles
    FOR EACH ROW EXECUTE FUNCTION update_last_updated_column();

-- Function to calculate distance between two points (Haversine formula)
CREATE OR REPLACE FUNCTION haversine_distance(
    lat1 DOUBLE PRECISION,
    lon1 DOUBLE PRECISION,
    lat2 DOUBLE PRECISION,
    lon2 DOUBLE PRECISION
) RETURNS DOUBLE PRECISION AS $$
DECLARE
    R CONSTANT DOUBLE PRECISION := 6371.0; -- Earth radius in km
    dLat DOUBLE PRECISION;
    dLon DOUBLE PRECISION;
    a DOUBLE PRECISION;
    c DOUBLE PRECISION;
BEGIN
    dLat := radians(lat2 - lat1);
    dLon := radians(lon2 - lon1);
    
    a := sin(dLat/2) * sin(dLat/2) +
         cos(radians(lat1)) * cos(radians(lat2)) *
         sin(dLon/2) * sin(dLon/2);
    
    c := 2 * atan2(sqrt(a), sqrt(1-a));
    
    RETURN R * c;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to find nearest available UAV
CREATE OR REPLACE FUNCTION find_nearest_uav(
    target_lat DOUBLE PRECISION,
    target_lon DOUBLE PRECISION,
    min_battery DOUBLE PRECISION DEFAULT 20.0
) RETURNS TABLE (
    uav_id VARCHAR(50),
    distance DOUBLE PRECISION,
    battery_level DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.uav_id,
        haversine_distance(u.latitude, u.longitude, target_lat, target_lon) as dist,
        u.battery_level
    FROM uavs u
    WHERE u.status = 'available'
        AND u.battery_level >= min_battery
    ORDER BY dist ASC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- View for mission statistics
CREATE OR REPLACE VIEW mission_stats AS
SELECT 
    status,
    COUNT(*) as count,
    AVG(actual_duration) as avg_duration,
    MIN(created_at) as first_mission,
    MAX(created_at) as last_mission
FROM missions
GROUP BY status;

-- View for UAV fleet status
CREATE OR REPLACE VIEW fleet_status AS
SELECT 
    status,
    COUNT(*) as count,
    AVG(battery_level) as avg_battery,
    MIN(battery_level) as min_battery,
    MAX(battery_level) as max_battery
FROM uavs
GROUP BY status;

-- View for detection summary
CREATE OR REPLACE VIEW detection_summary AS
SELECT 
    detection_type,
    COUNT(*) as total_detections,
    AVG(confidence) as avg_confidence,
    COUNT(CASE WHEN verified = TRUE THEN 1 END) as verified_count
FROM detections
GROUP BY detection_type;

-- Insert comments for documentation
COMMENT ON TABLE tiles IS 'Geographic tiles for satellite monitoring coverage';
COMMENT ON TABLE uavs IS 'UAV fleet registry and status';
COMMENT ON TABLE missions IS 'UAV mission assignments and tracking';
COMMENT ON TABLE sat_alerts IS 'Satellite detection alerts requiring UAV verification';
COMMENT ON TABLE detections IS 'UAV edge inference detections (YOLOv8 results)';
COMMENT ON TABLE telemetry IS 'Real-time UAV telemetry data';
COMMENT ON TABLE evidence IS 'Evidence storage references (MinIO paths)';

COMMENT ON FUNCTION haversine_distance IS 'Calculate great-circle distance between two lat/lon points in kilometers';
COMMENT ON FUNCTION find_nearest_uav IS 'Find the nearest available UAV with sufficient battery to a target location';
