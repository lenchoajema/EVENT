# Threat & Illegal Activity Logic
## Coordinated Satellite & UAV Event-Analysis MVP

**Document Version:** 1.0  
**Date:** November 9, 2025  
**Parent Document:** [Detection Pipeline](./DETECTION_PIPELINE.md)

---

## 4. Threat & Illegal Activity Logic

### 4.1 Geofencing & No-Go Region Rules

The EVENT system enforces **multi-layered geofencing** to identify unauthorized presence in restricted zones and trigger automatic escalation protocols.

#### Geofence Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│ GEOFENCE HIERARCHY (Nested Zones)                                      │
│                                                                          │
│  ┌──────────────────────────────────────────────────────┐               │
│  │ TIER 1: PERMISSIVE ZONE (Public Areas)              │               │
│  │ - Public roads, parks, designated pathways           │               │
│  │ - Alert Level: None                                  │               │
│  │ - Action: Monitor only                               │               │
│  │                                                       │               │
│  │  ┌────────────────────────────────────────────┐     │               │
│  │  │ TIER 2: CONTROLLED ZONE (Restricted)      │     │               │
│  │  │ - Border buffer (0-5km from boundary)      │     │               │
│  │  │ - Alert Level: Medium                      │     │               │
│  │  │ - Action: Track & log                      │     │               │
│  │  │                                             │     │               │
│  │  │  ┌──────────────────────────────────┐     │     │               │
│  │  │  │ TIER 3: PROHIBITED ZONE          │     │     │               │
│  │  │  │ - Military installations          │     │     │               │
│  │  │  │ - Critical infrastructure         │     │     │               │
│  │  │  │ - Alert Level: High               │     │     │               │
│  │  │  │ - Action: Immediate response      │     │     │               │
│  │  │  │                                    │     │     │               │
│  │  │  │  ┌────────────────────────┐      │     │     │               │
│  │  │  │  │ TIER 4: EXCLUSION ZONE │      │     │     │               │
│  │  │  │  │ - International border  │      │     │     │               │
│  │  │  │  │ - No-entry areas        │      │     │     │               │
│  │  │  │  │ - Alert: CRITICAL       │      │     │     │               │
│  │  │  │  │ - Auto-dispatch backup  │      │     │     │               │
│  │  │  │  └────────────────────────┘      │     │     │               │
│  │  │  └──────────────────────────────────┘     │     │               │
│  │  └────────────────────────────────────────────┘     │               │
│  └──────────────────────────────────────────────────────┘               │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Geofence Data Model

```python
from typing import List, Tuple
from shapely.geometry import Polygon, Point
from enum import Enum

class GeofenceType(Enum):
    PERMISSIVE = 1
    CONTROLLED = 2
    PROHIBITED = 3
    EXCLUSION = 4

class GeofenceRule:
    """
    Define spatial boundaries with enforcement policies.
    """
    def __init__(self, name: str, polygon: Polygon, fence_type: GeofenceType):
        self.name = name
        self.polygon = polygon
        self.fence_type = fence_type
        self.priority = fence_type.value
        
        # Type-specific attributes
        self.alert_threshold = self._get_alert_threshold()
        self.response_time_sla = self._get_response_sla()
        self.notification_channels = self._get_notification_channels()
    
    def _get_alert_threshold(self) -> float:
        """Confidence threshold for automatic alert."""
        thresholds = {
            GeofenceType.PERMISSIVE: 0.90,   # High bar (avoid false alarms)
            GeofenceType.CONTROLLED: 0.75,   # Standard
            GeofenceType.PROHIBITED: 0.65,   # Lower bar (catch more)
            GeofenceType.EXCLUSION: 0.50     # Lowest (zero tolerance)
        }
        return thresholds[self.fence_type]
    
    def _get_response_sla(self) -> int:
        """Maximum response time in seconds."""
        slas = {
            GeofenceType.PERMISSIVE: None,   # No SLA
            GeofenceType.CONTROLLED: 1200,   # 20 minutes
            GeofenceType.PROHIBITED: 600,    # 10 minutes
            GeofenceType.EXCLUSION: 180      # 3 minutes
        }
        return slas[self.fence_type]
    
    def _get_notification_channels(self) -> List[str]:
        """Alert escalation channels."""
        channels = {
            GeofenceType.PERMISSIVE: ['log'],
            GeofenceType.CONTROLLED: ['dashboard'],
            GeofenceType.PROHIBITED: ['dashboard', 'email'],
            GeofenceType.EXCLUSION: ['dashboard', 'email', 'sms', 'radio']
        }
        return channels[self.fence_type]
    
    def check_violation(self, position: Tuple[float, float], 
                       confidence: float) -> dict:
        """
        Check if position violates geofence rules.
        
        Args:
            position: (latitude, longitude)
            confidence: Detection confidence (0.0-1.0)
        
        Returns:
            Violation report or None
        """
        point = Point(position[1], position[0])  # lon, lat for shapely
        
        if self.polygon.contains(point):
            if confidence >= self.alert_threshold:
                return {
                    'violated': True,
                    'fence_name': self.name,
                    'fence_type': self.fence_type.name,
                    'priority': self.priority,
                    'position': position,
                    'confidence': confidence,
                    'response_sla': self.response_time_sla,
                    'notification_channels': self.notification_channels,
                    'distance_to_boundary': self.polygon.boundary.distance(point),
                    'severity': self._calculate_severity(point, confidence)
                }
        
        return {'violated': False}
    
    def _calculate_severity(self, point: Point, confidence: float) -> str:
        """
        Calculate violation severity based on depth of penetration.
        """
        # Distance from boundary (negative = inside)
        boundary_distance = self.polygon.boundary.distance(point)
        
        # Normalize by polygon size
        max_distance = self.polygon.length / (2 * 3.14159)  # Approx radius
        penetration_ratio = boundary_distance / max_distance
        
        # Combined severity score
        severity_score = (
            0.4 * confidence +
            0.3 * self.priority / 4 +
            0.3 * penetration_ratio
        )
        
        if severity_score >= 0.85:
            return 'CRITICAL'
        elif severity_score >= 0.70:
            return 'HIGH'
        elif severity_score >= 0.55:
            return 'MEDIUM'
        else:
            return 'LOW'
```

