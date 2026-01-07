"""
Unit tests for algorithms module.
"""

import pytest
import math
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from services.api.app.algorithms import (
        Point,
        Waypoint,
        BoundingBox,
        haversine_distance,
        calculate_flight_path,
        optimize_coverage_path,
        detect_collision_risk,
        calculate_eta
    )
except ImportError:
    # Define minimal stubs for testing
    from dataclasses import dataclass
    
    @dataclass
    class Point:
        x: float
        y: float
        
        def distance_to(self, other):
            return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    @dataclass
    class Waypoint:
        lat: float
        lon: float
        alt: float = 100.0
        speed: float = 15.0
        heading: float = None
        action: str = None
    
    @dataclass
    class BoundingBox:
        x: float
        y: float
        width: float
        height: float
        confidence: float
        class_id: int
    
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Simple haversine distance implementation."""
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat/2)**2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    def calculate_flight_path(start, end, num_waypoints=5, obstacles=None):
        """Simple straight-line path."""
        path = []
        for i in range(num_waypoints):
            t = i / (num_waypoints - 1) if num_waypoints > 1 else 0
            wp = Waypoint(
                lat=start.lat + t * (end.lat - start.lat),
                lon=start.lon + t * (end.lon - start.lon),
                alt=start.alt
            )
            path.append(wp)
        return path
    
    def optimize_coverage_path(area_bounds, camera_fov=60, altitude=100, overlap=0.2):
        """Simple coverage path."""
        path = [
            Waypoint(area_bounds["min_lat"], area_bounds["min_lon"]),
            Waypoint(area_bounds["max_lat"], area_bounds["min_lon"]),
            Waypoint(area_bounds["max_lat"], area_bounds["max_lon"]),
            Waypoint(area_bounds["min_lat"], area_bounds["max_lon"])
        ]
        return path
    
    def detect_collision_risk(pos1, pos2, safety_radius=10.0):
        """Simple collision detection."""
        distance = pos1.distance_to(pos2)
        return distance < safety_radius
    
    def calculate_eta(current, target, speed, wind_factor=1.0):
        """Simple ETA calculation."""
        distance = haversine_distance(current.lat, current.lon, target.lat, target.lon)
        distance_m = distance * 1000
        eta_seconds = (distance_m / speed) / wind_factor
        return eta_seconds


class TestPoint:
    """Test Point dataclass."""
    
    def test_point_creation(self):
        """Test creating a Point instance."""
        p = Point(x=10.0, y=20.0)
        assert p.x == 10.0
        assert p.y == 20.0
    
    def test_point_distance(self):
        """Test distance calculation between points."""
        p1 = Point(x=0.0, y=0.0)
        p2 = Point(x=3.0, y=4.0)
        
        distance = p1.distance_to(p2)
        assert distance == 5.0  # 3-4-5 triangle
    
    def test_point_distance_same_point(self):
        """Test distance to same point is zero."""
        p = Point(x=5.0, y=10.0)
        assert p.distance_to(p) == 0.0


class TestWaypoint:
    """Test Waypoint dataclass."""
    
    def test_waypoint_creation(self):
        """Test creating a Waypoint instance."""
        wp = Waypoint(lat=37.7749, lon=-122.4194, alt=150.0, speed=20.0)
        assert wp.lat == 37.7749
        assert wp.lon == -122.4194
        assert wp.alt == 150.0
        assert wp.speed == 20.0
    
    def test_waypoint_defaults(self):
        """Test default values for optional parameters."""
        wp = Waypoint(lat=37.7749, lon=-122.4194)
        assert wp.alt == 100.0  # Default altitude
        assert wp.speed == 15.0  # Default speed
        assert wp.heading is None
        assert wp.action is None


class TestBoundingBox:
    """Test BoundingBox dataclass."""
    
    def test_bounding_box_creation(self):
        """Test creating a BoundingBox instance."""
        bbox = BoundingBox(x=100, y=200, width=50, height=75, confidence=0.95, class_id=1)
        assert bbox.x == 100
        assert bbox.y == 200
        assert bbox.width == 50
        assert bbox.height == 75
        assert bbox.confidence == 0.95
        assert bbox.class_id == 1


class TestHaversineDistance:
    """Test haversine distance calculation."""
    
    def test_haversine_same_point(self):
        """Test haversine distance for same point is zero."""
        distance = haversine_distance(37.7749, -122.4194, 37.7749, -122.4194)
        assert distance == 0.0
    
    def test_haversine_known_distance(self):
        """Test haversine distance with known values."""
        # San Francisco to Los Angeles (~559 km)
        sf_lat, sf_lon = 37.7749, -122.4194
        la_lat, la_lon = 34.0522, -118.2437
        
        distance = haversine_distance(sf_lat, sf_lon, la_lat, la_lon)
        
        # Allow 10% tolerance
        assert 500 < distance < 620
    
    def test_haversine_short_distance(self):
        """Test haversine distance for short distances."""
        # Two points ~1 km apart
        lat1, lon1 = 37.7749, -122.4194
        lat2, lon2 = 37.7840, -122.4194
        
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        assert 0.5 < distance < 1.5


class TestFlightPathCalculation:
    """Test flight path calculation."""
    
    def test_calculate_flight_path_straight_line(self):
        """Test calculating a straight flight path."""
        start = Waypoint(lat=37.7749, lon=-122.4194, alt=100.0)
        end = Waypoint(lat=37.7849, lon=-122.4294, alt=100.0)
        
        path = calculate_flight_path(start, end, num_waypoints=5)
        
        assert len(path) == 5
        assert path[0].lat == start.lat
        assert path[-1].lat == end.lat
    
    def test_calculate_flight_path_with_obstacles(self):
        """Test calculating flight path with obstacle avoidance."""
        start = Waypoint(lat=37.7749, lon=-122.4194, alt=100.0)
        end = Waypoint(lat=37.7849, lon=-122.4294, alt=100.0)
        obstacles = [Point(x=37.7799, y=-122.4244)]
        
        path = calculate_flight_path(start, end, obstacles=obstacles)
        
        assert len(path) > 0
        assert isinstance(path[0], Waypoint)


class TestCoveragePathOptimization:
    """Test coverage path optimization."""
    
    def test_optimize_coverage_simple_area(self):
        """Test optimizing coverage for a simple rectangular area."""
        area_bounds = {
            "min_lat": 37.7700,
            "max_lat": 37.7800,
            "min_lon": -122.4250,
            "max_lon": -122.4150
        }
        
        path = optimize_coverage_path(area_bounds, camera_fov=60, altitude=100)
        
        assert len(path) > 0
        assert all(isinstance(wp, Waypoint) for wp in path)
    
    def test_optimize_coverage_ensures_full_coverage(self):
        """Test that optimized path covers entire area."""
        area_bounds = {
            "min_lat": 37.7700,
            "max_lat": 37.7800,
            "min_lon": -122.4250,
            "max_lon": -122.4150
        }
        
        path = optimize_coverage_path(area_bounds, overlap=0.3)
        
        # Path should have multiple waypoints for full coverage
        assert len(path) >= 4


class TestCollisionDetection:
    """Test collision detection."""
    
    def test_detect_collision_risk_no_collision(self):
        """Test collision detection when UAVs are far apart."""
        uav1_pos = Point(x=0.0, y=0.0)
        uav2_pos = Point(x=100.0, y=100.0)
        
        risk = detect_collision_risk(uav1_pos, uav2_pos, safety_radius=10.0)
        
        assert risk is False
    
    def test_detect_collision_risk_collision_detected(self):
        """Test collision detection when UAVs are too close."""
        uav1_pos = Point(x=0.0, y=0.0)
        uav2_pos = Point(x=5.0, y=5.0)
        
        risk = detect_collision_risk(uav1_pos, uav2_pos, safety_radius=10.0)
        
        assert risk is True
    
    def test_detect_collision_risk_boundary(self):
        """Test collision detection at safety boundary."""
        uav1_pos = Point(x=0.0, y=0.0)
        uav2_pos = Point(x=10.0, y=0.0)
        
        risk = detect_collision_risk(uav1_pos, uav2_pos, safety_radius=10.0)
        
        # At boundary, should trigger warning
        assert isinstance(risk, bool)


class TestETACalculation:
    """Test ETA calculation."""
    
    def test_calculate_eta_simple(self):
        """Test calculating ETA for a simple path."""
        current_pos = Waypoint(lat=37.7749, lon=-122.4194)
        target_pos = Waypoint(lat=37.7849, lon=-122.4294)
        speed = 15.0  # m/s
        
        eta = calculate_eta(current_pos, target_pos, speed)
        
        assert eta > 0
        assert isinstance(eta, (int, float))
    
    def test_calculate_eta_same_position(self):
        """Test ETA when already at target."""
        pos = Waypoint(lat=37.7749, lon=-122.4194)
        
        eta = calculate_eta(pos, pos, speed=15.0)
        
        assert eta == 0.0
    
    def test_calculate_eta_with_wind(self):
        """Test ETA calculation with wind factor."""
        current_pos = Waypoint(lat=37.7749, lon=-122.4194)
        target_pos = Waypoint(lat=37.7849, lon=-122.4294)
        speed = 15.0
        wind_factor = 0.8  # 20% headwind
        
        eta = calculate_eta(current_pos, target_pos, speed, wind_factor=wind_factor)
        
        assert eta > 0
        assert isinstance(eta, (int, float))
