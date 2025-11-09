# Roadmap to Scale
## Coordinated Satellite & UAV Event-Analysis MVP

**Document Version:** 1.0  
**Date:** November 9, 2025  
**Parent Document:** [Deployment Blueprint](./DEPLOYMENT_BLUEPRINT.md)

---

## 11. Roadmap to Scale

### 11.1 Phase 1: MVP Prototype (Current → 6 months)

Initial deployment in single test region to validate concept and refine operations.

#### Objectives
- Validate detection accuracy in real-world conditions
- Establish operational procedures
- Collect training data for model improvement
- Demonstrate value to stakeholders

#### Deployment Specifications

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: MVP PROTOTYPE                                                  │
│                                                                          │
│ COVERAGE AREA                                                            │
│  Region:             100 km² test area                                   │
│  Terrain:            Mixed (urban periphery + rural)                     │
│  Population:         ~5,000 - 10,000                                     │
│  Risk Level:         Medium threat assessment                            │
│                                                                          │
│ FLEET CONFIGURATION                                                      │
│  UAVs:               5 units                                             │
│  Flight Time:        40 min per mission                                  │
│  Coverage Rate:      ~25 km²/day (5 UAVs × 2 missions/day × 2.5 km²)   │
│  Revisit Time:       4 days for full area                               │
│                                                                          │
│ INFRASTRUCTURE                                                           │
│  Ground Stations:    1 command center                                    │
│  Edge Relays:        2 relay stations                                    │
│  Operators:          2 pilots + 1 technician                             │
│  Command Center:     On-premises (small facility)                        │
│                                                                          │
│ SATELLITE INTEGRATION                                                    │
│  Sources:            Sentinel-2 (ESA, free)                              │
│  Resolution:         10m multispectral                                   │
│  Revisit:            5 days                                              │
│  Cost:               $0 (open data)                                      │
│                                                                          │
│ PERFORMANCE TARGETS                                                      │
│  Detection Accuracy: ≥ 90% (TPR)                                         │
│  False Positive:     ≤ 10%                                               │
│  Response Time:      < 120 seconds                                       │
│  Uptime:             > 95%                                               │
│                                                                          │
│ BUDGET                                                                   │
│  CAPEX:              $120,000 (5 UAVs + infrastructure)                  │
│  OPEX (6 months):    $60,000 (personnel + operations)                    │
│  Total:              $180,000                                            │
│                                                                          │
│ SUCCESS CRITERIA                                                         │
│  ✓ 90% detection accuracy achieved                                      │
│  ✓ 100+ verified threat detections                                      │
│  ✓ < 5% false alarm rate                                                │
│  ✓ Operational procedures documented                                    │
│  ✓ Stakeholder buy-in secured                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Key Milestones

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

@dataclass
class Milestone:
    """Project milestone definition."""
    id: str
    name: str
    description: str
    target_date: datetime
    dependencies: List[str]
    deliverables: List[str]
    status: str = 'pending'  # pending, in_progress, completed, delayed