#### Geofence Manager

```python
class GeofenceManager:
    """
    Manage multiple overlapping geofences with priority resolution.
    """
    def __init__(self):
        self.fences: List[GeofenceRule] = []
    
    def add_fence(self, fence: GeofenceRule):
        """Add geofence and sort by priority."""
        self.fences.append(fence)
        self.fences.sort(key=lambda f: f.priority, reverse=True)
    
    def check_all_fences(self, position: Tuple[float, float], 
                        confidence: float) -> List[dict]:
        """
        Check position against all geofences.
        Returns violations sorted by priority.
        """
        violations = []
        
        for fence in self.fences:
            result = fence.check_violation(position, confidence)
            if result['violated']:
                violations.append(result)
        
        return violations
    
    def get_highest_priority_violation(self, position: Tuple[float, float],
                                      confidence: float) -> dict:
        """
        Return most severe violation (used for alert routing).
        """
        violations = self.check_all_fences(position, confidence)
        
        if violations:
            # Already sorted by priority
            return violations[0]
        
        return None

# Example Usage
def initialize_border_geofences():
    """
    Set up geofences for US-Mexico border scenario.
    """
    manager = GeofenceManager()
    
    # Tier 4: Exclusion Zone (international boundary line)
    border_line = Polygon([
        (-106.5, 31.76), (-106.4, 31.78), 
        (-106.3, 31.77), (-106.2, 31.75)
    ])
    manager.add_fence(GeofenceRule(
        "International Border - Sector 1",
        border_line.buffer(0.001),  # ~100m buffer
        GeofenceType.EXCLUSION
    ))
    
    # Tier 3: Prohibited Zone (0-1 mile from border)
    prohibited_zone = border_line.buffer(0.015)  # ~1 mile
    manager.add_fence(GeofenceRule(
        "Border Enforcement Zone",
        prohibited_zone,
        GeofenceType.PROHIBITED
    ))
    
    # Tier 2: Controlled Zone (1-5 miles from border)
    controlled_zone = border_line.buffer(0.075)  # ~5 miles
    manager.add_fence(GeofenceRule(
        "Border Monitoring Zone",
        controlled_zone,
        GeofenceType.CONTROLLED
    ))
    
    return manager
```

#### Dynamic Geofence Adjustment

```python
def adjust_geofence_by_threat_level(fence: GeofenceRule, 
                                   threat_intel: dict):
    """
    Dynamically adjust geofence parameters based on intelligence.
    
    Use cases:
      - Heightened alert periods
      - Known smuggling routes
      - Seasonal migration patterns
    """
    base_threshold = fence.alert_threshold
    
    # Intelligence factors
    recent_incidents = threat_intel.get('incidents_last_7days', 0)
    known_trafficker_activity = threat_intel.get('trafficker_reports', 0)
    weather_advantage = threat_intel.get('low_visibility_hours', 0)
    
    # Calculate adjustment
    adjustment = 0.0
    
    if recent_incidents > 5:
        adjustment -= 0.10  # Lower threshold (more sensitive)
    
    if known_trafficker_activity > 3:
        adjustment -= 0.15
    
    if weather_advantage > 12:  # >12 hours of poor visibility
        adjustment -= 0.05
    
    # Apply bounds
    fence.alert_threshold = max(0.40, base_threshold + adjustment)
    
    # Log adjustment
    if adjustment < 0:
        log_event('GEOFENCE_SENSITIVITY_INCREASED', {
            'fence': fence.name,
            'old_threshold': base_threshold,
            'new_threshold': fence.alert_threshold,
            'reason': threat_intel
        })
```

---

### 4.2 Abnormal Movement Classifier

