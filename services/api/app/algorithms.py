"""
Advanced Algorithms for Path Planning, Coverage, and Tracking.

Implements algorithms from Appendix A: Algorithm Specifications.
"""

import math
import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum
import heapq


# ============================================================
# Data Structures
# ============================================================

@dataclass
class Point:
    """2D point."""
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        """Euclidean distance to another point."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


@dataclass
class Waypoint:
    """Waypoint with position and optional metadata."""
    lat: float
    lon: float
    alt: float = 100.0
    speed: float = 15.0
    heading: Optional[float] = None
    action: Optional[str] = None


@dataclass
class BoundingBox:
    """Bounding box for detection."""
    x: float
    y: float
    width: float
    height: float
    confidence: float
    class_id: int


# ============================================================
# A* Pathfinding Algorithm (Appendix A.3)
# ============================================================

class AStarPathfinder:
    """
    A* pathfinding algorithm for UAV path planning.
    
    Complexity: O(w*h*log(w*h)) where w,h are grid dimensions.
    """
    
    def __init__(self, grid_width: int, grid_height: int, obstacles: List[Tuple[int, int]]):
        """
        Initialize pathfinder.
        
        Args:
            grid_width: Width of search grid
            grid_height: Height of search grid
            obstacles: List of (x, y) obstacle positions
        """
        self.width = grid_width
        self.height = grid_height
        self.obstacles = set(obstacles)
    
    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Euclidean distance heuristic."""
        return math.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)
    
    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighbors (8-connected grid)."""
        x, y = pos
        neighbors = []
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                nx, ny = x + dx, y + dy
                
                # Check bounds
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    # Check obstacles
                    if (nx, ny) not in self.obstacles:
                        neighbors.append((nx, ny))
        
        return neighbors
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Find path from start to goal using A*.
        
        Returns list of (x, y) positions or None if no path exists.
        """
        frontier = []
        heapq.heappush(frontier, (0, start))
        
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            _, current = heapq.heappop(frontier)
            
            if current == goal:
                break
            
            for next_pos in self.get_neighbors(current):
                # Cost is 1.4 for diagonal, 1.0 for cardinal
                dx = abs(next_pos[0] - current[0])
                dy = abs(next_pos[1] - current[1])
                step_cost = 1.4 if (dx + dy) == 2 else 1.0
                
                new_cost = cost_so_far[current] + step_cost
                
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.heuristic(next_pos, goal)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current
        
        # Reconstruct path
        if goal not in came_from:
            return None
        
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = came_from[current]
        
        path.reverse()
        return path


# ============================================================
# Dubins Paths (Appendix A.4)
# ============================================================

class DubinsPathType(Enum):
    """Dubins path canonical types."""
    LSL = "LSL"  # Left-Straight-Left
    LSR = "LSR"  # Left-Straight-Right
    RSL = "RSL"  # Right-Straight-Left
    RSR = "RSR"  # Right-Straight-Right
    RLR = "RLR"  # Right-Left-Right
    LRL = "LRL"  # Left-Right-Left


@dataclass
class DubinsPath:
    """Dubins path with type and arc lengths."""
    path_type: DubinsPathType
    lengths: Tuple[float, float, float]  # (t, p, q)
    total_length: float