class Phase1Roadmap:
    """
    Phase 1 project roadmap and milestone tracker.
    """
    
    def __init__(self, start_date: datetime):
        self.start_date = start_date
        self.milestones = self._define_milestones()
    
    def _define_milestones(self) -> List[Milestone]:
        """Define Phase 1 milestones."""
        start = self.start_date
        
        return [
            Milestone(
                id='M1.1',
                name='Equipment Acquisition',
                description='Purchase and receive all UAVs and ground equipment',
                target_date=start + timedelta(weeks=4),
                dependencies=[],
                deliverables=[
                    '5 UAVs with compute modules',
                    'Ground station server',
                    '2 edge relay stations',
                    'All sensors and radios'
                ]
            ),
            Milestone(
                id='M1.2',
                name='Software Deployment',
                description='Deploy EVENT software stack and integrate hardware',
                target_date=start + timedelta(weeks=6),
                dependencies=['M1.1'],
                deliverables=[
                    'Docker containers running',
                    'Database initialized',
                    'UAV firmware configured',
                    'Detection models loaded',
                    'End-to-end test passed'
                ]
            ),
            Milestone(
                id='M1.3',
                name='Operator Training',
                description='Train pilots and technicians on EVENT system',
                target_date=start + timedelta(weeks=7),
                dependencies=['M1.2'],
                deliverables=[
                    '2 certified pilots',
                    '1 certified technician',
                    'Training manual completed',
                    'SOPs documented'
                ]
            ),
            Milestone(
                id='M1.4',
                name='Field Deployment',
                description='Deploy system to test region and begin operations',
                target_date=start + timedelta(weeks=8),
                dependencies=['M1.3'],
                deliverables=[
                    'Site setup completed',
                    'All systems operational',
                    'First mission flown',
                    'Dashboard accessible'
                ]
            ),
            Milestone(
                id='M1.5',
                name='Initial Operations (30 days)',
                description='Run continuous operations for 30 days',
                target_date=start + timedelta(weeks=12),
                dependencies=['M1.4'],
                deliverables=[
                    '200+ flight hours',
                    '50+ detections logged',
                    'Performance metrics collected',
                    'Operational issues documented'
                ]
            ),
            Milestone(
                id='M1.6',
                name='Model Refinement',
                description='Retrain models with production data',
                target_date=start + timedelta(weeks=14),
                dependencies=['M1.5'],
                deliverables=[
                    'Updated detection model',
                    'Improved accuracy metrics',
                    'False positive reduction',
                    'Model deployed to UAVs'
                ]
            ),
            Milestone(
                id='M1.7',
                name='Extended Operations (60 days)',
                description='Continue operations with refined system',
                target_date=start + timedelta(weeks=22),
                dependencies=['M1.6'],
                deliverables=[
                    '400+ flight hours',
                    '150+ detections logged',
                    'Stakeholder reports',
                    'Scale-up plan drafted'
                ]
            ),
            Milestone(
                id='M1.8',
                name='Phase 1 Review',
                description='Comprehensive review and Phase 2 planning',
                target_date=start + timedelta(weeks=24),
                dependencies=['M1.7'],
                deliverables=[
                    'Performance report',
                    'Lessons learned document',
                    'Phase 2 budget proposal',
                    'Go/No-Go decision'
                ]
            )
        ]
    
    def get_critical_path(self) -> List[Milestone]:
        """Identify critical path milestones."""
        return [m for m in self.milestones if m.id.startswith('M1.')]
    
    def check_schedule_health(self) -> dict:
        """Assess schedule health."""
        now = datetime.now()
        
        total = len(self.milestones)
        completed = sum(1 for m in self.milestones if m.status == 'completed')
        delayed = sum(1 for m in self.milestones if m.status == 'delayed')
        on_track = sum(1 for m in self.milestones 
                      if m.status in ['pending', 'in_progress'] 
                      and m.target_date > now)
        
        return {
            'total_milestones': total,
            'completed': completed,
            'delayed': delayed,
            'on_track': on_track,
            'completion_rate': (completed / total) * 100,
            'health': 'green' if delayed == 0 else 'yellow' if delayed < 2 else 'red'
        }
```

---

### 11.2 Phase 2: Regional Network (6-18 months)

Expand to multi-site deployment covering regional network.

#### Objectives
- Scale to 5-10 deployment sites
- Cover 1,000-2,000 km²
- Establish central coordination
- Integrate commercial satellite data
- Prove operational sustainability

#### Deployment Specifications

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: REGIONAL NETWORK                                               │
│                                                                          │
│ COVERAGE AREA                                                            │
│  Region:             1,500 km² (multi-site)                              │
│  Sites:              7 deployment locations                              │
│  Terrain:            Diverse (urban, rural, border regions)              │
│  Population:         ~100,000 coverage                                   │
│                                                                          │
│ FLEET CONFIGURATION                                                      │
│  UAVs:               35 units (5 per site)                               │
│  Swarm Size:         5-10 UAVs per mission                               │
│  Coverage Rate:      ~175 km²/day                                        │
│  Revisit Time:       8-10 days for full area                             │
│                                                                          │
│ INFRASTRUCTURE                                                           │
│  Ground Stations:    7 field command centers                             │
│  Central Hub:        1 regional coordination center                      │
│  Edge Relays:        14 relay stations (2 per site)                      │
│  Operators:          21 personnel (3 per site) + 5 central staff         │
│                                                                          │
│ SATELLITE INTEGRATION                                                    │
│  Sources:            - Sentinel-2 (10m, free)                            │
│                      - Planet SkySat (3m, commercial)                    │
│                      - Maxar WorldView (0.5m, on-demand)                 │
│  Cost:               $50,000/year satellite data licenses                │
│                                                                          │
│ NETWORK ARCHITECTURE                                                     │
│  Topology:           Star network (sites → regional hub)                 │
│  Connectivity:       - Primary: Dedicated fiber/microwave               │
│                      - Backup: LTE/5G                                    │
│  Latency:            < 50ms site-to-hub                                  │
│  Bandwidth:          100 Mbps per site                                   │
│                                                                          │
│ ADVANCED FEATURES                                                        │
│  ✓ Multi-site coordination (cross-site UAV handoff)                     │
│  ✓ Centralized mission planning                                         │
│  ✓ Shared threat intelligence                                           │
│  ✓ Load balancing across sites                                          │
│  ✓ Automated model updates (OTA)                                        │
│  ✓ 99.5% uptime SLA                                                     │
│                                                                          │
│ PERFORMANCE TARGETS                                                      │
│  Detection Accuracy: ≥ 95% (TPR)                                         │
│  False Positive:     ≤ 5%                                                │
│  Response Time:      < 90 seconds                                        │
│  Uptime:             > 99%                                               │
│  Multi-site Handoff: < 30 seconds                                        │
│                                                                          │
│ BUDGET                                                                   │
│  CAPEX:              $800,000 (35 UAVs + infrastructure)                 │
│  OPEX (12 months):   $520,000 (personnel + operations + satellite)       │
│  Total:              $1,320,000                                          │
│                                                                          │
│ SUCCESS CRITERIA                                                         │
│  ✓ 95% detection accuracy maintained                                    │
│  ✓ 1,000+ verified detections across network                            │
│  ✓ Multi-site coordination operational                                  │
│  ✓ 99% uptime achieved                                                  │
│  ✓ ROI positive (threat prevention value > costs)                       │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Regional Coordination System

```python
from typing import List, Dict, Optional
import numpy as np
from geopy.distance import geodesic

