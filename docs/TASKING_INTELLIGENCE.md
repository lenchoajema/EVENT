# Tasking & Follow-up Intelligence
## Coordinated Satellite & UAV Event-Analysis MVP

**Document Version:** 1.0  
**Date:** November 9, 2025  
**Parent Document:** [Threat Logic](./THREAT_LOGIC.md)

---

## 5. Tasking & Follow-up Intelligence

### 5.1 Satellite-to-UAV Trigger Pipeline

The EVENT system implements a **fully automated trigger pipeline** that translates satellite alerts into UAV reconnaissance missions with zero human intervention (in autonomous mode).

#### Alert Processing Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│ SATELLITE-TO-UAV TRIGGER PIPELINE                                       │
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐             │
│  │ 1. SATELLITE │───>│ 2. ALERT     │───>│ 3. MISSION   │             │
│  │    DETECTION │    │    TRIAGE    │    │    CREATION  │             │
│  └──────────────┘    └──────────────┘    └──────────────┘             │
│       │                     │                     │                      │
│       │ Imagery            │ Priority             │ Mission Plan         │
│       │ Metadata           │ Queue                │ Task Order           │
│       │ Confidence         │ Deduplication        │ Route                │
│       │                     │                     │                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐             │
│  │ 6. FOLLOW-UP │<───│ 5. UAV       │<───│ 4. UAV       │             │
│  │    INTEL     │    │    EXECUTION │    │    DISPATCH  │             │
│  └──────────────┘    └──────────────┘    └──────────────┘             │
│       │                     │                     │                      │
│       │ Confirmation       │ Live Feed            │ Best UAV             │
│       │ Evidence           │ Detections           │ Assignment           │
│       │ Report             │ Telemetry            │ Launch                │
│       │                     │                     │                      │
│  Total Latency: 45-90 seconds (alert → UAV airborne)                    │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Stage 1: Alert Ingestion

```python
from datetime import datetime
from enum import Enum
import asyncio

class AlertSource(Enum):
    SATELLITE = "satellite"
    GROUND_SENSOR = "ground"
    INTELLIGENCE = "intel"
    MANUAL = "manual"

class AlertPriority(Enum):
    CRITICAL = 1  # Border violation, armed group
    HIGH = 2      # Convoy, large group
    MEDIUM = 3    # Single vehicle, suspicious activity
    LOW = 4       # Routine monitoring

class SatelliteAlert:
    """
    Structured satellite alert with geospatial context.
    """
    def __init__(self, alert_data: dict):
        self.alert_id = alert_data['alert_id']
        self.source = AlertSource(alert_data['source'])
        self.timestamp = datetime.fromisoformat(alert_data['timestamp'])
        
        # Geospatial
        self.latitude = alert_data['latitude']
        self.longitude = alert_data['longitude']
        self.tile_id = alert_data.get('tile_id')
        
        # Detection details
        self.detection_class = alert_data['detection_class']
        self.confidence = alert_data['confidence']
        self.threat_score = alert_data.get('threat_score', 0.0)
        
        # Context
        self.geofence_violation = alert_data.get('geofence_violation', False)
        self.behavior_tags = alert_data.get('behavior_tags', [])
        self.nearby_poi = alert_data.get('nearby_poi', [])
        
        # Priority calculation
        self.priority = self._calculate_priority()
        
        # State tracking
        self.status = 'pending'
        self.assigned_mission = None
        self.processed_at = None
    
    def _calculate_priority(self) -> AlertPriority:
        """
        Calculate alert priority based on multiple factors.
        
        Priority Matrix:
        ┌─────────────────┬──────────────────────────────────┐
        │ Factor          │ Impact                           │
        ├─────────────────┼──────────────────────────────────┤
        │ Geofence Tier 4 │ CRITICAL (override all)          │
        │ Armed Detection │ CRITICAL                         │
        │ Convoy (5+ veh) │ HIGH                             │
        │ Border Probe    │ HIGH                             │
        │ Group (3+ pers) │ MEDIUM                           │
        │ Single Entity   │ MEDIUM (if high confidence)      │
        │ Routine Scan    │ LOW                              │
        └─────────────────┴──────────────────────────────────┘
        """
        # Critical overrides
        if self.geofence_violation:
            fence_type = self.geofence_violation.get('fence_type')
            if fence_type == 'EXCLUSION':
                return AlertPriority.CRITICAL
        
        if 'armed' in self.behavior_tags or 'weapon' in self.detection_class:
            return AlertPriority.CRITICAL
        
        # High priority
        if 'convoy' in self.behavior_tags:
            return AlertPriority.HIGH
        
        if 'border_probing' in self.behavior_tags:
            return AlertPriority.HIGH
        
        if self.threat_score >= 0.85:
            return AlertPriority.HIGH
        
        # Medium priority
        if 'group' in self.behavior_tags:
            return AlertPriority.MEDIUM
        
        if self.confidence >= 0.80 and self.threat_score >= 0.70:
            return AlertPriority.MEDIUM
        
        # Default to low
        return AlertPriority.LOW
    
    def to_dict(self) -> dict:
        """Serialize alert for database storage."""
        return {
            'alert_id': self.alert_id,
            'source': self.source.value,
            'timestamp': self.timestamp.isoformat(),
            'latitude': self.latitude,
            'longitude': self.longitude,
            'tile_id': self.tile_id,
            'detection_class': self.detection_class,
            'confidence': self.confidence,
            'threat_score': self.threat_score,
            'priority': self.priority.name,
            'status': self.status,
            'geofence_violation': self.geofence_violation,
            'behavior_tags': self.behavior_tags
        }
```