class DubinsPathPlanner:
    """
    Dubins path planner for UAV trajectories with turning radius constraint.
    
    Generates minimum-length paths consisting of circular arcs and straight lines.
    """
    
    def __init__(self, turning_radius: float):
        """
        Initialize Dubins planner.
        
        Args:
            turning_radius: Minimum turning radius in meters
        """
        self.rho = turning_radius
    
    def plan_path(
        self,
        start: Tuple[float, float, float],
        goal: Tuple[float, float, float]
    ) -> Optional[DubinsPath]:
        """
        Plan Dubins path from start to goal.
        
        Args:
            start: (x, y, theta) start configuration
            goal: (x, y, theta) goal configuration
        
        Returns:
            DubinsPath or None if no path exists
        """
        # Normalize coordinates
        dx = goal[0] - start[0]
        dy = goal[1] - start[1]
        d = math.sqrt(dx*dx + dy*dy) / self.rho
        
        theta = math.atan2(dy, dx)
        alpha = self._mod2pi(start[2] - theta)
        beta = self._mod2pi(goal[2] - theta)
        
        # Try all 6 Dubins path types
        best_path = None
        best_length = float('inf')
        
        for path_func in [self._LSL, self._RSR, self._LSR, self._RSL, self._RLR, self._LRL]:
            path = path_func(alpha, beta, d)
            if path and path.total_length < best_length:
                best_path = path
                best_length = path.total_length
        
        return best_path
    
    def _mod2pi(self, theta: float) -> float:
        """Normalize angle to [0, 2*pi)."""
        return theta - 2.0 * math.pi * math.floor(theta / (2.0 * math.pi))
    
    def _LSL(self, alpha: float, beta: float, d: float) -> Optional[DubinsPath]:
        """LSL path type."""
        sa = math.sin(alpha)
        sb = math.sin(beta)
        ca = math.cos(alpha)
        cb = math.cos(beta)
        c_ab = math.cos(alpha - beta)
        
        tmp = 2.0 + d*d - 2.0*c_ab + 2.0*d*(sa - sb)
        
        if tmp >= 0:
            t = self._mod2pi(-alpha + math.atan2(cb - ca, d + sa - sb))
            p = math.sqrt(max(0, tmp))
            q = self._mod2pi(beta - math.atan2(cb - ca, d + sa - sb))
            
            return DubinsPath(
                path_type=DubinsPathType.LSL,
                lengths=(t, p, q),
                total_length=(t + p + q) * self.rho
            )
        return None
    
    def _RSR(self, alpha: float, beta: float, d: float) -> Optional[DubinsPath]:
        """RSR path type."""
        sa = math.sin(alpha)
        sb = math.sin(beta)
        ca = math.cos(alpha)
        cb = math.cos(beta)
        c_ab = math.cos(alpha - beta)
        
        tmp = 2.0 + d*d - 2.0*c_ab + 2.0*d*(sb - sa)
        
        if tmp >= 0:
            t = self._mod2pi(alpha - math.atan2(ca - cb, d - sa + sb))
            p = math.sqrt(max(0, tmp))
            q = self._mod2pi(-beta + math.atan2(ca - cb, d - sa + sb))
            
            return DubinsPath(
                path_type=DubinsPathType.RSR,
                lengths=(t, p, q),
                total_length=(t + p + q) * self.rho
            )
        return None
    
    def _LSR(self, alpha: float, beta: float, d: float) -> Optional[DubinsPath]:
        """LSR path type."""
        sa = math.sin(alpha)
        sb = math.sin(beta)
        ca = math.cos(alpha)
        cb = math.cos(beta)
        c_ab = math.cos(alpha - beta)
        
        p_squared = -2.0 + d*d + 2.0*c_ab + 2.0*d*(sa + sb)
        
        if p_squared >= 0:
            p = math.sqrt(p_squared)
            t = self._mod2pi(-alpha + math.atan2(-ca - cb, d + sa + sb) - math.atan2(-2.0, p))
            q = self._mod2pi(-beta + math.atan2(-ca - cb, d + sa + sb) - math.atan2(-2.0, p))
            
            return DubinsPath(
                path_type=DubinsPathType.LSR,
                lengths=(t, p, q),
                total_length=(t + p + q) * self.rho
            )
        return None
    
    def _RSL(self, alpha: float, beta: float, d: float) -> Optional[DubinsPath]:
        """RSL path type."""
        sa = math.sin(alpha)
        sb = math.sin(beta)
        ca = math.cos(alpha)
        cb = math.cos(beta)
        c_ab = math.cos(alpha - beta)
        
        p_squared = -2.0 + d*d + 2.0*c_ab - 2.0*d*(sa + sb)
        
        if p_squared >= 0:
            p = math.sqrt(p_squared)
            t = self._mod2pi(alpha - math.atan2(ca + cb, d - sa - sb) + math.atan2(2.0, p))
            q = self._mod2pi(beta - math.atan2(ca + cb, d - sa - sb) + math.atan2(2.0, p))
            
            return DubinsPath(
                path_type=DubinsPathType.RSL,
                lengths=(t, p, q),
                total_length=(t + p + q) * self.rho
            )
        return None
    
    def _RLR(self, alpha: float, beta: float, d: float) -> Optional[DubinsPath]:
        """RLR path type."""
        sa = math.sin(alpha)
        sb = math.sin(beta)
        ca = math.cos(alpha)
        cb = math.cos(beta)
        c_ab = math.cos(alpha - beta)
        
        tmp = (6.0 - d*d + 2.0*c_ab + 2.0*d*(sa - sb)) / 8.0
        
        if abs(tmp) <= 1.0:
            p = self._mod2pi(2.0*math.pi - math.acos(tmp))
            t = self._mod2pi(alpha - math.atan2(ca - cb, d - sa + sb) + p/2.0)
            q = self._mod2pi(alpha - beta - t + p)
            
            return DubinsPath(
                path_type=DubinsPathType.RLR,
                lengths=(t, p, q),
                total_length=(t + p + q) * self.rho
            )
        return None
    
    def _LRL(self, alpha: float, beta: float, d: float) -> Optional[DubinsPath]:
        """LRL path type."""
        sa = math.sin(alpha)
        sb = math.sin(beta)
        ca = math.cos(alpha)
        cb = math.cos(beta)
        c_ab = math.cos(alpha - beta)
        
        tmp = (6.0 - d*d + 2.0*c_ab + 2.0*d*(sb - sa)) / 8.0
        
        if abs(tmp) <= 1.0:
            p = self._mod2pi(2.0*math.pi - math.acos(tmp))
            t = self._mod2pi(-alpha - math.atan2(ca - cb, d + sa - sb) + p/2.0)
            q = self._mod2pi(beta - alpha - t + p)
            
            return DubinsPath(
                path_type=DubinsPathType.LRL,
                lengths=(t, p, q),
                total_length=(t + p + q) * self.rho
            )
        return None