@dataclass
class DeploymentSite:
    """Deployment site specification."""
    site_id: str
    name: str
    location: Tuple[float, float]  # (lat, lon)
    coverage_area: float  # km²
    uav_count: int
    status: str  # operational, maintenance, offline
    current_missions: int

class RegionalCoordinator:
    """
    Coordinate multiple deployment sites in regional network.
    """
    
    def __init__(self):
        self.sites: Dict[str, DeploymentSite] = {}
        self.active_missions: Dict[str, dict] = {}
    
    def register_site(self, site: DeploymentSite):
        """Register new deployment site."""
        self.sites[site.site_id] = site
        print(f"Site {site.name} registered at {site.location}")
    
    def find_nearest_site(self, location: Tuple[float, float]) -> Optional[DeploymentSite]:
        """
        Find nearest operational site to given location.
        """
        if not self.sites:
            return None
        
        operational_sites = [s for s in self.sites.values() if s.status == 'operational']
        if not operational_sites:
            return None
        
        distances = [
            (site, geodesic(location, site.location).km)
            for site in operational_sites
        ]
        
        nearest_site, distance = min(distances, key=lambda x: x[1])
        return nearest_site
    
    def assign_mission_to_site(self, mission: dict) -> Optional[str]:
        """
        Assign mission to best available site.
        
        Selection criteria:
        1. Distance to target
        2. Available UAV capacity
        3. Current workload
        """
        target_location = mission['location']
        
        # Score each site
        site_scores = []
        for site in self.sites.values():
            if site.status != 'operational':
                continue
            
            if site.current_missions >= site.uav_count:
                continue  # Site at capacity
            
            # Distance factor (closer is better)
            distance = geodesic(target_location, site.location).km
            distance_score = 1 / (1 + distance)  # Normalize
            
            # Capacity factor (more available UAVs is better)
            capacity = site.uav_count - site.current_missions
            capacity_score = capacity / site.uav_count
            
            # Workload factor (less busy is better)
            workload_score = 1 - (site.current_missions / site.uav_count)
            
            # Combined score
            total_score = (
                distance_score * 0.5 +
                capacity_score * 0.3 +
                workload_score * 0.2
            )
            
            site_scores.append((site, total_score))
        
        if not site_scores:
            return None
        
        # Select best site
        best_site, _ = max(site_scores, key=lambda x: x[1])
        
        # Assign mission
        mission_id = mission['mission_id']
        self.active_missions[mission_id] = {
            'site_id': best_site.site_id,
            'mission': mission,
            'assigned_at': datetime.now()
        }
        
        best_site.current_missions += 1
        
        return best_site.site_id
    
    def coordinate_cross_site_handoff(self, uav_id: str, 
                                     from_site_id: str, 
                                     to_site_id: str) -> bool:
        """
        Coordinate UAV handoff between sites (for continuous pursuit).
        """
        from_site = self.sites.get(from_site_id)
        to_site = self.sites.get(to_site_id)
        
        if not from_site or not to_site:
            return False
        
        if to_site.status != 'operational':
            return False
        
        # Check if sites are within handoff range (50 km)
        distance = geodesic(from_site.location, to_site.location).km
        if distance > 50:
            return False  # Too far for handoff
        
        # Execute handoff
        # 1. From site releases UAV
        from_site.current_missions -= 1
        
        # 2. To site accepts UAV
        to_site.current_missions += 1
        
        # 3. Update UAV's assigned site
        print(f"Handoff: UAV {uav_id} from {from_site.name} to {to_site.name}")
        
        return True
    
    def get_network_status(self) -> Dict:
        """Get overall network status."""
        total_uavs = sum(site.uav_count for site in self.sites.values())
        operational_sites = sum(1 for site in self.sites.values() 
                               if site.status == 'operational')
        active_missions = len(self.active_missions)
        
        total_coverage = sum(site.coverage_area for site in self.sites.values())
        
        return {
            'total_sites': len(self.sites),
            'operational_sites': operational_sites,
            'total_uavs': total_uavs,
            'active_missions': active_missions,
            'total_coverage_km2': total_coverage,
            'network_health': 'healthy' if operational_sites == len(self.sites) else 'degraded'
        }
    
    def optimize_coverage_allocation(self) -> List[Dict]:
        """
        Optimize UAV allocation across sites based on threat density.
        """
        recommendations = []
        
        for site in self.sites.values():
            # Calculate utilization
            utilization = site.current_missions / site.uav_count if site.uav_count > 0 else 0
            
            if utilization > 0.9:
                # Site over-utilized
                recommendations.append({
                    'site_id': site.site_id,
                    'action': 'increase_capacity',
                    'reason': f'High utilization: {utilization:.1%}',
                    'suggested_uavs': int(site.uav_count * 0.2)  # Add 20%
                })
            elif utilization < 0.3 and site.uav_count > 3:
                # Site under-utilized
                recommendations.append({
                    'site_id': site.site_id,
                    'action': 'reduce_capacity',
                    'reason': f'Low utilization: {utilization:.1%}',
                    'suggested_uavs': -int(site.uav_count * 0.2)  # Reduce 20%
                })
        
        return recommendations