#### Stage 2: Alert Triage & Deduplication

```python
from collections import defaultdict
from typing import List, Optional

class AlertTriageEngine:
    """
    Intelligent alert processing with deduplication and clustering.
    """
    
    def __init__(self):
        self.alert_queue = defaultdict(list)  # priority -> [alerts]
        self.processed_alerts = {}  # alert_id -> status
        self.spatial_index = {}  # (lat, lon) grid -> alert_ids
    
    async def process_alert(self, alert: SatelliteAlert) -> dict:
        """
        Process incoming alert through triage pipeline.
        
        Steps:
        1. Deduplication check
        2. Spatial clustering
        3. Priority queue insertion
        4. Trigger mission creation
        """
        # Step 1: Check for duplicates
        duplicate = self._find_duplicate(alert)
        if duplicate:
            return {
                'status': 'duplicate',
                'merged_with': duplicate.alert_id,
                'action': 'merged'
            }
        
        # Step 2: Find spatially related alerts
        cluster = self._find_spatial_cluster(alert)
        if cluster:
            # Merge into existing cluster
            return await self._merge_into_cluster(alert, cluster)
        
        # Step 3: Add to priority queue
        self.alert_queue[alert.priority].append(alert)
        self.processed_alerts[alert.alert_id] = 'queued'
        
        # Step 4: Trigger mission creation
        mission = await self._trigger_mission_creation(alert)
        
        return {
            'status': 'processed',
            'alert_id': alert.alert_id,
            'priority': alert.priority.name,
            'mission_id': mission['mission_id'] if mission else None,
            'action': 'mission_created'
        }
    
    def _find_duplicate(self, alert: SatelliteAlert,
                       time_window: int = 300) -> Optional[SatelliteAlert]:
        """
        Find duplicate alerts within time/space window.
        
        Duplicate criteria:
        - Same detection class
        - Within 50m distance
        - Within 5 minute time window
        """
        for existing_alert in self._get_recent_alerts(time_window):
            if existing_alert.detection_class != alert.detection_class:
                continue
            
            distance = haversine_distance(
                (existing_alert.latitude, existing_alert.longitude),
                (alert.latitude, alert.longitude)
            )
            
            if distance < 50:  # 50 meters
                time_delta = abs(
                    (alert.timestamp - existing_alert.timestamp).total_seconds()
                )
                if time_delta < time_window:
                    return existing_alert
        
        return None
    
    def _find_spatial_cluster(self, alert: SatelliteAlert,
                             radius: float = 200) -> Optional[List]:
        """
        Find alerts within clustering radius.
        
        Used to identify related events (e.g., convoy members).
        """
        cluster = []
        
        for existing_alert in self._get_pending_alerts():
            distance = haversine_distance(
                (existing_alert.latitude, existing_alert.longitude),
                (alert.latitude, alert.longitude)
            )
            
            if distance <= radius:
                cluster.append(existing_alert)
        
        return cluster if len(cluster) >= 2 else None
    
    async def _merge_into_cluster(self, alert: SatelliteAlert,
                                  cluster: List[SatelliteAlert]) -> dict:
        """
        Merge alert into existing cluster and escalate priority.
        """
        # Update cluster priority (take highest)
        cluster_priority = min(
            [a.priority for a in cluster] + [alert.priority],
            key=lambda p: p.value
        )
        
        # Add to cluster
        cluster.append(alert)
        
        # Check if this creates a convoy pattern
        if len(cluster) >= 3:
            # Escalate to convoy detection
            return await self._create_convoy_mission(cluster)
        
        return {
            'status': 'clustered',
            'cluster_size': len(cluster),
            'cluster_priority': cluster_priority.name
        }
    
    async def _trigger_mission_creation(self, 
                                       alert: SatelliteAlert) -> dict:
        """
        Automatically create UAV mission for alert.
        """
        # Only create missions for MEDIUM and above
        if alert.priority.value > AlertPriority.MEDIUM.value:
            return {'status': 'low_priority', 'mission_id': None}
        
        # Create mission
        mission = await MissionPlanner.create_from_alert(alert)
        
        # Link alert to mission
        alert.assigned_mission = mission['mission_id']
        alert.status = 'mission_created'
        alert.processed_at = datetime.now()
        
        return mission
    
    def _get_recent_alerts(self, seconds: int) -> List[SatelliteAlert]:
        """Get alerts from last N seconds."""
        cutoff = datetime.now().timestamp() - seconds
        return [
            alert for priority_alerts in self.alert_queue.values()
            for alert in priority_alerts
            if alert.timestamp.timestamp() > cutoff
        ]
    
    def _get_pending_alerts(self) -> List[SatelliteAlert]:
        """Get all alerts awaiting mission assignment."""
        return [
            alert for priority_alerts in self.alert_queue.values()
            for alert in priority_alerts
            if alert.status == 'queued'
        ]
```