The EVENT system identifies **suspicious movement patterns** that deviate from normal behavior profiles.

#### Movement Pattern Detection

```python
import numpy as np
from scipy.spatial.distance import euclidean
from sklearn.cluster import DBSCAN

class MovementClassifier:
    """
    Classify movement patterns as normal, suspicious, or evasive.
    """
    
    # Normal movement speeds (meters/second)
    SPEED_PROFILES = {
        'person_walking': (0.8, 2.0),
        'person_running': (2.5, 5.5),
        'person_sprinting': (5.5, 10.0),
        'vehicle_slow': (2.0, 8.0),      # Rough terrain
        'vehicle_normal': (8.0, 25.0),   # Roads
        'vehicle_fast': (25.0, 45.0),    # Highways
        'bicycle': (3.0, 8.0),
        'motorcycle': (5.0, 30.0)
    }
    
    def __init__(self):
        self.track_history = {}  # track_id -> list of positions
    
    def analyze_track(self, track_id: str, 
                     positions: List[Tuple[float, float, float]],
                     detection_class: str) -> dict:
        """
        Analyze movement track for abnormal patterns.
        
        Args:
            track_id: Unique tracker ID
            positions: [(lat, lon, timestamp), ...]
            detection_class: 'person', 'vehicle', etc.
        
        Returns:
            Classification result with suspicion factors
        """
        if len(positions) < 3:
            return {'pattern': 'insufficient_data'}
        
        # Calculate movement metrics
        velocities = self._calculate_velocities(positions)
        headings = self._calculate_headings(positions)
        accelerations = self._calculate_accelerations(velocities)
        
        # Pattern features
        features = {
            'avg_speed': np.mean(velocities),
            'max_speed': np.max(velocities),
            'speed_variance': np.var(velocities),
            'direction_changes': self._count_direction_changes(headings),
            'stops': self._count_stops(velocities),
            'path_linearity': self._calculate_linearity(positions),
            'total_distance': self._calculate_total_distance(positions),
            'displacement': self._calculate_displacement(positions),
            'duration': positions[-1][2] - positions[0][2]  # seconds
        }
        
        # Classify pattern
        pattern = self._classify_pattern(features, detection_class)
        suspicion_score = self._calculate_suspicion(features, pattern, 
                                                    detection_class)
        
        return {
            'track_id': track_id,
            'pattern': pattern,
            'suspicion_score': suspicion_score,
            'features': features,
            'alerts': self._generate_alerts(pattern, suspicion_score)
        }
    
    def _calculate_velocities(self, positions: List) -> np.ndarray:
        """Calculate speed between consecutive positions."""
        velocities = []
        for i in range(1, len(positions)):
            lat1, lon1, t1 = positions[i-1]
            lat2, lon2, t2 = positions[i]
            
            distance = haversine_distance((lat1, lon1), (lat2, lon2))
            time_delta = t2 - t1
            
            if time_delta > 0:
                velocity = distance / time_delta  # m/s
                velocities.append(velocity)
        
        return np.array(velocities)
    
    def _calculate_headings(self, positions: List) -> np.ndarray:
        """Calculate bearing between consecutive positions."""
        headings = []
        for i in range(1, len(positions)):
            lat1, lon1, _ = positions[i-1]
            lat2, lon2, _ = positions[i]
            
            # Calculate bearing
            dlon = np.radians(lon2 - lon1)
            lat1_rad = np.radians(lat1)
            lat2_rad = np.radians(lat2)
            
            x = np.sin(dlon) * np.cos(lat2_rad)
            y = (np.cos(lat1_rad) * np.sin(lat2_rad) - 
                 np.sin(lat1_rad) * np.cos(lat2_rad) * np.cos(dlon))
            
            bearing = np.degrees(np.arctan2(x, y))
            headings.append((bearing + 360) % 360)
        
        return np.array(headings)
    
    def _count_direction_changes(self, headings: np.ndarray, 
                                 threshold: float = 45) -> int:
        """Count significant direction changes (>threshold degrees)."""
        changes = 0
        for i in range(1, len(headings)):
            delta = abs(headings[i] - headings[i-1])
            # Handle wraparound
            if delta > 180:
                delta = 360 - delta
            
            if delta > threshold:
                changes += 1
        
        return changes
    
    def _count_stops(self, velocities: np.ndarray, 
                    threshold: float = 0.3) -> int:
        """Count number of stops (velocity < threshold)."""
        return np.sum(velocities < threshold)
    
    def _calculate_linearity(self, positions: List) -> float:
        """
        Calculate path linearity ratio.
        
        Linearity = straight_line_distance / path_length
        - 1.0 = perfectly straight
        - <0.5 = very winding/erratic
        """
        if len(positions) < 2:
            return 1.0
        
        # Straight line distance (start to end)
        start = (positions[0][0], positions[0][1])
        end = (positions[-1][0], positions[-1][1])
        straight_dist = haversine_distance(start, end)
        
        # Actual path length
        path_length = self._calculate_total_distance(positions)
        
        if path_length == 0:
            return 1.0
        
        return straight_dist / path_length
    
    def _calculate_total_distance(self, positions: List) -> float:
        """Sum of all segment distances."""
        total = 0
        for i in range(1, len(positions)):
            p1 = (positions[i-1][0], positions[i-1][1])
            p2 = (positions[i][0], positions[i][1])
            total += haversine_distance(p1, p2)
        return total
    
    def _calculate_displacement(self, positions: List) -> float:
        """Straight-line distance from start to end."""
        start = (positions[0][0], positions[0][1])
        end = (positions[-1][0], positions[-1][1])
        return haversine_distance(start, end)
    
    def _classify_pattern(self, features: dict, 
                         detection_class: str) -> str:
        """
        Classify movement pattern.
        
        Patterns:
          - direct: Straight path, consistent speed
          - patrol: Back-and-forth, stops, predictable
          - evasive: Erratic, direction changes, speed variance
          - loitering: Minimal movement, circling
          - pursuit: High speed, direct, accelerating
        """
        avg_speed = features['avg_speed']
        linearity = features['path_linearity']
        direction_changes = features['direction_changes']
        stops = features['stops']
        speed_variance = features['speed_variance']
        
        # Decision tree classification
        if avg_speed < 0.5 and stops > 3:
            return 'loitering'
        
        elif linearity > 0.85 and direction_changes < 2:
            if avg_speed > 5.0:
                return 'pursuit'
            else:
                return 'direct'
        
        elif direction_changes > 5 or speed_variance > 4.0:
            return 'evasive'
        
        elif stops > 2 and linearity < 0.6:
            return 'patrol'
        
        else:
            return 'normal'
    
    def _calculate_suspicion(self, features: dict, pattern: str,
                            detection_class: str) -> float:
        """
        Calculate suspicion score (0.0-1.0).
        
        High suspicion indicators:
          - Evasive patterns
          - Speed inconsistent with terrain
          - Nighttime movement
          - Proximity to restricted zones
        """
        score = 0.0
        
        # Pattern-based scoring
        pattern_scores = {
            'evasive': 0.85,
            'loitering': 0.75,
            'pursuit': 0.70,
            'patrol': 0.50,
            'direct': 0.40,
            'normal': 0.30
        }
        score += pattern_scores.get(pattern, 0.5) * 0.5
        
        # Speed anomaly
        avg_speed = features['avg_speed']
        expected_range = self.SPEED_PROFILES.get(
            f"{detection_class}_normal", (0, 100)
        )
        
        if not (expected_range[0] <= avg_speed <= expected_range[1]):
            score += 0.15  # Speed anomaly
        
        # Erratic behavior
        if features['direction_changes'] > 8:
            score += 0.15  # Excessive direction changes
        
        if features['speed_variance'] > 5.0:
            score += 0.10  # Inconsistent speed
        
        # Non-linear path
        if features['path_linearity'] < 0.4:
            score += 0.10  # Very winding path
        
        return min(score, 1.0)
    
    def _generate_alerts(self, pattern: str, 
                        suspicion_score: float) -> List[str]:
        """Generate human-readable alerts."""
        alerts = []
        
        if pattern == 'evasive':
            alerts.append('EVASIVE MOVEMENT DETECTED')
        
        if pattern == 'loitering':
            alerts.append('LOITERING BEHAVIOR')
        
        if suspicion_score >= 0.80:
            alerts.append('HIGH SUSPICION SCORE')
        
        return alerts
```