```

---

### 11.3 Phase 3: National Grid (18-36 months)

Scale to nationwide coverage with standardized operations.

#### Objectives
- Deploy 50+ sites across country
- Achieve national coverage
- Integrate with national security infrastructure
- Support 200+ UAV fleet
- Enable predictive analytics

#### Deployment Specifications

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: NATIONAL GRID                                                  │
│                                                                          │
│ COVERAGE AREA                                                            │
│  Region:             Nationwide (50,000+ km²)                            │
│  Sites:              50-75 deployment locations                          │
│  Hubs:               5 regional hubs + 1 national center                 │
│  Coverage:           High-risk areas + borders + critical infrastructure │
│                                                                          │
│ FLEET CONFIGURATION                                                      │
│  UAVs:               250 units (3-7 per site based on risk)              │
│  Swarm Size:         10-20 UAVs per coordinated mission                  │
│  Coverage Rate:      ~1,250 km²/day (continuous operations)              │
│  Revisit Time:       Daily for high-priority zones                       │
│                      Weekly for standard coverage                        │
│                                                                          │
│ INFRASTRUCTURE                                                           │
│  Field Stations:     50-75 automated stations (minimal staff)            │
│  Regional Hubs:      5 hubs (10-15 staff each)                           │
│  National Center:    1 command center (25 staff)                         │
│  Data Centers:       3 redundant cloud regions                           │
│                                                                          │
│ SATELLITE INTEGRATION                                                    │
│  Sources:            - Multiple commercial constellations                │
│                      - Government satellites (classified)                │
│                      - Dedicated tasking capability                      │
│  Resolution:         0.3m - 10m (multi-tier)                             │
│  Revisit:            Sub-daily for critical areas                        │
│  Cost:               $500,000/year satellite services                    │
│                                                                          │
│ NETWORK ARCHITECTURE                                                     │
│  Topology:           Hierarchical (stations → hubs → national)           │
│  Connectivity:       - Primary: Dedicated fiber network                  │
│                      - Backup: Satellite internet (Starlink)             │
│  Latency:            < 20ms station-to-national                          │
│  Bandwidth:          1 Gbps national backbone                            │
│  Redundancy:         N+2 (dual redundancy)                               │
│                                                                          │
│ ADVANCED CAPABILITIES                                                    │
│  ✓ Automated threat detection & classification                          │
│  ✓ Predictive analytics (ML-based threat forecasting)                   │
│  ✓ Real-time intelligence sharing with agencies                         │
│  ✓ Automated emergency response integration                             │
│  ✓ Multi-UAV swarm coordination (20+ units)                             │
│  ✓ 99.9% uptime SLA                                                     │
│  ✓ Edge AI inference (sub-second detection)                             │
│  ✓ Blockchain audit trail                                               │
│                                                                          │
│ PERFORMANCE TARGETS                                                      │
│  Detection Accuracy: ≥ 98% (TPR)                                         │
│  False Positive:     ≤ 2%                                                │
│  Response Time:      < 60 seconds                                        │
│  Uptime:             > 99.9%                                             │
│  Threat Prevention:  80% reduction in incidents                          │
│                                                                          │
│ BUDGET (Per Year)                                                        │
│  CAPEX:              $5M (hardware refresh, new sites)                   │
│  OPEX:               $8M (personnel, operations, satellite, cloud)       │
│  Total Annual:       $13M                                                │
│  Cost per km²/year:  $260                                                │
│                                                                          │
│ SUCCESS CRITERIA                                                         │
│  ✓ National coverage operational                                        │
│  ✓ 98% detection accuracy sustained                                     │
│  ✓ 10,000+ verified detections/year                                     │
│  ✓ Measurable crime/incident reduction                                  │
│  ✓ Integration with law enforcement complete                            │
│  ✓ Congressional/stakeholder approval for permanent funding             │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Predictive Analytics Engine

```python
import torch
import torch.nn as nn
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from datetime import datetime, timedelta