---

### 5.2 UAV Close-Scout Standard Operating Procedure

Once a UAV is dispatched, it follows a **standardized close-scout protocol** to maximize intelligence value.

#### Scout Mission Phases

```
┌─────────────────────────────────────────────────────────────────────────┐
│ CLOSE-SCOUT MISSION PHASES                                              │
│                                                                          │
│  PHASE 1: TRANSIT (30-120s)                                             │
│  ├─ Direct route to alert coordinates                                   │
│  ├─ High speed (15 m/s)                                                 │
│  ├─ Camera in standby mode                                              │
│  └─ Continuous telemetry streaming                                      │
│                                                                          │
│  PHASE 2: APPROACH (15-30s)                                             │
│  ├─ Reduce speed to 8 m/s                                               │
│  ├─ Activate optical + thermal cameras                                  │
│  ├─ Begin wide-area scan (spiral pattern)                               │
│  └─ Initial target acquisition                                          │
│                                                                          │
│  PHASE 3: RECONNAISSANCE (2-10 min)                                     │
│  ├─ Orbit target at 100m radius                                         │
│  ├─ Multi-angle image capture                                           │
│  ├─ Thermal signature analysis                                          │
│  ├─ Activity classification                                             │
│  ├─ Count persons/vehicles                                              │
│  └─ Capture evidence (photos/video)                                     │
│                                                                          │
│  PHASE 4: FOLLOW-UP (Variable)                                          │
│  ├─ If threat confirmed: Continue surveillance                          │
│  ├─ If threat mobile: Initiate tracking mode                            │
│  ├─ If false alarm: Mark area clear, RTB                                │
│  └─ If backup needed: Request additional UAVs                           │
│                                                                          │
│  PHASE 5: RETURN (30-120s)                                              │
│  ├─ Return to base or next mission                                      │
│  ├─ Data sync (if not continuous)                                       │
│  └─ Post-mission debrief (automated)                                    │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Scout Mission Executor

```python
import asyncio
from typing import Tuple, Optional