---

### 4.3 Human, Vehicle & Convoy Detection

The EVENT system employs **specialized detection logic** for different entity types with contextual analysis.

#### Entity-Specific Detection

```python
class EntityDetector:
    """
    Specialized detection and analysis for different entity types.
    """
    
    def analyze_person_detection(self, detection: dict, 
                                 context: dict) -> dict:
        """
        Enhanced analysis for person detections.
        
        Factors:
          - Group size (isolated vs convoy)
          - Equipment (backpacks, weapons indicators)
          - Activity (walking, running, hiding)
          - Environment (trail, off-trail, urban)
        """
        analysis = {
            'entity_type': 'person',
            'threat_indicators': [],
            'threat_score': 0.0
        }
        
        # Check for group
        nearby_persons = self._find_nearby_entities(
            detection, entity_type='person', radius=50
        )
        
        group_size = len(nearby_persons) + 1
        if group_size >= 5:
            analysis['threat_indicators'].append(
                f'LARGE GROUP ({group_size} persons)'
            )
            analysis['threat_score'] += 0.20
        elif group_size >= 3:
            analysis['threat_indicators'].append(
                f'SMALL GROUP ({group_size} persons)'
            )
            analysis['threat_score'] += 0.10
        
        # Check for backpacks (load bearing)
        if self._detect_backpack(detection):
            analysis['threat_indicators'].append('CARRYING LOAD')
            analysis['threat_score'] += 0.15
        
        # Check environment
        if context.get('off_trail', False):
            analysis['threat_indicators'].append('OFF-TRAIL MOVEMENT')
            analysis['threat_score'] += 0.20
        
        # Check time of day
        if context.get('nighttime', False):
            analysis['threat_indicators'].append('NIGHTTIME ACTIVITY')
            analysis['threat_score'] += 0.25
        
        # Check proximity to POI
        nearest_poi = self._get_nearest_poi(detection['position'])
        if nearest_poi['distance'] < 500:  # Within 500m
            analysis['threat_indicators'].append(
                f'NEAR {nearest_poi["type"].upper()}'
            )
            analysis['threat_score'] += 0.15
        
        analysis['threat_level'] = self._classify_threat(
            analysis['threat_score']
        )
        
        return analysis
    
    def analyze_vehicle_detection(self, detection: dict,
                                  context: dict) -> dict:
        """
        Enhanced analysis for vehicle detections.
        
        Factors:
          - Vehicle type (car, truck, ATV)
          - Convoy formation
          - Road vs off-road
          - Speed profile
        """
        analysis = {
            'entity_type': 'vehicle',
            'vehicle_type': detection.get('sub_class', 'unknown'),
            'threat_indicators': [],
            'threat_score': 0.0
        }
        
        # Check for convoy
        nearby_vehicles = self._find_nearby_entities(
            detection, entity_type='vehicle', radius=100
        )
        
        if len(nearby_vehicles) >= 2:
            # Check if vehicles are moving in formation
            if self._is_convoy_formation(detection, nearby_vehicles):
                convoy_size = len(nearby_vehicles) + 1
                analysis['threat_indicators'].append(
                    f'VEHICLE CONVOY ({convoy_size} vehicles)'
                )
                analysis['threat_score'] += 0.30
        
        # Check if off-road
        if not self._is_on_road(detection['position']):
            analysis['threat_indicators'].append('OFF-ROAD VEHICLE')
            analysis['threat_score'] += 0.25
        
        # Check vehicle type risk
        if analysis['vehicle_type'] in ['truck', 'van']:
            analysis['threat_indicators'].append('HIGH-CAPACITY VEHICLE')
            analysis['threat_score'] += 0.15
        
        # Check speed
        speed = detection.get('speed', 0)
        if speed < 2.0:  # Stopped or very slow
            analysis['threat_indicators'].append('VEHICLE STOPPED')
            analysis['threat_score'] += 0.20
        
        # Check proximity to border
        border_distance = self._distance_to_border(detection['position'])
        if border_distance < 1000:  # Within 1km
            analysis['threat_indicators'].append('NEAR BORDER')
            analysis['threat_score'] += 0.25
        
        analysis['threat_level'] = self._classify_threat(
            analysis['threat_score']
        )
        
        return analysis
    
    def detect_convoy(self, detections: List[dict]) -> List[dict]:
        """
        Identify vehicle convoys using spatial clustering.
        
        Convoy criteria:
          - 3+ vehicles within 100m
          - Similar headings (±20°)
          - Similar speeds (±30%)
        """
        if len(detections) < 3:
            return []
        
        # Extract vehicle positions
        positions = []
        for det in detections:
            if det['class'] in ['car', 'truck', 'motorcycle']:
                positions.append([
                    det['position'][0],
                    det['position'][1]
                ])
        
        if len(positions) < 3:
            return []
        
        # Cluster using DBSCAN
        clustering = DBSCAN(eps=0.001, min_samples=3).fit(positions)
        labels = clustering.labels_
        
        convoys = []
        for cluster_id in set(labels):
            if cluster_id == -1:  # Noise
                continue
            
            # Get vehicles in this cluster
            cluster_vehicles = [
                detections[i] for i, label in enumerate(labels)
                if label == cluster_id
            ]
            
            # Verify convoy criteria
            if self._verify_convoy_criteria(cluster_vehicles):
                convoys.append({
                    'convoy_id': f'CONVOY_{cluster_id}',
                    'vehicle_count': len(cluster_vehicles),
                    'vehicles': cluster_vehicles,
                    'center': np.mean(positions[labels == cluster_id], axis=0),
                    'threat_score': 0.70  # Convoys are high priority
                })
        
        return convoys
    
    def _verify_convoy_criteria(self, vehicles: List[dict]) -> bool:
        """Verify vehicles meet convoy definition."""
        if len(vehicles) < 3:
            return False
        
        # Check heading consistency
        headings = [v.get('heading', 0) for v in vehicles]
        heading_variance = np.var(headings)
        if heading_variance > 400:  # >20° std dev
            return False
        
        # Check speed consistency
        speeds = [v.get('speed', 0) for v in vehicles]
        speed_mean = np.mean(speeds)
        speed_variance = np.var(speeds)
        
        if speed_variance > (speed_mean * 0.3)**2:  # >30% variance
            return False
        
        return True
    
    def _classify_threat(self, score: float) -> str:
        """Convert threat score to category."""
        if score >= 0.75:
            return 'CRITICAL'
        elif score >= 0.60:
            return 'HIGH'
        elif score >= 0.45:
            return 'MEDIUM'
        else:
            return 'LOW'
```