class ThreatPredictionModel(nn.Module):
    """
    LSTM-based threat prediction model.
    
    Predicts likelihood of illegal activity in specific areas
    based on historical patterns.
    """
    
    def __init__(self, input_size=50, hidden_size=128, num_layers=2):
        super().__init__()
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )
        
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        """
        Args:
            x: (batch, sequence_length, input_size)
        
        Returns:
            Threat probability (batch, 1)
        """
        lstm_out, _ = self.lstm(x)
        last_output = lstm_out[:, -1, :]
        prediction = self.fc(last_output)
        return prediction

class PredictiveAnalyticsEngine:
    """
    Predictive analytics for threat forecasting.
    """
    
    def __init__(self):
        self.threat_model = ThreatPredictionModel()
        self.pattern_classifier = RandomForestClassifier(n_estimators=100)
        
        # Load pretrained models
        # self.threat_model.load_state_dict(torch.load('threat_prediction.pth'))
        
        self.feature_history = []
    
    def extract_features(self, location: Tuple[float, float], 
                        historical_data: pd.DataFrame) -> np.ndarray:
        """
        Extract features for threat prediction.
        
        Features:
        - Historical detection count (7/30/90 days)
        - Day of week patterns
        - Time of day patterns
        - Weather conditions
        - Proximity to borders/roads
        - Population density
        - Recent trend (increasing/decreasing)
        """
        lat, lon = location
        
        # Filter data for this location (within 1km)
        local_data = historical_data[
            (historical_data['lat'].between(lat - 0.01, lat + 0.01)) &
            (historical_data['lon'].between(lon - 0.01, lon + 0.01))
        ]
        
        now = datetime.now()
        
        features = []
        
        # 1. Historical detection counts
        for days in [7, 30, 90]:
            cutoff = now - timedelta(days=days)
            count = len(local_data[local_data['timestamp'] > cutoff])
            features.append(count)
        
        # 2. Day of week pattern (one-hot encoded)
        day_of_week = now.weekday()
        day_onehot = [1 if i == day_of_week else 0 for i in range(7)]
        features.extend(day_onehot)
        
        # 3. Hour of day pattern (sine/cosine encoding)
        hour = now.hour
        features.append(np.sin(2 * np.pi * hour / 24))
        features.append(np.cos(2 * np.pi * hour / 24))
        
        # 4. Recent trend (slope of last 7 days)
        if len(local_data) > 0:
            recent = local_data.tail(7).groupby('date').size()
            if len(recent) > 1:
                slope = np.polyfit(range(len(recent)), recent.values, 1)[0]
                features.append(slope)
            else:
                features.append(0)
        else:
            features.append(0)
        
        # 5. Spatial features (distance to borders, roads, etc.)
        # Placeholder - would integrate with GIS data
        features.extend([0, 0, 0])
        
        # Pad to fixed size (50 features)
        while len(features) < 50:
            features.append(0)
        
        return np.array(features[:50])
    
    def predict_threat_probability(self, location: Tuple[float, float],
                                   historical_data: pd.DataFrame) -> float:
        """
        Predict probability of threat at location in next 24 hours.
        """
        # Extract features
        features = self.extract_features(location, historical_data)
        
        # Prepare for LSTM (needs sequence)
        # Use last 7 days of features
        feature_sequence = np.tile(features, (7, 1))  # Simplified
        
        # Convert to tensor
        x = torch.FloatTensor(feature_sequence).unsqueeze(0)  # (1, 7, 50)
        
        # Predict
        self.threat_model.eval()
        with torch.no_grad():
            probability = self.threat_model(x).item()
        
        return probability
    
    def generate_patrol_priorities(self, grid_cells: List[dict],
                                   historical_data: pd.DataFrame) -> List[dict]:
        """
        Generate priority rankings for patrol areas.
        """
        priorities = []
        
        for cell in grid_cells:
            location = (cell['center_lat'], cell['center_lon'])
            
            # Predict threat probability
            threat_prob = self.predict_threat_probability(location, historical_data)
            
            # Calculate priority score
            # Factors: threat probability, time since last visit, coverage gap
            time_since_visit = cell.get('hours_since_last_visit', 48)
            coverage_gap = min(time_since_visit / 24, 1.0)  # Normalize to [0, 1]
            
            priority_score = (
                threat_prob * 0.6 +
                coverage_gap * 0.4
            )
            
            priorities.append({
                'cell_id': cell['id'],
                'location': location,
                'threat_probability': threat_prob,
                'coverage_gap': coverage_gap,
                'priority_score': priority_score,
                'recommended_action': 'high_priority' if priority_score > 0.7 else 'standard'
            })
        
        # Sort by priority
        priorities.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return priorities
    
    def optimize_national_coverage(self, sites: List[DeploymentSite],
                                   threat_predictions: List[dict]) -> Dict:
        """
        Optimize UAV allocation across national grid based on predicted threats.
        """
        # Aggregate threat predictions by site
        site_threats = {}
        for site in sites:
            nearby_threats = [
                p for p in threat_predictions
                if geodesic(p['location'], site.location).km < 20
            ]
            
            avg_threat = np.mean([t['threat_probability'] for t in nearby_threats]) if nearby_threats else 0
            site_threats[site.site_id] = avg_threat
        
        # Calculate ideal UAV allocation
        total_threat = sum(site_threats.values())
        total_uavs = sum(site.uav_count for site in sites)
        
        allocations = {}
        for site in sites:
            threat_ratio = site_threats[site.site_id] / total_threat if total_threat > 0 else 1/len(sites)
            ideal_uavs = int(total_uavs * threat_ratio)
            
            # Ensure minimum 2 UAVs per site
            ideal_uavs = max(ideal_uavs, 2)
            
            allocations[site.site_id] = {
                'current_uavs': site.uav_count,
                'ideal_uavs': ideal_uavs,
                'adjustment': ideal_uavs - site.uav_count,
                'threat_level': site_threats[site.site_id]
            }
        
        return allocations