class ScoutMissionExecutor:
    """
    Execute close-scout reconnaissance mission.
    """
    
    PHASE_CONFIG = {
        'transit': {
            'speed': 15.0,  # m/s
            'altitude': 80,  # meters AGL
            'camera_mode': 'standby'
        },
        'approach': {
            'speed': 8.0,
            'altitude': 60,
            'camera_mode': 'wide_scan'
        },
        'reconnaissance': {
            'speed': 5.0,
            'altitude': 50,
            'camera_mode': 'focused'
        },
        'tracking': {
            'speed': 'match_target',  # Dynamic
            'altitude': 70,
            'camera_mode': 'locked'
        }
    }
    
    def __init__(self, uav_id: str, mission: dict):
        self.uav_id = uav_id
        self.mission = mission
        self.current_phase = 'transit'
        self.target_position = (mission['latitude'], mission['longitude'])
        self.evidence_collected = []
        self.mission_log = []
    
    async def execute(self) -> dict:
        """
        Execute full scout mission sequence.
        """
        self._log_event('MISSION_START')
        
        try:
            # Phase 1: Transit
            await self._phase_transit()
            
            # Phase 2: Approach
            await self._phase_approach()
            
            # Phase 3: Reconnaissance
            recon_result = await self._phase_reconnaissance()
            
            # Phase 4: Follow-up (conditional)
            if recon_result['threat_confirmed']:
                followup_result = await self._phase_followup(recon_result)
            else:
                followup_result = {'action': 'rtb', 'reason': 'false_alarm'}
            
            # Phase 5: Return
            await self._phase_return()
            
            self._log_event('MISSION_COMPLETE')
            
            return {
                'mission_id': self.mission['mission_id'],
                'status': 'completed',
                'outcome': followup_result,
                'evidence': self.evidence_collected,
                'log': self.mission_log
            }
        
        except Exception as e:
            self._log_event('MISSION_FAILED', {'error': str(e)})
            return {
                'mission_id': self.mission['mission_id'],
                'status': 'failed',
                'error': str(e)
            }
    
    async def _phase_transit(self):
        """
        Phase 1: Navigate to target area.
        """
        self.current_phase = 'transit'
        config = self.PHASE_CONFIG['transit']
        
        self._log_event('PHASE_TRANSIT_START')
        
        # Calculate route
        current_position = await self._get_uav_position()
        waypoints = self._calculate_direct_route(
            current_position, self.target_position
        )
        
        # Execute flight
        for waypoint in waypoints:
            await self._fly_to_waypoint(
                waypoint, 
                speed=config['speed'],
                altitude=config['altitude']
            )
            
            # Check for dynamic re-tasking
            if await self._check_priority_override():
                return
        
        self._log_event('PHASE_TRANSIT_COMPLETE')
    
    async def _phase_approach(self):
        """
        Phase 2: Slow approach with sensor activation.
        """
        self.current_phase = 'approach'
        config = self.PHASE_CONFIG['approach']
        
        self._log_event('PHASE_APPROACH_START')
        
        # Reduce speed
        await self._set_speed(config['speed'])
        await self._set_altitude(config['altitude'])
        
        # Activate sensors
        await self._activate_camera('optical')
        await self._activate_camera('thermal')
        
        # Begin spiral approach
        spiral_waypoints = self._generate_spiral_pattern(
            center=self.target_position,
            radius_start=500,
            radius_end=100,
            turns=2
        )
        
        # Fly spiral while scanning
        for waypoint in spiral_waypoints:
            await self._fly_to_waypoint(waypoint, speed=config['speed'])
            
            # Attempt target acquisition
            detection = await self._scan_for_target()
            if detection:
                self.target_position = detection['position']
                self._log_event('TARGET_ACQUIRED', detection)
                break
        
        self._log_event('PHASE_APPROACH_COMPLETE')
    
    async def _phase_reconnaissance(self) -> dict:
        """
        Phase 3: Detailed reconnaissance of target.
        """
        self.current_phase = 'reconnaissance'
        config = self.PHASE_CONFIG['reconnaissance']
        
        self._log_event('PHASE_RECON_START')
        
        # Establish orbit
        orbit_waypoints = self._generate_orbit_pattern(
            center=self.target_position,
            radius=100,
            altitude=config['altitude']
        )
        
        # Reconnaissance loop
        start_time = datetime.now()
        max_duration = 600  # 10 minutes
        
        detections = []
        while (datetime.now() - start_time).total_seconds() < max_duration:
            # Fly orbit segment
            for waypoint in orbit_waypoints:
                await self._fly_to_waypoint(waypoint, speed=config['speed'])
                
                # Capture data
                frame = await self._capture_frame()
                detection = await self._analyze_frame(frame)
                
                if detection:
                    detections.append(detection)
                    
                    # Capture evidence
                    evidence = await self._collect_evidence(detection)
                    self.evidence_collected.append(evidence)
            
            # Check if we have enough data
            if len(detections) >= 5:
                break
        
        # Analyze all detections
        analysis = self._analyze_reconnaissance_data(detections)
        
        self._log_event('PHASE_RECON_COMPLETE', analysis)
        
        return analysis
    
    async def _phase_followup(self, recon_result: dict) -> dict:
        """
        Phase 4: Follow-up based on reconnaissance findings.
        """
        threat_level = recon_result['threat_level']
        target_mobile = recon_result.get('target_moving', False)
        
        self._log_event('PHASE_FOLLOWUP_START', {
            'threat_level': threat_level,
            'target_mobile': target_mobile
        })
        
        if threat_level == 'CRITICAL':
            # Request backup
            await self._request_backup_uavs(count=2)
            
            if target_mobile:
                # Switch to tracking mode
                return await self._initiate_tracking_mode(recon_result)
            else:
                # Continue surveillance
                return await self._continue_surveillance(duration=1800)  # 30 min
        
        elif threat_level == 'HIGH':
            if target_mobile:
                return await self._initiate_tracking_mode(recon_result)
            else:
                return await self._continue_surveillance(duration=600)  # 10 min
        
        else:
            # False alarm or low threat
            return {
                'action': 'rtb',
                'reason': 'threat_level_low',
                'threat_level': threat_level
            }
    
    async def _initiate_tracking_mode(self, target_info: dict) -> dict:
        """
        Switch to active target tracking.
        """
        self.current_phase = 'tracking'
        config = self.PHASE_CONFIG['tracking']
        
        self._log_event('TRACKING_MODE_START')
        
        # Initialize tracker
        tracker = TargetTracker()
        track = tracker._create_track({
            'position': target_info['position'],
            'class': target_info['detection_class'],
            'velocity': target_info.get('velocity', (0, 0))
        })
        
        # Tracking loop
        tracking_duration = 1800  # 30 minutes max
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < tracking_duration:
            # Get predicted position
            predicted_pos = track.predicted_position
            
            # Adjust UAV position to maintain standoff distance
            standoff_distance = 150  # meters
            follow_position = self._calculate_follow_position(
                predicted_pos, standoff_distance
            )
            
            await self._fly_to_waypoint(follow_position, speed=8.0)
            
            # Update track
            frame = await self._capture_frame()
            detection = await self._analyze_frame(frame)
            
            if detection:
                track.update(detection)
                self.evidence_collected.append(
                    await self._collect_evidence(detection)
                )
            else:
                # Target lost
                self._log_event('TARGET_LOST')
                break
            
            # Check if target stopped
            if track.velocity[0]**2 + track.velocity[1]**2 < 0.25:  # <0.5 m/s
                self._log_event('TARGET_STOPPED')
                # Switch back to reconnaissance
                return await self._continue_surveillance(duration=600)
        
        self._log_event('TRACKING_MODE_COMPLETE')
        
        return {
            'action': 'tracking_completed',
            'duration': (datetime.now() - start_time).total_seconds(),
            'evidence_count': len(self.evidence_collected)
        }
    
    async def _continue_surveillance(self, duration: int) -> dict:
        """
        Maintain surveillance for specified duration.
        """
        self._log_event('SURVEILLANCE_START', {'duration': duration})
        
        start_time = datetime.now()
        capture_interval = 30  # seconds
        
        while (datetime.now() - start_time).total_seconds() < duration:
            # Maintain orbit
            await self._maintain_orbit(self.target_position, radius=100)
            
            # Periodic capture
            await asyncio.sleep(capture_interval)
            
            frame = await self._capture_frame()
            detection = await self._analyze_frame(frame)
            
            if detection:
                evidence = await self._collect_evidence(detection)
                self.evidence_collected.append(evidence)
        
        self._log_event('SURVEILLANCE_COMPLETE')
        
        return {
            'action': 'surveillance_completed',
            'duration': duration,
            'evidence_count': len(self.evidence_collected)
        }
    
    def _analyze_reconnaissance_data(self, detections: List[dict]) -> dict:
        """
        Analyze all reconnaissance detections to determine threat.
        """
        if not detections:
            return {
                'threat_confirmed': False,
                'threat_level': 'NONE',
                'confidence': 0.0,
                'reason': 'no_detections'
            }
        
        # Calculate average confidence
        avg_confidence = sum(d['confidence'] for d in detections) / len(detections)
        
        # Determine detection class
        classes = [d['detection_class'] for d in detections]
        primary_class = max(set(classes), key=classes.count)
        
        # Count entities
        entity_count = len(set(d.get('track_id', i) for i, d in enumerate(detections)))
        
        # Calculate threat score
        threat_score = 0.0
        
        if primary_class in ['person', 'vehicle']:
            threat_score += 0.40
        
        if entity_count >= 5:
            threat_score += 0.30
        elif entity_count >= 3:
            threat_score += 0.20
        
        if avg_confidence >= 0.85:
            threat_score += 0.20
        
        # Check for suspicious behaviors
        behaviors = [b for d in detections for b in d.get('behavior_tags', [])]
        if any(b in ['evasive', 'border_probing', 'stealth_pathing'] for b in behaviors):
            threat_score += 0.30
        
        # Determine threat level
        if threat_score >= 0.85:
            threat_level = 'CRITICAL'
        elif threat_score >= 0.70:
            threat_level = 'HIGH'
        elif threat_score >= 0.50:
            threat_level = 'MEDIUM'
        else:
            threat_level = 'LOW'
        
        return {
            'threat_confirmed': threat_score >= 0.50,
            'threat_level': threat_level,
            'threat_score': threat_score,
            'confidence': avg_confidence,
            'detection_class': primary_class,
            'entity_count': entity_count,
            'detections': len(detections),
            'target_moving': self._is_target_moving(detections)
        }
    
    def _is_target_moving(self, detections: List[dict]) -> bool:
        """Check if target exhibits movement."""
        if len(detections) < 2:
            return False
        
        positions = [d['position'] for d in detections]
        total_displacement = 0
        
        for i in range(1, len(positions)):
            dist = haversine_distance(positions[i-1], positions[i])
            total_displacement += dist
        
        # Moving if total displacement > 20 meters
        return total_displacement > 20
    
    def _log_event(self, event_type: str, data: dict = None):
        """Log mission event."""
        self.mission_log.append({
            'timestamp': datetime.now().isoformat(),
            'event': event_type,
            'phase': self.current_phase,
            'data': data or {}
        })