---

### 4.4 Suspicious Behavior Labels

The EVENT system tags detections with **behavior labels** derived from temporal and spatial analysis.

#### Behavior Classification System

```python
from datetime import datetime, timedelta
from collections import defaultdict

class BehaviorAnalyzer:
    """
    Classify entity behaviors based on observation history.
    """
    
    BEHAVIOR_DEFINITIONS = {
        'loitering': {
            'description': 'Remaining in area with minimal movement',
            'criteria': {
                'min_duration': 120,  # seconds
                'max_displacement': 20,  # meters
                'max_speed': 0.5  # m/s
            },
            'suspicion': 0.75
        },
        'stealth_pathing': {
            'description': 'Following non-obvious routes, avoiding roads',
            'criteria': {
                'off_road_ratio': 0.80,  # 80% of path off-road
                'cover_usage': 0.60,  # 60% near vegetation/terrain
                'nighttime': True
            },
            'suspicion': 0.85
        },
        'border_probing': {
            'description': 'Repeated approach and retreat from boundary',
            'criteria': {
                'border_approaches': 3,  # Number of times
                'approach_distance': 100,  # meters from border
                'retreat_pattern': True
            },
            'suspicion': 0.90
        },
        'evasive_maneuvering': {
            'description': 'Erratic movement, direction changes',
            'criteria': {
                'direction_changes': 8,
                'speed_variance': 5.0,
                'linearity': 0.40
            },
            'suspicion': 0.80
        },
        'group_coordination': {
            'description': 'Multiple entities moving in sync',
            'criteria': {
                'group_size': 3,
                'formation_maintained': True,
                'synchronized_stops': True
            },
            'suspicion': 0.70
        },
        'loading_activity': {
            'description': 'Transfer of goods between entities',
            'criteria': {
                'entities_proximity': 5,  # meters
                'stop_duration': 60,  # seconds
                'vehicle_present': True
            },
            'suspicion': 0.85
        },
        'surveillance': {
            'description': 'Observing location without approaching',
            'criteria': {
                'stationary_duration': 300,  # 5 minutes
                'line_of_sight_to_poi': True,
                'elevated_position': True
            },
            'suspicion': 0.75
        }
    }
    
    def __init__(self):
        self.observation_history = defaultdict(list)
    
    def analyze_behavior(self, track_id: str, 
                        track_data: dict) -> List[dict]:
        """
        Analyze track history to identify behavioral patterns.
        
        Returns list of detected behaviors with confidence scores.
        """
        behaviors = []
        
        # Check each behavior definition
        for behavior_name, definition in self.BEHAVIOR_DEFINITIONS.items():
            if self._matches_criteria(track_data, definition['criteria']):
                behaviors.append({
                    'behavior': behavior_name,
                    'description': definition['description'],
                    'confidence': self._calculate_behavior_confidence(
                        track_data, definition
                    ),
                    'suspicion_score': definition['suspicion'],
                    'detected_at': datetime.now().isoformat()
                })
        
        return behaviors
    
    def _matches_criteria(self, track_data: dict, criteria: dict) -> bool:
        """Check if track matches behavior criteria."""
        matches = 0
        required_matches = len(criteria)
        
        for key, value in criteria.items():
            track_value = track_data.get(key)
            
            if track_value is None:
                continue
            
            # Type-specific comparison
            if isinstance(value, bool):
                if track_value == value:
                    matches += 1
            elif isinstance(value, (int, float)):
                if track_value >= value:
                    matches += 1
            elif isinstance(value, str):
                if track_value == value:
                    matches += 1
        
        # Require 60% of criteria to match
        return matches / required_matches >= 0.6
    
    def _calculate_behavior_confidence(self, track_data: dict,
                                      definition: dict) -> float:
        """
        Calculate confidence that behavior is correctly identified.
        """
        # Start with base confidence
        confidence = 0.70
        
        # Boost for strong criteria matches
        criteria = definition['criteria']
        for key, threshold in criteria.items():
            value = track_data.get(key, 0)
            
            if isinstance(threshold, (int, float)) and value > threshold * 1.5:
                confidence += 0.10
        
        # Boost for longer observation time
        duration = track_data.get('duration', 0)
        if duration > 300:  # >5 minutes
            confidence += 0.10
        
        return min(confidence, 0.99)
    
    def label_detection(self, detection: dict, 
                       behaviors: List[dict]) -> dict:
        """
        Attach behavior labels to detection record.
        """
        if not behaviors:
            detection['behaviors'] = []
            detection['behavior_summary'] = 'NORMAL'
            return detection
        
        # Sort by suspicion score
        behaviors.sort(key=lambda b: b['suspicion_score'], reverse=True)
        
        # Attach labels
        detection['behaviors'] = behaviors
        detection['behavior_summary'] = behaviors[0]['behavior'].upper()
        detection['max_suspicion'] = behaviors[0]['suspicion_score']
        
        # Generate alert if high suspicion
        if behaviors[0]['suspicion_score'] >= 0.80:
            detection['alert_type'] = 'SUSPICIOUS_BEHAVIOR'
            detection['alert_priority'] = 'HIGH'
        
        return detection
```