# ============================================================
# Coverage Patterns (Appendix A.5)
# ============================================================

class CoveragePatternType(Enum):
    """Coverage pattern types."""
    LAWNMOWER = "lawnmower"
    SPIRAL = "spiral"
    SECTOR_SCAN = "sector_scan"


class CoveragePatternGenerator:
    """
    Generate coverage patterns for area surveillance.
    """
    
    @staticmethod
    def generate_lawnmower(
        center_lat: float,
        center_lon: float,
        width_m: float,
        height_m: float,
        spacing_m: float,
        altitude_m: float = 100.0,
        heading_deg: float = 0.0
    ) -> List[Waypoint]:
        """
        Generate lawnmower (boustrophedon) coverage pattern.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            width_m: Pattern width in meters
            height_m: Pattern height in meters
            spacing_m: Line spacing in meters
            altitude_m: Flight altitude
            heading_deg: Pattern rotation in degrees
        
        Returns:
            List of waypoints
        """
        waypoints = []
        
        # Number of passes
        num_passes = int(height_m / spacing_m) + 1
        
        # Convert to local coordinates
        meters_per_degree_lat = 111320.0
        meters_per_degree_lon = 111320.0 * math.cos(math.radians(center_lat))
        
        for i in range(num_passes):
            # Y position
            y_offset = -height_m/2 + i * spacing_m
            
            # X positions (alternate direction)
            if i % 2 == 0:
                x_start, x_end = -width_m/2, width_m/2
            else:
                x_start, x_end = width_m/2, -width_m/2
            
            # Convert to lat/lon
            lat_offset = y_offset / meters_per_degree_lat
            lon_start = (x_start / meters_per_degree_lon)
            lon_end = (x_end / meters_per_degree_lon)
            
            waypoints.append(Waypoint(
                lat=center_lat + lat_offset,
                lon=center_lon + lon_start,
                alt=altitude_m
            ))
            
            waypoints.append(Waypoint(
                lat=center_lat + lat_offset,
                lon=center_lon + lon_end,
                alt=altitude_m
            ))
        
        return waypoints
    
    @staticmethod
    def generate_spiral(
        center_lat: float,
        center_lon: float,
        max_radius_m: float,
        spacing_m: float,
        altitude_m: float = 100.0,
        num_points: int = 100
    ) -> List[Waypoint]:
        """
        Generate Archimedean spiral coverage pattern.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            max_radius_m: Maximum spiral radius in meters
            spacing_m: Spacing between spiral arms
            altitude_m: Flight altitude
            num_points: Number of waypoints
        
        Returns:
            List of waypoints
        """
        waypoints = []
        
        # Convert to local coordinates
        meters_per_degree_lat = 111320.0
        meters_per_degree_lon = 111320.0 * math.cos(math.radians(center_lat))
        
        # Archimedean spiral: r = a * theta
        a = spacing_m / (2 * math.pi)
        max_theta = max_radius_m / a
        
        for i in range(num_points):
            theta = (i / num_points) * max_theta
            r = a * theta
            
            # Convert polar to Cartesian
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            
            # Convert to lat/lon
            lat = center_lat + (y / meters_per_degree_lat)
            lon = center_lon + (x / meters_per_degree_lon)
            
            waypoints.append(Waypoint(
                lat=lat,
                lon=lon,
                alt=altitude_m
            ))
        
        return waypoints
    
    @staticmethod
    def generate_sector_scan(
        center_lat: float,
        center_lon: float,
        radius_m: float,
        start_angle_deg: float,
        end_angle_deg: float,
        num_radials: int,
        altitude_m: float = 100.0
    ) -> List[Waypoint]:
        """
        Generate sector scan pattern.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_m: Scan radius in meters
            start_angle_deg: Start angle in degrees
            end_angle_deg: End angle in degrees
            num_radials: Number of radial lines
            altitude_m: Flight altitude
        
        Returns:
            List of waypoints
        """
        waypoints = []
        
        # Convert to local coordinates
        meters_per_degree_lat = 111320.0
        meters_per_degree_lon = 111320.0 * math.cos(math.radians(center_lat))
        
        angle_step = (end_angle_deg - start_angle_deg) / (num_radials - 1)
        
        for i in range(num_radials):
            angle = start_angle_deg + i * angle_step
            angle_rad = math.radians(angle)
            
            # From center to perimeter
            x = radius_m * math.cos(angle_rad)
            y = radius_m * math.sin(angle_rad)
            
            # Convert to lat/lon
            lat = center_lat + (y / meters_per_degree_lat)
            lon = center_lon + (x / meters_per_degree_lon)
            
            # Add center point
            waypoints.append(Waypoint(
                lat=center_lat,
                lon=center_lon,
                alt=altitude_m
            ))
            
            # Add perimeter point
            waypoints.append(Waypoint(
                lat=lat,
                lon=lon,
                alt=altitude_m
            ))
        
        return waypoints