```

---

### 11.4 Swarm Intelligence Upgrades

Evolution from individual UAV operations to coordinated swarm behavior.

#### Swarm Capability Progression

```
┌─────────────────────────────────────────────────────────────────────────┐
│ SWARM EVOLUTION TIMELINE                                                │
│                                                                          │
│ CURRENT (Phase 1): Individual UAV Operations                            │
│  ├─ Manual mission assignment                                           │
│  ├─ No inter-UAV communication                                          │
│  ├─ Sequential coverage                                                 │
│  └─ Human-in-loop for all decisions                                     │
│                                                                          │
│ PHASE 2 (+6 months): Basic Swarm Coordination                           │
│  ├─ Mesh networking between UAVs                                        │
│  ├─ Shared situational awareness                                        │
│  ├─ Collision avoidance (automatic deconfliction)                       │
│  ├─ Load balancing (distribute coverage)                                │
│  └─ 2-5 UAV swarms                                                      │
│                                                                          │
│ PHASE 3 (+18 months): Intelligent Swarm Behavior                        │
│  ├─ Emergent behavior (flocking, swarming)                              │
│  ├─ Distributed decision making                                         │
│  ├─ Multi-objective optimization                                        │
│  ├─ Target tracking with multiple UAVs                                  │
│  ├─ Adaptive formation control                                          │
│  └─ 10-20 UAV swarms                                                    │
│                                                                          │
│ FUTURE (Phase 4+): Autonomous Swarm Intelligence                        │
│  ├─ Self-organizing swarms (no central control)                         │
│  ├─ Reinforcement learning for tactics                                  │
│  ├─ Adversarial robustness (anti-jamming, evasion)                      │
│  ├─ Cross-site swarm coordination                                       │
│  ├─ 50+ UAV mega-swarms                                                 │
│  └─ Autonomous mission planning                                         │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Swarm Coordination Algorithm