---

### 4.5 Confidence Threshold Escalation Rules

The EVENT system implements **dynamic threshold adjustment** based on threat intelligence and operational conditions.

#### Escalation Framework

```python
class ConfidenceEscalator:
    """
    Dynamically adjust confidence thresholds based on threat levels.
    """
    
    # Base thresholds (normal operations)
    BASE_THRESHOLDS = {
        'detection': 0.75,
        'alert': 0.80,
        'dispatch': 0.85,
        'critical': 0.90
    }
    
    def __init__(self):
        self.current_threat_level = 'NORMAL'
        self.active_modifiers = []
    
    def calculate_adjusted_thresholds(self, 
                                     threat_intel: dict) -> dict:
        """
        Calculate threshold adjustments based on intelligence.
        
        Factors:
          - Recent incident frequency
          - Known threat actor presence
          - Environmental conditions
          - Operational priorities
        """
        adjustments = {}
        
        # Factor 1: Recent incident rate
        recent_incidents = threat_intel.get('incidents_last_24h', 0)
        if recent_incidents >= 5:
            adjustment = -0.10  # Lower thresholds
            self.active_modifiers.append('HIGH_INCIDENT_RATE')
        elif recent_incidents >= 3:
            adjustment = -0.05
            self.active_modifiers.append('ELEVATED_ACTIVITY')
        else:
            adjustment = 0.0
        
        # Factor 2: Known threat actors
        if threat_intel.get('known_traffickers_active', False):
            adjustment -= 0.15
            self.active_modifiers.append('KNOWN_THREATS')
        
        # Factor 3: Environmental advantage
        visibility = threat_intel.get('visibility_km', 10)
        if visibility < 2:  # Poor visibility
            adjustment -= 0.05
            self.active_modifiers.append('LOW_VISIBILITY')
        
        # Factor 4: Operational mode
        if threat_intel.get('heightened_alert', False):
            adjustment -= 0.10
            self.active_modifiers.append('HEIGHTENED_ALERT')
        
        # Apply adjustments
        for key, base in self.BASE_THRESHOLDS.items():
            adjusted = max(0.40, base + adjustment)  # Floor at 0.40
            adjustments[key] = adjusted
        
        # Set threat level
        if adjustment <= -0.20:
            self.current_threat_level = 'CRITICAL'
        elif adjustment <= -0.10:
            self.current_threat_level = 'HIGH'
        elif adjustment <= -0.05:
            self.current_threat_level = 'ELEVATED'
        else:
            self.current_threat_level = 'NORMAL'
        
        return adjustments
    
    def should_escalate(self, detection: dict, 
                       current_thresholds: dict) -> bool:
        """
        Determine if detection should trigger escalation.
        """
        confidence = detection.get('confidence', 0)
        threat_score = detection.get('threat_score', 0)
        
        # Check critical threshold
        if confidence >= current_thresholds['critical']:
            return True
        
        # Check combined score
        combined_score = (confidence + threat_score) / 2
        if combined_score >= current_thresholds['dispatch']:
            return True
        
        # Check for override conditions
        if detection.get('geofence_violation') and confidence >= 0.70:
            return True
        
        if detection.get('behavior_summary') == 'BORDER_PROBING':
            return True
        
        return False
```