```

---

### 5.3 Multi-Sensor Confirmation Strategy

The EVENT system employs **multi-sensor fusion** to reduce false positives and increase detection confidence.

#### Sensor Fusion Architecture

```python
from typing import List, Dict
import numpy as np

class MultiSensorFusion:
    """
    Fuse detections from multiple sensors for confirmation.
    """
    
    SENSOR_WEIGHTS = {
        'optical': 0.40,
        'thermal': 0.35,
        'radar': 0.25
    }
    
    SENSOR_RELIABILITY = {
        'optical': {
            'day_clear': 0.95,
            'day_overcast': 0.85,
            'night_clear': 0.40,
            'night_overcast': 0.20
        },
        'thermal': {
            'day_clear': 0.90,
            'day_overcast': 0.90,
            'night_clear': 0.95,
            'night_overcast': 0.85
        },
        'radar': {
            'day_clear': 0.75,
            'day_overcast': 0.75,
            'night_clear': 0.75,
            'night_overcast': 0.70
        }
    }
    
    def fuse_detections(self, detections: List[dict],
                       environment: dict) -> dict:
        """
        Fuse multi-sensor detections into single confirmed detection.
        
        Args:
            detections: List of detections from different sensors
            environment: Environmental conditions (time, weather)
        
        Returns:
            Fused detection with enhanced confidence
        """
        if not detections:
            return None
        
        # Group by sensor type
        sensor_detections = self._group_by_sensor(detections)
        
        # Calculate weighted confidence
        fused_confidence = self._calculate_fused_confidence(
            sensor_detections, environment
        )
        
        # Spatial consistency check
        spatial_consistent = self._check_spatial_consistency(detections)
        
        # Temporal consistency check
        temporal_consistent = self._check_temporal_consistency(detections)
        
        # Class agreement
        class_agreement = self._calculate_class_agreement(detections)
        
        # Final confidence adjustment
        final_confidence = fused_confidence
        
        if spatial_consistent:
            final_confidence += 0.10
        
        if temporal_consistent:
            final_confidence += 0.10
        
        if class_agreement >= 0.80:
            final_confidence += 0.10
        
        # Cap at 0.99
        final_confidence = min(final_confidence, 0.99)
        
        # Create fused detection
        primary_detection = max(detections, key=lambda d: d['confidence'])
        
        return {
            'detection_id': f"FUSED_{primary_detection['detection_id']}",
            'position': self._calculate_consensus_position(detections),
            'detection_class': self._get_consensus_class(detections),
            'confidence': final_confidence,
            'sensor_count': len(sensor_detections),
            'sensors_used': list(sensor_detections.keys()),
            'spatial_consistent': spatial_consistent,
            'temporal_consistent': temporal_consistent,
            'class_agreement': class_agreement,
            'source_detections': detections
        }
    
    def _group_by_sensor(self, detections: List[dict]) -> Dict[str, List]:
        """Group detections by sensor type."""
        groups = {}
        for det in detections:
            sensor = det.get('sensor_type', 'unknown')
            if sensor not in groups:
                groups[sensor] = []
            groups[sensor].append(det)
        return groups
    
    def _calculate_fused_confidence(self, sensor_detections: dict,
                                    environment: dict) -> float:
        """
        Calculate weighted confidence across sensors.
        
        Bayesian fusion formula:
        P(target | sensors) = 1 - ∏(1 - P(target | sensor_i))
        """
        # Get environmental condition
        time_of_day = environment.get('time_of_day', 'day')  # day/night
        weather = environment.get('weather', 'clear')  # clear/overcast/rain
        condition = f"{time_of_day}_{weather}"
        
        # Calculate per-sensor confidence
        sensor_confidences = []
        for sensor_type, detections in sensor_detections.items():
            # Average confidence from this sensor
            avg_conf = np.mean([d['confidence'] for d in detections])
            
            # Apply reliability factor
            reliability = self.SENSOR_RELIABILITY.get(sensor_type, {}).get(
                condition, 0.70
            )
            
            # Adjusted confidence
            adjusted_conf = avg_conf * reliability
            sensor_confidences.append(adjusted_conf)
        
        # Bayesian fusion
        fused = 1.0 - np.prod([1.0 - c for c in sensor_confidences])
        
        return fused
    
    def _check_spatial_consistency(self, detections: List[dict],
                                   threshold: float = 10.0) -> bool:
        """
        Check if all detections are spatially consistent.
        
        Consistent if all within threshold meters of centroid.
        """
        positions = [d['position'] for d in detections]
        
        # Calculate centroid
        centroid = (
            np.mean([p[0] for p in positions]),
            np.mean([p[1] for p in positions])
        )
        
        # Check distances
        for pos in positions:
            dist = haversine_distance(centroid, pos)
            if dist > threshold:
                return False
        
        return True
    
    def _check_temporal_consistency(self, detections: List[dict],
                                   window: float = 5.0) -> bool:
        """
        Check if detections are temporally close.
        
        Consistent if all within window seconds.
        """
        timestamps = [
            datetime.fromisoformat(d['timestamp']) for d in detections
        ]
        
        min_time = min(timestamps)
        max_time = max(timestamps)
        
        delta = (max_time - min_time).total_seconds()
        
        return delta <= window
    
    def _calculate_class_agreement(self, detections: List[dict]) -> float:
        """
        Calculate agreement on detection class.
        
        Returns ratio of detections agreeing with majority class.
        """
        classes = [d['detection_class'] for d in detections]
        
        # Find majority class
        majority_class = max(set(classes), key=classes.count)
        
        # Calculate agreement ratio
        agreement = classes.count(majority_class) / len(classes)
        
        return agreement
    
    def _calculate_consensus_position(self, 
                                     detections: List[dict]) -> Tuple[float, float]:
        """Calculate weighted average position."""
        total_weight = sum(d['confidence'] for d in detections)
        
        weighted_lat = sum(
            d['position'][0] * d['confidence'] for d in detections
        ) / total_weight
        
        weighted_lon = sum(
            d['position'][1] * d['confidence'] for d in detections
        ) / total_weight
        
        return (weighted_lat, weighted_lon)
    
    def _get_consensus_class(self, detections: List[dict]) -> str:
        """Get majority-vote detection class."""
        classes = [d['detection_class'] for d in detections]
        return max(set(classes), key=classes.count)