```python
import numpy as np
from scipy.spatial.distance import cdist
from typing import List, Tuple

@dataclass
class UAVState:
    """UAV state vector."""
    uav_id: str
    position: np.ndarray  # (x, y, z)
    velocity: np.ndarray  # (vx, vy, vz)
    heading: float
    battery: float
    assigned_target: Optional[Tuple[float, float]]
    
class SwarmController:
    """
    Coordinate swarm of UAVs using distributed behavior rules.
    
    Based on Reynolds' Boids algorithm with additional rules:
    - Separation: Avoid crowding neighbors
    - Alignment: Steer towards average heading
    - Cohesion: Steer towards average position
    - Target seeking: Move towards assigned targets
    - Obstacle avoidance: Avoid no-fly zones
    """
    
    def __init__(self, num_uavs: int):
        self.num_uavs = num_uavs
        self.uav_states: Dict[str, UAVState] = {}
        
        # Swarm parameters
        self.separation_distance = 50  # meters
        self.cohesion_distance = 200   # meters
        self.alignment_distance = 150  # meters
        
        # Behavior weights
        self.w_separation = 1.5
        self.w_alignment = 1.0
        self.w_cohesion = 1.0
        self.w_target = 2.0
        self.w_obstacle = 3.0
        
        self.max_speed = 15  # m/s
        self.max_acceleration = 2  # m/s²
    
    def update_uav_state(self, state: UAVState):
        """Update state for UAV."""
        self.uav_states[state.uav_id] = state
    
    def compute_swarm_behavior(self, uav_id: str) -> np.ndarray:
        """
        Compute desired velocity for UAV based on swarm rules.
        
        Returns:
            Desired velocity vector (3D)
        """
        if uav_id not in self.uav_states:
            return np.zeros(3)
        
        ego_state = self.uav_states[uav_id]
        
        # Get neighbors
        neighbors = [s for uid, s in self.uav_states.items() if uid != uav_id]
        
        if not neighbors:
            # No neighbors - just go to target
            return self._target_seeking(ego_state)
        
        # Calculate behavior components
        v_separation = self._separation(ego_state, neighbors)
        v_alignment = self._alignment(ego_state, neighbors)
        v_cohesion = self._cohesion(ego_state, neighbors)
        v_target = self._target_seeking(ego_state)
        
        # Combine behaviors
        desired_velocity = (
            v_separation * self.w_separation +
            v_alignment * self.w_alignment +
            v_cohesion * self.w_cohesion +
            v_target * self.w_target
        )
        
        # Normalize and limit speed
        speed = np.linalg.norm(desired_velocity)
        if speed > self.max_speed:
            desired_velocity = (desired_velocity / speed) * self.max_speed
        
        return desired_velocity
    
    def _separation(self, ego: UAVState, neighbors: List[UAVState]) -> np.ndarray:
        """
        Steer away from nearby UAVs to avoid crowding.
        """
        steer = np.zeros(3)
        
        for neighbor in neighbors:
            distance = np.linalg.norm(ego.position - neighbor.position)
            
            if distance < self.separation_distance and distance > 0:
                # Repulsion force (inverse square law)
                diff = ego.position - neighbor.position
                diff = diff / (distance ** 2)  # Normalize and weight by distance
                steer += diff
        
        return steer
    
    def _alignment(self, ego: UAVState, neighbors: List[UAVState]) -> np.ndarray:
        """
        Steer towards average heading of nearby UAVs.
        """
        avg_velocity = np.zeros(3)
        count = 0
        
        for neighbor in neighbors:
            distance = np.linalg.norm(ego.position - neighbor.position)
            
            if distance < self.alignment_distance:
                avg_velocity += neighbor.velocity
                count += 1
        
        if count > 0:
            avg_velocity /= count
            
            # Steer towards average velocity
            steer = avg_velocity - ego.velocity
            return steer
        
        return np.zeros(3)
    
    def _cohesion(self, ego: UAVState, neighbors: List[UAVState]) -> np.ndarray:
        """
        Steer towards average position of nearby UAVs.
        """
        avg_position = np.zeros(3)
        count = 0
        
        for neighbor in neighbors:
            distance = np.linalg.norm(ego.position - neighbor.position)
            
            if distance < self.cohesion_distance:
                avg_position += neighbor.position
                count += 1
        
        if count > 0:
            avg_position /= count
            
            # Steer towards center of mass
            steer = avg_position - ego.position
            return steer
        
        return np.zeros(3)
    
    def _target_seeking(self, ego: UAVState) -> np.ndarray:
        """
        Steer towards assigned target.
        """
        if ego.assigned_target is None:
            return np.zeros(3)
        
        # Convert 2D target to 3D (maintain altitude)
        target_3d = np.array([ego.assigned_target[0], ego.assigned_target[1], ego.position[2]])
        
        # Steer towards target
        steer = target_3d - ego.position
        
        # Normalize
        distance = np.linalg.norm(steer)
        if distance > 0:
            steer = steer / distance
        
        return steer * self.max_speed
    
    def assign_targets_to_swarm(self, targets: List[Tuple[float, float]]) -> Dict[str, Tuple[float, float]]:
        """
        Optimally assign targets to UAVs in swarm.
        
        Uses Hungarian algorithm for optimal assignment.
        """
        from scipy.optimize import linear_sum_assignment
        
        if not targets or not self.uav_states:
            return {}
        
        # Build cost matrix (distances)
        uav_ids = list(self.uav_states.keys())
        uav_positions = np.array([self.uav_states[uid].position[:2] for uid in uav_ids])
        target_positions = np.array(targets)
        
        cost_matrix = cdist(uav_positions, target_positions)
        
        # Solve assignment problem
        uav_indices, target_indices = linear_sum_assignment(cost_matrix)
        
        # Create assignments
        assignments = {}
        for uav_idx, target_idx in zip(uav_indices, target_indices):
            uav_id = uav_ids[uav_idx]
            target = targets[target_idx]
            assignments[uav_id] = target
            
            # Update UAV state
            self.uav_states[uav_id].assigned_target = target
        
        return assignments
    
    def get_swarm_formation(self, formation_type: str, 
                           center: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Generate formation positions for swarm.
        
        Formations: line, wedge, circle, grid
        """
        uav_ids = list(self.uav_states.keys())
        n = len(uav_ids)
        
        positions = {}
        
        if formation_type == 'line':
            # Linear formation
            spacing = 50
            for i, uav_id in enumerate(uav_ids):
                offset = (i - n/2) * spacing
                positions[uav_id] = center + np.array([offset, 0, 0])
        
        elif formation_type == 'wedge':
            # V-formation
            spacing = 50
            for i, uav_id in enumerate(uav_ids):
                row = int(np.sqrt(i))
                col = i - row**2
                positions[uav_id] = center + np.array([row * spacing, col * spacing - row * spacing/2, 0])
        
        elif formation_type == 'circle':
            # Circular formation
            radius = 100
            for i, uav_id in enumerate(uav_ids):
                angle = 2 * np.pi * i / n
                positions[uav_id] = center + np.array([radius * np.cos(angle), radius * np.sin(angle), 0])
        
        elif formation_type == 'grid':
            # Grid formation
            cols = int(np.ceil(np.sqrt(n)))
            rows = int(np.ceil(n / cols))
            spacing = 50
            
            for i, uav_id in enumerate(uav_ids):
                row = i // cols
                col = i % cols
                positions[uav_id] = center + np.array([row * spacing, col * spacing, 0])
        
        return positions
```

---

## Key Takeaways

✅ **3-phase roadmap**: MVP (100 km²) → Regional (1,500 km²) → National (50,000+ km²)  
✅ **Fleet scaling**: 5 UAVs → 35 UAVs → 250+ UAVs over 36 months  
✅ **Budget progression**: $180K (Phase 1) → $1.3M (Phase 2) → $13M/year (Phase 3)  
✅ **Regional coordination**: Multi-site handoffs, centralized planning, shared intelligence  
✅ **Predictive analytics**: LSTM-based threat forecasting, patrol optimization, dynamic allocation  
✅ **Swarm evolution**: Individual ops → Basic coordination → Intelligent swarms → Autonomous mega-swarms  
✅ **Performance targets**: 90% → 95% → 98% detection accuracy across phases  
✅ **National impact**: 80% incident reduction target, integration with law enforcement  

---

## Navigation

- **Previous:** [Deployment Blueprint](./DEPLOYMENT_BLUEPRINT.md)
- **Next:** [Algorithm Specifications (Appendix A)](./APPENDIX_A_ALGORITHMS.md)
- **Home:** [Documentation Index](./README.md)

---

**Document Status:** ✅ Complete  
**Last Updated:** November 9, 2025  
**Review Cycle:** Quarterly