---

### 4.6 Target Tracking & Pursuit Model

The EVENT system implements **persistent tracking** with predictive pursuit algorithms.

#### Multi-Object Tracking

```python
from scipy.optimize import linear_sum_assignment
from filterpy.kalman import KalmanFilter

class TargetTracker:
    """
    Persistent multi-object tracking with Kalman filtering.
    """
    
    def __init__(self):
        self.tracks = {}  # track_id -> Track object
        self.next_id = 1
        self.max_age = 30  # frames before track deletion
    
    def update(self, detections: List[dict]) -> List[dict]:
        """
        Update tracks with new detections.
        
        Uses Hungarian algorithm for data association.
        """
        if not self.tracks:
            # Initialize tracks from first frame
            for det in detections:
                self._create_track(det)
            return list(self.tracks.values())
        
        # Predict next positions for existing tracks
        for track in self.tracks.values():
            track.predict()
        
        # Build cost matrix (detection-to-track distances)
        cost_matrix = self._build_cost_matrix(detections)
        
        # Solve assignment problem
        det_indices, track_indices = linear_sum_assignment(cost_matrix)
        
        # Update matched tracks
        matched_det_ids = set()
        matched_track_ids = set()
        
        for det_idx, track_idx in zip(det_indices, track_indices):
            if cost_matrix[det_idx, track_idx] < 50:  # Max 50m distance
                track_id = list(self.tracks.keys())[track_idx]
                self.tracks[track_id].update(detections[det_idx])
                matched_det_ids.add(det_idx)
                matched_track_ids.add(track_id)
        
        # Create new tracks for unmatched detections
        for i, det in enumerate(detections):
            if i not in matched_det_ids:
                self._create_track(det)
        
        # Age out unmatched tracks
        for track_id in list(self.tracks.keys()):
            if track_id not in matched_track_ids:
                self.tracks[track_id].age += 1
                if self.tracks[track_id].age > self.max_age:
                    del self.tracks[track_id]
        
        return list(self.tracks.values())
    
    def _create_track(self, detection: dict) -> int:
        """Create new track from detection."""
        track_id = f'TRACK_{self.next_id}'
        self.next_id += 1
        
        self.tracks[track_id] = Track(track_id, detection)
        return track_id
    
    def _build_cost_matrix(self, detections: List[dict]) -> np.ndarray:
        """Calculate detection-to-track distances."""
        n_det = len(detections)
        n_tracks = len(self.tracks)
        
        cost_matrix = np.zeros((n_det, n_tracks))
        
        for i, det in enumerate(detections):
            for j, track in enumerate(self.tracks.values()):
                # Euclidean distance
                det_pos = det['position']
                track_pos = track.predicted_position
                
                distance = haversine_distance(det_pos, track_pos)
                cost_matrix[i, j] = distance
        
        return cost_matrix

class Track:
    """
    Individual target track with Kalman filter.
    """
    def __init__(self, track_id: str, initial_detection: dict):
        self.track_id = track_id
        self.age = 0
        self.hits = 1
        self.history = [initial_detection]
        
        # Initialize Kalman filter
        self.kf = KalmanFilter(dim_x=4, dim_z=2)
        # State: [x, y, vx, vy]
        # Measurement: [x, y]
        
        pos = initial_detection['position']
        self.kf.x = np.array([pos[0], pos[1], 0, 0])
        self.kf.P *= 10  # Initial uncertainty
        
        # Motion model (constant velocity)
        dt = 1.0  # 1 second
        self.kf.F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        # Measurement model
        self.kf.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])
        
        # Noise
        self.kf.R *= 5  # Measurement noise
        self.kf.Q *= 0.01  # Process noise
    
    def predict(self):
        """Predict next position."""
        self.kf.predict()
    
    def update(self, detection: dict):
        """Update with new measurement."""
        pos = detection['position']
        self.kf.update(np.array([pos[0], pos[1]]))
        
        self.history.append(detection)
        self.hits += 1
        self.age = 0
    
    @property
    def predicted_position(self) -> Tuple[float, float]:
        """Get predicted position."""
        return (self.kf.x[0], self.kf.x[1])
    
    @property
    def velocity(self) -> Tuple[float, float]:
        """Get estimated velocity."""
        return (self.kf.x[2], self.kf.x[3])
```

