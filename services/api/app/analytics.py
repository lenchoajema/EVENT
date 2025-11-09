"""
Analytics & Metrics Module.

Implements performance evaluation, coverage analysis, and response time tracking
as specified in Section 9: Monitoring & Optimization.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from scipy import stats
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from .models import UAV, Mission, Detection, SatelliteAlert
from .auth_models import Zone, AuditLog


@dataclass
class PerformanceMetrics:
    """System performance metrics."""
    detection_rate: float  # Detections per hour
    false_positive_rate: float  # Percentage
    response_time_avg: float  # Seconds
    response_time_p95: float  # 95th percentile in seconds
    coverage_percentage: float  # Percentage of area covered
    uav_utilization: float  # Percentage of time UAVs are active
    mission_success_rate: float  # Percentage
    total_missions: int
    total_detections: int
    total_alerts: int


@dataclass
class CoverageMetrics:
    """Coverage analysis metrics."""
    total_area_km2: float
    covered_area_km2: float
    coverage_percentage: float
    gaps: List[Dict]  # Uncovered regions
    overlap_percentage: float  # Redundant coverage
    coverage_by_zone: Dict[str, float]  # Zone-level coverage
    heatmap_data: List[Dict]  # Grid cells with coverage intensity


@dataclass
class ResponseMetrics:
    """Response time metrics."""
    alert_to_assignment: float  # Seconds from alert to mission assignment
    assignment_to_launch: float  # Seconds from assignment to UAV launch
    launch_to_arrival: float  # Seconds from launch to arrival at target
    total_response_time: float  # End-to-end response time
    response_time_by_priority: Dict[str, float]  # By alert priority


class PerformanceEvaluator:
    """
    Evaluates system performance metrics.
    
    Implements Section 9.1: Performance Monitoring
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_metrics(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics for a time period."""
        
        # Detection metrics
        detections = self.db.query(Detection).filter(
            Detection.timestamp.between(start_time, end_time)
        ).all()
        
        hours = (end_time - start_time).total_seconds() / 3600
        detection_rate = len(detections) / hours if hours > 0 else 0
        
        # False positive rate (detections marked as false positives)
        false_positives = sum(1 for d in detections if d.confidence < 0.5)
        false_positive_rate = (false_positives / len(detections) * 100) if detections else 0
        
        # Mission metrics
        missions = self.db.query(Mission).filter(
            Mission.created_at.between(start_time, end_time)
        ).all()
        
        completed_missions = [m for m in missions if m.status == 'completed']
        mission_success_rate = (len(completed_missions) / len(missions) * 100) if missions else 0
        
        # Response time metrics
        response_times = []
        for mission in missions:
            if mission.created_at and mission.completed_at:
                response_time = (mission.completed_at - mission.created_at).total_seconds()
                response_times.append(response_time)
        
        response_time_avg = np.mean(response_times) if response_times else 0
        response_time_p95 = np.percentile(response_times, 95) if response_times else 0
        
        # Coverage metrics
        coverage_analyzer = CoverageAnalyzer(self.db)
        coverage = coverage_analyzer.calculate_coverage(start_time, end_time)
        
        # UAV utilization
        uavs = self.db.query(UAV).all()
        total_time = (end_time - start_time).total_seconds()
        active_time = 0
        
        for uav in uavs:
            uav_missions = [m for m in missions if m.uav_id == uav.uav_id]
            for mission in uav_missions:
                if mission.created_at and mission.completed_at:
                    active_time += (mission.completed_at - mission.created_at).total_seconds()
        
        uav_utilization = (active_time / (total_time * len(uavs)) * 100) if uavs and total_time > 0 else 0
        
        # Alert count
        alerts = self.db.query(SatelliteAlert).filter(
            SatelliteAlert.timestamp.between(start_time, end_time)
        ).count()
        
        return PerformanceMetrics(
            detection_rate=detection_rate,
            false_positive_rate=false_positive_rate,
            response_time_avg=response_time_avg,
            response_time_p95=response_time_p95,
            coverage_percentage=coverage.coverage_percentage,
            uav_utilization=uav_utilization,
            mission_success_rate=mission_success_rate,
            total_missions=len(missions),
            total_detections=len(detections),
            total_alerts=alerts
        )
    
    def get_detection_trends(
        self,
        start_time: datetime,
        end_time: datetime,
        interval_hours: int = 1
    ) -> List[Dict]:
        """Get detection trends over time."""
        trends = []
        current_time = start_time
        
        while current_time < end_time:
            interval_end = current_time + timedelta(hours=interval_hours)
            
            count = self.db.query(Detection).filter(
                Detection.timestamp.between(current_time, interval_end)
            ).count()
            
            trends.append({
                'timestamp': current_time.isoformat(),
                'detection_count': count,
                'interval_hours': interval_hours
            })
            
            current_time = interval_end
        
        return trends
    
    def get_uav_performance(self, uav_id: str) -> Dict:
        """Get performance metrics for a specific UAV."""
        uav = self.db.query(UAV).filter(UAV.uav_id == uav_id).first()
        if not uav:
            return {}
        
        missions = self.db.query(Mission).filter(Mission.uav_id == uav_id).all()
        detections = self.db.query(Detection).filter(Detection.uav_id == uav_id).all()
        
        completed_missions = [m for m in missions if m.status == 'completed']
        failed_missions = [m for m in missions if m.status == 'failed']
        
        mission_durations = []
        for mission in completed_missions:
            if mission.created_at and mission.completed_at:
                duration = (mission.completed_at - mission.created_at).total_seconds()
                mission_durations.append(duration)
        
        return {
            'uav_id': uav_id,
            'total_missions': len(missions),
            'completed_missions': len(completed_missions),
            'failed_missions': len(failed_missions),
            'success_rate': (len(completed_missions) / len(missions) * 100) if missions else 0,
            'total_detections': len(detections),
            'avg_mission_duration': np.mean(mission_durations) if mission_durations else 0,
            'total_flight_time': sum(mission_durations),
            'current_status': uav.status,
            'battery_level': uav.battery_level
        }


class CoverageAnalyzer:
    """
    Analyzes spatial coverage of the monitoring system.
    
    Implements Section 9.2: Coverage Analysis
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_coverage(
        self,
        start_time: datetime,
        end_time: datetime,
        grid_size_m: float = 100.0
    ) -> CoverageMetrics:
        """Calculate coverage metrics for a time period."""
        
        # Get all zones
        zones = self.db.query(Zone).all()
        
        if not zones:
            return CoverageMetrics(
                total_area_km2=0,
                covered_area_km2=0,
                coverage_percentage=0,
                gaps=[],
                overlap_percentage=0,
                coverage_by_zone={},
                heatmap_data=[]
            )
        
        # Calculate total area
        total_area_m2 = 0
        for zone in zones:
            # Approximate area from bounding box
            # In production, use PostGIS ST_Area
            lat_range = 0.1  # Default ~11km
            lon_range = 0.1  # Default ~11km at equator
            area_m2 = lat_range * lon_range * 111000 * 111000  # Rough approximation
            total_area_m2 += area_m2
        
        total_area_km2 = total_area_m2 / 1_000_000
        
        # Get all detections in the period
        detections = self.db.query(Detection).filter(
            Detection.timestamp.between(start_time, end_time)
        ).all()
        
        # Build coverage grid
        coverage_grid = {}
        overlap_count = 0
        
        for detection in detections:
            # Quantize detection location to grid
            grid_x = int(detection.latitude * 1000 / grid_size_m)
            grid_y = int(detection.longitude * 1000 / grid_size_m)
            grid_key = (grid_x, grid_y)
            
            if grid_key in coverage_grid:
                coverage_grid[grid_key] += 1
                overlap_count += 1
            else:
                coverage_grid[grid_key] = 1
        
        # Calculate covered area
        covered_cells = len(coverage_grid)
        cell_area_m2 = grid_size_m * grid_size_m
        covered_area_m2 = covered_cells * cell_area_m2
        covered_area_km2 = covered_area_m2 / 1_000_000
        
        coverage_percentage = (covered_area_km2 / total_area_km2 * 100) if total_area_km2 > 0 else 0
        overlap_percentage = (overlap_count / len(detections) * 100) if detections else 0
        
        # Coverage by zone
        coverage_by_zone = {}
        for zone in zones:
            zone_detections = [d for d in detections if self._point_in_zone(d, zone)]
            coverage_by_zone[zone.name] = len(zone_detections)
        
        # Generate heatmap data
        heatmap_data = []
        for (grid_x, grid_y), count in coverage_grid.items():
            lat = grid_x * grid_size_m / 1000
            lon = grid_y * grid_size_m / 1000
            heatmap_data.append({
                'latitude': lat,
                'longitude': lon,
                'intensity': count,
                'grid_x': grid_x,
                'grid_y': grid_y
            })
        
        # Identify gaps (simplified)
        gaps = []
        for zone in zones:
            zone_coverage = coverage_by_zone.get(zone.name, 0)
            if zone_coverage == 0:
                gaps.append({
                    'zone_name': zone.name,
                    'center_lat': zone.center_lat,
                    'center_lon': zone.center_lon,
                    'severity': 'critical'
                })
        
        return CoverageMetrics(
            total_area_km2=total_area_km2,
            covered_area_km2=covered_area_km2,
            coverage_percentage=coverage_percentage,
            gaps=gaps,
            overlap_percentage=overlap_percentage,
            coverage_by_zone=coverage_by_zone,
            heatmap_data=heatmap_data
        )
    
    def _point_in_zone(self, detection: Detection, zone: Zone) -> bool:
        """Check if detection is within zone bounds (simplified)."""
        # Simplified bounding box check
        # In production, use PostGIS ST_Contains
        lat_tolerance = 0.05  # ~5.5km
        lon_tolerance = 0.05
        
        return (
            abs(detection.latitude - zone.center_lat) < lat_tolerance and
            abs(detection.longitude - zone.center_lon) < lon_tolerance
        )
    
    def get_coverage_gaps(
        self,
        min_coverage_threshold: int = 1
    ) -> List[Dict]:
        """Identify areas with insufficient coverage."""
        zones = self.db.query(Zone).all()
        gaps = []
        
        for zone in zones:
            # Count detections in zone in last 24 hours
            since = datetime.utcnow() - timedelta(hours=24)
            detection_count = self.db.query(Detection).filter(
                Detection.timestamp >= since
            ).count()
            
            if detection_count < min_coverage_threshold:
                gaps.append({
                    'zone_id': zone.zone_id,
                    'zone_name': zone.name,
                    'center_lat': zone.center_lat,
                    'center_lon': zone.center_lon,
                    'detection_count': detection_count,
                    'severity': 'high' if detection_count == 0 else 'medium'
                })
        
        return gaps


class ResponseTimeTracker:
    """
    Tracks and analyzes response times.
    
    Implements Section 9.3: Response Time Analysis
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_response_metrics(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> ResponseMetrics:
        """Calculate response time metrics."""
        
        alerts = self.db.query(SatelliteAlert).filter(
            SatelliteAlert.timestamp.between(start_time, end_time)
        ).all()
        
        if not alerts:
            return ResponseMetrics(
                alert_to_assignment=0,
                assignment_to_launch=0,
                launch_to_arrival=0,
                total_response_time=0,
                response_time_by_priority={}
            )
        
        # Collect response time components
        alert_to_assignment_times = []
        assignment_to_launch_times = []
        launch_to_arrival_times = []
        total_response_times = []
        priority_response_times = {'high': [], 'medium': [], 'low': []}
        
        for alert in alerts:
            # Find associated mission
            mission = self.db.query(Mission).filter(
                Mission.satellite_alert_id == alert.alert_id
            ).first()
            
            if not mission:
                continue
            
            # Calculate time components
            if alert.timestamp and mission.created_at:
                alert_to_assignment = (mission.created_at - alert.timestamp).total_seconds()
                alert_to_assignment_times.append(max(0, alert_to_assignment))
            
            # For launch time, use mission start (simplified)
            # In production, track actual UAV takeoff time
            assignment_to_launch = 60.0  # Assume 60s average
            assignment_to_launch_times.append(assignment_to_launch)
            
            # For arrival time, use mission completion
            if mission.created_at and mission.completed_at:
                launch_to_arrival = (mission.completed_at - mission.created_at).total_seconds()
                launch_to_arrival_times.append(max(0, launch_to_arrival))
                
                # Total response time
                if alert.timestamp:
                    total_time = (mission.completed_at - alert.timestamp).total_seconds()
                    total_response_times.append(max(0, total_time))
                    
                    # Track by priority
                    priority = alert.priority.lower() if alert.priority else 'medium'
                    if priority in priority_response_times:
                        priority_response_times[priority].append(total_time)
        
        # Calculate averages
        return ResponseMetrics(
            alert_to_assignment=np.mean(alert_to_assignment_times) if alert_to_assignment_times else 0,
            assignment_to_launch=np.mean(assignment_to_launch_times) if assignment_to_launch_times else 0,
            launch_to_arrival=np.mean(launch_to_arrival_times) if launch_to_arrival_times else 0,
            total_response_time=np.mean(total_response_times) if total_response_times else 0,
            response_time_by_priority={
                priority: np.mean(times) if times else 0
                for priority, times in priority_response_times.items()
            }
        )
    
    def get_response_time_percentiles(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, float]:
        """Get response time percentiles."""
        
        missions = self.db.query(Mission).filter(
            Mission.created_at.between(start_time, end_time),
            Mission.status == 'completed'
        ).all()
        
        response_times = []
        for mission in missions:
            # Get associated alert
            alert = self.db.query(SatelliteAlert).filter(
                SatelliteAlert.alert_id == mission.satellite_alert_id
            ).first()
            
            if alert and alert.timestamp and mission.completed_at:
                response_time = (mission.completed_at - alert.timestamp).total_seconds()
                response_times.append(max(0, response_time))
        
        if not response_times:
            return {
                'p50': 0,
                'p75': 0,
                'p90': 0,
                'p95': 0,
                'p99': 0
            }
        
        return {
            'p50': float(np.percentile(response_times, 50)),
            'p75': float(np.percentile(response_times, 75)),
            'p90': float(np.percentile(response_times, 90)),
            'p95': float(np.percentile(response_times, 95)),
            'p99': float(np.percentile(response_times, 99))
        }
    
    def analyze_bottlenecks(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, any]:
        """Identify bottlenecks in the response pipeline."""
        
        metrics = self.calculate_response_metrics(start_time, end_time)
        
        # Identify the slowest component
        components = {
            'alert_to_assignment': metrics.alert_to_assignment,
            'assignment_to_launch': metrics.assignment_to_launch,
            'launch_to_arrival': metrics.launch_to_arrival
        }
        
        slowest_component = max(components.items(), key=lambda x: x[1])
        
        # Calculate component percentages
        total_time = sum(components.values())
        component_percentages = {
            name: (time / total_time * 100) if total_time > 0 else 0
            for name, time in components.items()
        }
        
        # Recommendations
        recommendations = []
        if metrics.alert_to_assignment > 60:
            recommendations.append({
                'issue': 'Slow alert-to-assignment',
                'time': metrics.alert_to_assignment,
                'suggestion': 'Implement automated mission assignment algorithm'
            })
        
        if metrics.assignment_to_launch > 120:
            recommendations.append({
                'issue': 'Slow UAV launch',
                'time': metrics.assignment_to_launch,
                'suggestion': 'Pre-position UAVs at strategic locations'
            })
        
        if metrics.launch_to_arrival > 600:
            recommendations.append({
                'issue': 'Long travel time to target',
                'time': metrics.launch_to_arrival,
                'suggestion': 'Deploy additional UAVs to reduce coverage distance'
            })
        
        return {
            'bottleneck': slowest_component[0],
            'bottleneck_time': slowest_component[1],
            'component_percentages': component_percentages,
            'total_response_time': metrics.total_response_time,
            'recommendations': recommendations
        }


class AnomalyDetector:
    """
    Detects anomalies in system behavior.
    
    Implements Section 9.4: Anomaly Detection
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def detect_performance_anomalies(
        self,
        lookback_hours: int = 24
    ) -> List[Dict]:
        """Detect performance anomalies using statistical analysis."""
        
        anomalies = []
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=lookback_hours)
        
        # Get hourly detection counts
        hourly_counts = []
        current = start_time
        
        while current < end_time:
            interval_end = current + timedelta(hours=1)
            count = self.db.query(Detection).filter(
                Detection.timestamp.between(current, interval_end)
            ).count()
            hourly_counts.append(count)
            current = interval_end
        
        if len(hourly_counts) < 3:
            return anomalies
        
        # Calculate statistics
        mean = np.mean(hourly_counts)
        std = np.std(hourly_counts)
        
        # Detect outliers (beyond 2 standard deviations)
        for i, count in enumerate(hourly_counts):
            z_score = (count - mean) / std if std > 0 else 0
            
            if abs(z_score) > 2:
                timestamp = start_time + timedelta(hours=i)
                anomalies.append({
                    'timestamp': timestamp.isoformat(),
                    'metric': 'detection_count',
                    'value': count,
                    'expected': mean,
                    'z_score': z_score,
                    'severity': 'high' if abs(z_score) > 3 else 'medium',
                    'description': f"Unusual detection count: {count} (expected ~{mean:.1f})"
                })
        
        return anomalies
    
    def detect_uav_anomalies(self) -> List[Dict]:
        """Detect anomalies in UAV behavior."""
        
        anomalies = []
        uavs = self.db.query(UAV).all()
        
        for uav in uavs:
            # Check battery anomalies
            if uav.battery_level < 20 and uav.status == 'active':
                anomalies.append({
                    'uav_id': uav.uav_id,
                    'anomaly_type': 'low_battery_active',
                    'severity': 'high',
                    'description': f'UAV {uav.uav_id} is active with low battery ({uav.battery_level}%)',
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Check communication anomalies
            if uav.last_contact:
                time_since_contact = (datetime.utcnow() - uav.last_contact).total_seconds()
                if time_since_contact > 300 and uav.status == 'active':  # 5 minutes
                    anomalies.append({
                        'uav_id': uav.uav_id,
                        'anomaly_type': 'communication_loss',
                        'severity': 'critical',
                        'description': f'No contact with {uav.uav_id} for {time_since_contact:.0f} seconds',
                        'timestamp': datetime.utcnow().isoformat()
                    })
        
        return anomalies