```

---

### 5.4 Tactical Routing Algorithm

UAVs use **intelligent routing** that balances speed, safety, and sensor coverage.

#### Routing Objectives

```python
from scipy.optimize import minimize
from typing import List, Tuple

class TacticalRouter:
    """
    Calculate optimal UAV routes considering multiple objectives.
    
    Objectives:
    1. Minimize flight time
    2. Maximize terrain masking (stay low when possible)
    3. Avoid detection by ground observers
    4. Maintain communication links
    5. Avoid restricted airspace
    """
    
    def __init__(self, terrain_data: dict, threats: List[dict]):
        self.terrain = terrain_data
        self.threats = threats
        self.comm_towers = []  # Communication relay points
    
    def calculate_route(self, start: Tuple[float, float],
                       end: Tuple[float, float],
                       priority: str = 'balanced') -> List[Tuple]:
        """
        Calculate optimal route from start to end.
        
        Priorities:
        - 'speed': Direct route, minimize time
        - 'stealth': Terrain following, avoid detection
        - 'balanced': Balance speed and safety
        """
        if priority == 'speed':
            return self._direct_route(start, end)
        elif priority == 'stealth':
            return self._stealth_route(start, end)
        else:
            return self._balanced_route(start, end)
    
    def _direct_route(self, start: Tuple, end: Tuple) -> List[Tuple]:
        """
        Direct line route (fastest).
        """
        # Simple straight line with waypoints every 500m
        distance = haversine_distance(start, end)
        num_waypoints = int(distance / 500) + 1
        
        waypoints = []
        for i in range(num_waypoints + 1):
            t = i / num_waypoints
            lat = start[0] + t * (end[0] - start[0])
            lon = start[1] + t * (end[1] - start[1])
            waypoints.append((lat, lon))
        
        return waypoints
    
    def _stealth_route(self, start: Tuple, end: Tuple) -> List[Tuple]:
        """
        Route that maximizes terrain masking and minimizes exposure.
        """
        # Use A* with custom cost function
        def cost_function(waypoint):
            # Base cost: distance
            cost = haversine_distance(waypoint, end)
            
            # Penalty for high elevation (visible)
            elevation = self._get_elevation(waypoint)
            if elevation > 100:  # Above 100m AGL
                cost += 1000 * (elevation - 100)
            
            # Penalty for proximity to threats
            for threat in self.threats:
                threat_pos = threat['position']
                distance = haversine_distance(waypoint, threat_pos)
                detection_range = threat.get('detection_range', 500)
                
                if distance < detection_range:
                    cost += 5000 * (1 - distance / detection_range)
            
            # Bonus for terrain cover
            if self._has_terrain_cover(waypoint):
                cost -= 500
            
            return cost
        
        # Run A* pathfinding
        route = self._astar_search(start, end, cost_function)
        
        return route
    
    def _balanced_route(self, start: Tuple, end: Tuple) -> List[Tuple]:
        """
        Balance between speed and safety.
        """
        # Multi-objective optimization
        def objective(waypoint_params):
            # Reconstruct waypoints from parameters
            waypoints = self._params_to_waypoints(waypoint_params, start, end)
            
            # Calculate costs
            time_cost = self._calculate_flight_time(waypoints)
            exposure_cost = self._calculate_exposure(waypoints)
            
            # Weighted sum
            return 0.6 * time_cost + 0.4 * exposure_cost
        
        # Initial guess (direct route)
        initial_waypoints = self._direct_route(start, end)
        initial_params = self._waypoints_to_params(initial_waypoints)
        
        # Optimize
        result = minimize(
            objective,
            initial_params,
            method='SLSQP',
            bounds=self._get_bounds(start, end)
        )
        
        # Convert back to waypoints
        optimal_waypoints = self._params_to_waypoints(result.x, start, end)
        
        return optimal_waypoints
    
    def _calculate_flight_time(self, waypoints: List[Tuple]) -> float:
        """Calculate total flight time for route."""
        total_distance = 0
        for i in range(1, len(waypoints)):
            total_distance += haversine_distance(waypoints[i-1], waypoints[i])
        
        # Assume 12 m/s average speed
        return total_distance / 12.0
    
    def _calculate_exposure(self, waypoints: List[Tuple]) -> float:
        """
        Calculate cumulative exposure to threats.
        """
        exposure = 0
        
        for waypoint in waypoints:
            for threat in self.threats:
                threat_pos = threat['position']
                distance = haversine_distance(waypoint, threat_pos)
                detection_range = threat.get('detection_range', 500)
                
                if distance < detection_range:
                    # Exposure proportional to time in detection range
                    exposure += (1 - distance / detection_range) ** 2
        
        return exposure