#### Pursuit Planning

```python
def calculate_intercept_point(target_track: Track, 
                             uav_position: Tuple[float, float],
                             uav_speed: float) -> Tuple[float, float]:
    """
    Calculate optimal intercept point for UAV to reach moving target.
    
    Uses proportional navigation guidance.
    """
    # Target state
    target_pos = target_track.predicted_position
    target_vel = target_track.velocity
    
    # Time to intercept (iterative solution)
    t_intercept = 0
    for _ in range(10):  # 10 iterations
        # Predicted target position at t_intercept
        predicted_pos = (
            target_pos[0] + target_vel[0] * t_intercept,
            target_pos[1] + target_vel[1] * t_intercept
        )
        
        # Distance UAV must travel
        distance = haversine_distance(uav_position, predicted_pos)
        
        # Time required
        t_required = distance / uav_speed
        
        # Update estimate
        t_intercept = t_required
    
    intercept_point = (
        target_pos[0] + target_vel[0] * t_intercept,
        target_pos[1] + target_vel[1] * t_intercept
    )
    
    return intercept_point
```

---

## Key Takeaways

✅ **4-tier geofencing** provides graduated response from permissive to exclusion zones  
✅ **Movement classifier** identifies evasive, loitering, and pursuit patterns  
✅ **Entity-specific detection** tailored for persons, vehicles, and convoys  
✅ **7 suspicious behavior labels** from stealth pathing to border probing  
✅ **Dynamic threshold escalation** adjusts sensitivity based on threat intelligence  
✅ **Kalman-filtered tracking** with Hungarian algorithm data association for persistent pursuit  

---

## Navigation

- **Previous:** [Detection Pipeline](./DETECTION_PIPELINE.md)
- **Next:** [Tasking & Intelligence](./TASKING_INTELLIGENCE.md)
- **Home:** [Documentation Index](./README.md)

---

**Document Status:** ✅ Complete  
**Last Updated:** November 9, 2025  
**Review Cycle:** Quarterly