# ============================================================
# Kalman Filter for Tracking (Appendix A.2)
# ============================================================

class KalmanFilter:
    """
    Kalman filter for tracking detected objects.
    
    State vector: [x, y, vx, vy]
    """
    
    def __init__(self, dt: float = 1.0):
        """
        Initialize Kalman filter.
        
        Args:
            dt: Time step in seconds
        """
        self.dt = dt
        
        # State transition matrix
        self.F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        # Measurement matrix (we only observe position)
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])
        
        # Process noise covariance
        q = 0.1
        self.Q = np.array([
            [q*dt**4/4, 0, q*dt**3/2, 0],
            [0, q*dt**4/4, 0, q*dt**3/2],
            [q*dt**3/2, 0, q*dt**2, 0],
            [0, q*dt**3/2, 0, q*dt**2]
        ])
        
        # Measurement noise covariance
        r = 0.5
        self.R = np.array([
            [r, 0],
            [0, r]
        ])
        
        # State estimate and covariance
        self.x = None
        self.P = None
    
    def initialize(self, measurement: np.ndarray):
        """Initialize filter with first measurement."""
        self.x = np.array([measurement[0], measurement[1], 0, 0])
        self.P = np.eye(4) * 10.0
    
    def predict(self) -> np.ndarray:
        """Prediction step."""
        if self.x is None:
            return None
        
        # Predict state
        self.x = self.F @ self.x
        
        # Predict covariance
        self.P = self.F @ self.P @ self.F.T + self.Q
        
        return self.x
    
    def update(self, measurement: np.ndarray) -> np.ndarray:
        """
        Update step with new measurement.
        
        Args:
            measurement: [x, y] observation
        
        Returns:
            Updated state estimate
        """
        if self.x is None:
            self.initialize(measurement)
            return self.x
        
        # Innovation
        y = measurement - self.H @ self.x
        
        # Innovation covariance
        S = self.H @ self.P @ self.H.T + self.R
        
        # Kalman gain
        K = self.P @ self.H.T @ np.linalg.inv(S)
        
        # Update state
        self.x = self.x + K @ y
        
        # Update covariance
        I = np.eye(4)
        self.P = (I - K @ self.H) @ self.P
        
        return self.x
    
    def get_position(self) -> Optional[Tuple[float, float]]:
        """Get current position estimate."""
        if self.x is None:
            return None
        return (self.x[0], self.x[1])
    
    def get_velocity(self) -> Optional[Tuple[float, float]]:
        """Get current velocity estimate."""
        if self.x is None:
            return None
        return (self.x[2], self.x[3])