```

---

### 5.5 Mission Queue & Resource Allocation

The EVENT system manages **multiple concurrent missions** with intelligent UAV assignment.

#### Resource Allocator

```python
from queue import PriorityQueue
from typing import List, Optional

class MissionAllocator:
    """
    Allocate UAV resources to mission queue.
    """
    
    def __init__(self, uav_fleet: List[dict]):
        self.uav_fleet = {uav['uav_id']: uav for uav in uav_fleet}
        self.mission_queue = PriorityQueue()
        self.active_missions = {}  # mission_id -> uav_id
    
    def add_mission(self, mission: dict):
        """
        Add mission to queue with priority.
        """
        priority = mission['priority'].value  # Lower number = higher priority
        
        # Add timestamp as tiebreaker
        timestamp = datetime.now().timestamp()
        
        self.mission_queue.put((priority, timestamp, mission))
    
    def allocate_resources(self) -> List[dict]:
        """
        Assign UAVs to pending missions.
        
        Allocation strategy:
        1. Prioritize critical missions
        2. Assign closest available UAV
        3. Consider battery reserves
        4. Maintain fleet readiness (don't deplete all UAVs)
        """
        allocations = []
        
        # Get available UAVs
        available_uavs = self._get_available_uavs()
        
        # Reserve 20% of fleet for emergency response
        reserve_count = max(1, int(len(self.uav_fleet) * 0.20))
        max_allocations = len(available_uavs) - reserve_count
        
        # Process queue
        missions_allocated = 0
        while not self.mission_queue.empty() and missions_allocated < max_allocations:
            _, _, mission = self.mission_queue.get()
            
            # Find best UAV for this mission
            best_uav = self._select_best_uav(mission, available_uavs)
            
            if best_uav:
                # Allocate
                allocation = {
                    'mission_id': mission['mission_id'],
                    'uav_id': best_uav['uav_id'],
                    'assigned_at': datetime.now().isoformat(),
                    'eta': self._calculate_eta(best_uav, mission)
                }
                
                allocations.append(allocation)
                self.active_missions[mission['mission_id']] = best_uav['uav_id']
                
                # Remove from available pool
                available_uavs.remove(best_uav)
                missions_allocated += 1
            else:
                # No suitable UAV, put mission back in queue
                self.mission_queue.put((mission['priority'].value, 
                                       datetime.now().timestamp(), 
                                       mission))
                break
        
        return allocations
    
    def _get_available_uavs(self) -> List[dict]:
        """Get UAVs that are available for new missions."""
        available = []
        
        for uav_id, uav in self.uav_fleet.items():
            # Check if already on mission
            if uav_id in self.active_missions.values():
                continue
            
            # Check battery level
            if uav['battery_percent'] < 30:
                continue
            
            # Check maintenance status
            if uav.get('status') != 'ready':
                continue
            
            available.append(uav)
        
        return available
    
    def _select_best_uav(self, mission: dict, 
                        candidates: List[dict]) -> Optional[dict]:
        """
        Select best UAV for mission based on multiple factors.
        
        Scoring factors:
        - Distance to mission (40%)
        - Battery level (30%)
        - Sensor capabilities (20%)
        - Historical performance (10%)
        """
        if not candidates:
            return None
        
        mission_pos = (mission['latitude'], mission['longitude'])
        
        best_uav = None
        best_score = -float('inf')
        
        for uav in candidates:
            score = 0
            
            # Factor 1: Distance (closer is better)
            distance = haversine_distance(
                (uav['latitude'], uav['longitude']),
                mission_pos
            )
            distance_score = 1.0 / (1.0 + distance / 1000)  # Normalize by 1km
            score += 0.40 * distance_score
            
            # Factor 2: Battery (more is better)
            battery_score = uav['battery_percent'] / 100.0
            score += 0.30 * battery_score
            
            # Factor 3: Sensor capabilities
            required_sensors = mission.get('required_sensors', ['optical'])
            available_sensors = uav.get('sensors', ['optical'])
            
            sensor_match = len(
                set(required_sensors) & set(available_sensors)
            ) / len(required_sensors)
            score += 0.20 * sensor_match
            
            # Factor 4: Performance history
            success_rate = uav.get('mission_success_rate', 0.90)
            score += 0.10 * success_rate
            
            if score > best_score:
                best_score = score
                best_uav = uav
        
        return best_uav
    
    def _calculate_eta(self, uav: dict, mission: dict) -> float:
        """Calculate estimated time of arrival in seconds."""
        distance = haversine_distance(
            (uav['latitude'], uav['longitude']),
            (mission['latitude'], mission['longitude'])
        )
        
        # Assume 12 m/s cruise speed
        flight_time = distance / 12.0
        
        # Add takeoff time if UAV is on ground
        if uav.get('status') == 'ready' and not uav.get('airborne'):
            flight_time += 15  # 15 second launch
        
        return flight_time
```

---

## Key Takeaways

✅ **Automated alert triage** with deduplication and spatial clustering  
✅ **5-phase scout mission** protocol (transit → approach → recon → follow-up → return)  
✅ **Multi-sensor fusion** increases confidence by 10-30% over single-sensor  
✅ **Tactical routing** balances speed (60%) and safety (40%) with terrain awareness  
✅ **Resource allocator** maintains 20% fleet reserve for emergency response  
✅ **45-90 second latency** from satellite alert to UAV airborne  

---

## Navigation

- **Previous:** [Threat Logic](./THREAT_LOGIC.md)
- **Next:** [Flight Path Algorithms](./FLIGHT_PATH_ALGORITHMS.md)
- **Home:** [Documentation Index](./README.md)

---

**Document Status:** ✅ Complete  
**Last Updated:** November 9, 2025  
**Review Cycle:** Quarterly
