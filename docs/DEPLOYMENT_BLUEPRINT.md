# Deployment Blueprint
## Coordinated Satellite & UAV Event-Analysis MVP

**Document Version:** 1.0  
**Date:** November 9, 2025  
**Parent Document:** [Evaluation & Metrics](./EVALUATION_METRICS.md)

---

## 10. Deployment Blueprint

### 10.1 Hardware Bill of Materials (BOM)

Complete hardware specifications for production deployment.

#### UAV Platform Specifications

```
┌─────────────────────────────────────────────────────────────────────────┐
│ UAV HARDWARE CONFIGURATION                                              │
│                                                                          │
│ AIRFRAME                                                                │
│  Model:              DJI Matrice 300 RTK (or equivalent)               │
│  Wingspan:           ~810mm diagonal                                    │
│  Weight (Empty):     6.3 kg                                             │
│  Max Takeoff Weight: 9.0 kg                                             │
│  Flight Time:        55 minutes (no payload) / 40 min (full payload)   │
│  Max Speed:          23 m/s (82 km/h)                                   │
│  Wind Resistance:    15 m/s                                             │
│  Operating Temp:     -20°C to 50°C                                      │
│  IP Rating:          IP45 (weather resistant)                           │
│  Unit Cost:          $13,000 - $15,000                                  │
│                                                                          │
│ COMPUTE MODULE                                                           │
│  Model:              NVIDIA Jetson Xavier NX Developer Kit              │
│  GPU:                384-core NVIDIA Volta™ (48 Tensor Cores)           │
│  CPU:                6-core NVIDIA Carmel ARM®v8.2 64-bit               │
│  Memory:             8 GB 128-bit LPDDR4x @ 51.2GB/s                    │
│  Storage:            128 GB NVMe SSD                                     │
│  Power:              10W - 20W (configurable)                            │
│  AI Performance:     21 TOPS (INT8)                                      │
│  Dimensions:         103mm x 90.5mm x 31mm                               │
│  Weight:             ~250g (with heatsink)                               │
│  Unit Cost:          $399 (dev kit) / $199 (module)                     │
│                                                                          │
│ SENSOR SUITE                                                             │
│  Primary Camera:     Sony IMX477 12MP (RGB)                              │
│    - Resolution:     4056 x 3040 pixels                                  │
│    - Sensor Size:    7.9mm diagonal                                      │
│    - Lens:           6mm fixed focal length                              │
│    - FOV:            ~62.2° diagonal                                     │
│    - Unit Cost:      $50                                                 │
│                                                                          │
│  Thermal Camera:     FLIR Lepton 3.5 (optional)                          │
│    - Resolution:     160 x 120 pixels                                    │
│    - Spectral Range: 8-14 μm                                             │
│    - Frame Rate:     8.6 Hz                                              │
│    - FOV:            57° × 71°                                           │
│    - Unit Cost:      $200 - $250                                         │
│                                                                          │
│  Radar (optional):   Ainstein K-79 mmWave                                │
│    - Frequency:      76-81 GHz                                           │
│    - Range:          Up to 150m                                          │
│    - Unit Cost:      $500                                                │
│                                                                          │
│ COMMUNICATION                                                            │
│  Radio Module:       RFD900x Long Range Telemetry                        │
│    - Frequency:      902-928 MHz (ISM band)                              │
│    - Output Power:   1W (30 dBm)                                         │
│    - Range:          40+ km (line of sight)                              │
│    - Data Rate:      Up to 250 kbps                                      │
│    - Unit Cost:      $300 (pair)                                         │
│                                                                          │
│  Mesh Radio:         Doodle Labs Smart Radio 2.4 GHz                     │
│    - Frequency:      2.4 - 2.5 GHz                                       │
│    - Output Power:   30 dBm (1W)                                         │
│    - Range:          2-5 km (UAV-to-UAV)                                 │
│    - Mesh Protocol:  OLSR/AODV compatible                                │
│    - Unit Cost:      $800                                                │
│                                                                          │
│ POWER SYSTEM                                                             │
│  Battery:            TB60 Intelligent Flight Battery                     │
│    - Capacity:       5935 mAh                                            │
│    - Voltage:        52.8V                                               │
│    - Energy:         274 Wh                                              │
│    - Weight:         1.35 kg                                             │
│    - Charge Time:    60 minutes (fast charger)                           │
│    - Unit Cost:      $600 (per battery)                                  │
│                                                                          │
│  Compute Power:      12V DC-DC converter (vehicle power → Jetson)       │
│    - Input:          52.8V (UAV battery)                                 │
│    - Output:         12V @ 3A                                            │
│    - Efficiency:     >90%                                                │
│    - Unit Cost:      $50                                                 │
│                                                                          │
│ PER-UAV TOTAL COST: ~$17,000 - $19,500 (depending on sensors)           │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Ground Infrastructure

```
┌─────────────────────────────────────────────────────────────────────────┐
│ GROUND CONTROL STATION (GCS)                                            │
│                                                                          │
│ COMPUTE SERVER                                                           │
│  Model:              Dell PowerEdge R750 (or equivalent)                │
│  CPU:                2x Intel Xeon Gold 6338 (32 cores, 64 threads)     │
│  RAM:                256 GB DDR4 ECC                                     │
│  Storage:            - 2x 1TB NVMe SSD (RAID 1, OS)                     │
│                      - 4x 8TB SAS HDD (RAID 10, data)                   │
│  GPU:                2x NVIDIA RTX A5000 (24GB each)                     │
│  Network:            4x 10GbE ports                                      │
│  Power Supply:       2x 1400W redundant PSU                              │
│  Unit Cost:          $15,000 - $18,000                                   │
│                                                                          │
│ EDGE RELAY SYSTEM                                                        │
│  Compute:            Intel NUC 11 Extreme Kit                            │
│    - CPU:            Intel Core i7-11700B (8 cores)                      │
│    - RAM:            32 GB DDR4                                          │
│    - Storage:        1 TB NVMe SSD                                       │
│    - Unit Cost:      $1,200                                              │
│                                                                          │
│  Radio:              RFD900x Base Station                                │
│    - High-gain antenna (12 dBi)                                          │
│    - Antenna mast (10m telescopic)                                       │
│    - Unit Cost:      $500 (radio + antenna + mast)                      │
│                                                                          │
│ OPERATOR WORKSTATION                                                     │
│  Desktop:            High-performance workstation                        │
│    - CPU:            Intel i7-13700K (16 cores)                          │
│    - RAM:            64 GB DDR5                                          │
│    - GPU:            NVIDIA RTX 4070 (12GB)                              │
│    - Storage:        2TB NVMe SSD                                        │
│    - Display:        2x 32" 4K monitors                                  │
│    - Unit Cost:      $3,500                                              │
│                                                                          │
│ NETWORKING                                                               │
│  Router:             Enterprise-grade VPN router                         │
│  Switch:             48-port managed Gigabit switch                      │
│  Firewall:           Hardware firewall appliance                         │
│  Total Cost:         $2,000                                              │
│                                                                          │
│ GROUND INFRASTRUCTURE TOTAL: ~$22,000 - $25,000                          │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Fleet Configuration & Pricing

```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class HardwareComponent:
    """Hardware component specification."""
    name: str
    model: str
    quantity: int
    unit_cost: float
    lifespan_years: float
    maintenance_cost_annual: float

class FleetBOMCalculator:
    """
    Calculate Bill of Materials for UAV fleet deployment.
    """
    
    def __init__(self, num_uavs: int = 10):
        self.num_uavs = num_uavs
        
        # UAV components
        self.uav_components = [
            HardwareComponent("Airframe", "DJI Matrice 300 RTK", 1, 14000, 5, 1400),
            HardwareComponent("Compute", "NVIDIA Jetson Xavier NX", 1, 399, 3, 40),
            HardwareComponent("Primary Camera", "Sony IMX477 12MP", 1, 50, 3, 5),
            HardwareComponent("Thermal Camera", "FLIR Lepton 3.5", 1, 225, 5, 20),
            HardwareComponent("Telemetry Radio", "RFD900x", 1, 300, 5, 30),
            HardwareComponent("Mesh Radio", "Doodle Labs Smart Radio", 1, 800, 5, 80),
            HardwareComponent("Battery", "TB60 Flight Battery", 3, 600, 2, 180),  # 3 per UAV
            HardwareComponent("DC-DC Converter", "52V to 12V", 1, 50, 5, 5),
        ]
        
        # Ground infrastructure (one-time)
        self.ground_components = [
            HardwareComponent("Command Server", "Dell PowerEdge R750", 1, 16500, 5, 1650),
            HardwareComponent("Edge Relay", "Intel NUC 11 Extreme", 2, 1200, 5, 120),
            HardwareComponent("Relay Radio", "RFD900x Base", 2, 500, 5, 50),
            HardwareComponent("Operator Workstation", "Workstation + Displays", 2, 3500, 5, 350),
            HardwareComponent("Network Equipment", "Router/Switch/Firewall", 1, 2000, 5, 200),
        ]
        
        # Software licenses
        self.software_costs = {
            'gis_platform': 5000,  # Annual GIS software license
            'cloud_services': 12000,  # Annual cloud infrastructure
            'ssl_certificates': 500,  # Annual SSL/TLS certs
            'monitoring_tools': 2000,  # Annual monitoring/logging
        }
        
        # Operational costs
        self.operational_costs = {
            'personnel_annual': 150000,  # 2 operators + 1 technician
            'training_annual': 10000,
            'insurance_annual': 8000,
            'facility_annual': 24000,  # Hangar/office space
        }
    
    def calculate_capex(self) -> Dict[str, float]:
        """
        Calculate Capital Expenditure (one-time costs).
        """
        # UAV fleet
        uav_cost_per_unit = sum(c.unit_cost * c.quantity for c in self.uav_components)
        total_uav_cost = uav_cost_per_unit * self.num_uavs
        
        # Ground infrastructure
        ground_cost = sum(c.unit_cost * c.quantity for c in self.ground_components)
        
        # Installation & setup
        installation_cost = 15000  # Network setup, mounting, configuration
        
        # Initial training
        initial_training = 25000  # First-time operator training
        
        # Contingency (15%)
        subtotal = total_uav_cost + ground_cost + installation_cost + initial_training
        contingency = subtotal * 0.15
        
        return {
            'uav_fleet': total_uav_cost,
            'ground_infrastructure': ground_cost,
            'installation_setup': installation_cost,
            'initial_training': initial_training,
            'contingency': contingency,
            'total_capex': subtotal + contingency
        }
    
    def calculate_opex_annual(self) -> Dict[str, float]:
        """
        Calculate annual Operating Expenditure.
        """
        # Hardware maintenance
        uav_maintenance = sum(
            c.maintenance_cost_annual * c.quantity * self.num_uavs 
            for c in self.uav_components
        )
        
        ground_maintenance = sum(
            c.maintenance_cost_annual * c.quantity 
            for c in self.ground_components
        )
        
        total_maintenance = uav_maintenance + ground_maintenance
        
        # Software licenses
        total_software = sum(self.software_costs.values())
        
        # Operational costs
        total_operational = sum(self.operational_costs.values())
        
        # Consumables (batteries, propellers, etc.)
        consumables = 5000 * self.num_uavs  # $5k per UAV per year
        
        return {
            'hardware_maintenance': total_maintenance,
            'software_licenses': total_software,
            'operational': total_operational,
            'consumables': consumables,
            'total_opex_annual': total_maintenance + total_software + total_operational + consumables
        }
    
    def calculate_tco_5year(self) -> Dict[str, float]:
        """
        Calculate 5-year Total Cost of Ownership.
        """
        capex = self.calculate_capex()
        opex_annual = self.calculate_opex_annual()
        
        opex_5year = opex_annual['total_opex_annual'] * 5
        
        # Hardware refresh (replace batteries year 2, compute year 3)
        refresh_cost = (600 * 3 * self.num_uavs) + (399 * self.num_uavs)  # Batteries + Jetson
        
        tco = capex['total_capex'] + opex_5year + refresh_cost
        
        return {
            'capex': capex['total_capex'],
            'opex_5year': opex_5year,
            'hardware_refresh': refresh_cost,
            'tco_5year': tco,
            'cost_per_uav_5year': tco / self.num_uavs,
            'monthly_cost_averaged': tco / 60  # 5 years = 60 months
        }
    
    def generate_bom_report(self) -> str:
        """Generate comprehensive BOM report."""
        capex = self.calculate_capex()
        opex = self.calculate_opex_annual()
        tco = self.calculate_tco_5year()
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║               HARDWARE BILL OF MATERIALS (BOM)                       ║
║                  {self.num_uavs}-UAV Fleet Deployment                          ║
╚══════════════════════════════════════════════════════════════════════╝

CAPITAL EXPENDITURE (CAPEX)
──────────────────────────────────────────────────────────────────────
  UAV Fleet ({self.num_uavs} units):        ${capex['uav_fleet']:>12,.2f}
  Ground Infrastructure:     ${capex['ground_infrastructure']:>12,.2f}
  Installation & Setup:      ${capex['installation_setup']:>12,.2f}
  Initial Training:          ${capex['initial_training']:>12,.2f}
  Contingency (15%):         ${capex['contingency']:>12,.2f}
  ────────────────────────────────────────────────────
  TOTAL CAPEX:               ${capex['total_capex']:>12,.2f}

OPERATING EXPENDITURE (OPEX) - ANNUAL
──────────────────────────────────────────────────────────────────────
  Hardware Maintenance:      ${opex['hardware_maintenance']:>12,.2f}
  Software Licenses:         ${opex['software_licenses']:>12,.2f}
  Operational Costs:         ${opex['operational']:>12,.2f}
  Consumables:               ${opex['consumables']:>12,.2f}
  ────────────────────────────────────────────────────
  TOTAL ANNUAL OPEX:         ${opex['total_opex_annual']:>12,.2f}

5-YEAR TOTAL COST OF OWNERSHIP (TCO)
──────────────────────────────────────────────────────────────────────
  Initial CAPEX:             ${tco['capex']:>12,.2f}
  5-Year OPEX:               ${tco['opex_5year']:>12,.2f}
  Hardware Refresh:          ${tco['hardware_refresh']:>12,.2f}
  ────────────────────────────────────────────────────
  5-YEAR TCO:                ${tco['tco_5year']:>12,.2f}
  
  Cost per UAV (5-year):     ${tco['cost_per_uav_5year']:>12,.2f}
  Monthly Cost (averaged):   ${tco['monthly_cost_averaged']:>12,.2f}

PER-UAV COMPONENT BREAKDOWN
──────────────────────────────────────────────────────────────────────
"""
        
        for component in self.uav_components:
            cost = component.unit_cost * component.quantity
            report += f"  {component.name:<25s} ${cost:>8,.2f}\n"
        
        uav_total = sum(c.unit_cost * c.quantity for c in self.uav_components)
        report += f"  {'─' * 25} {'─' * 9}\n"
        report += f"  {'TOTAL PER UAV':<25s} ${uav_total:>8,.2f}\n"
        
        return report
```

---

### 10.2 Cloud & On-Premises Architecture

Hybrid deployment architecture combining cloud services and edge infrastructure.

#### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│ HYBRID CLOUD + ON-PREMISES ARCHITECTURE                                │
│                                                                          │
│  CLOUD TIER (AWS/Azure/GCP)                                             │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │  │
│  │  │  Satellite   │  │   Training   │  │   Archive    │            │  │
│  │  │  Imagery API │  │   Pipeline   │  │   Storage    │            │  │
│  │  │              │  │              │  │              │            │  │
│  │  │  - Sentinel  │  │  - PyTorch   │  │  - S3/Blob   │            │  │
│  │  │  - Landsat   │  │  - Model     │  │  - 100TB+    │            │  │
│  │  │  - Planet    │  │    Registry  │  │  - Glacier   │            │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │  │
│  │         │                  │                  │                    │  │
│  │         └──────────────────┼──────────────────┘                    │  │
│  │                            │                                        │  │
│  │  ┌─────────────────────────▼──────────────────────────┐            │  │
│  │  │         API Gateway + Load Balancer                │            │  │
│  │  │         - HTTPS/TLS termination                    │            │  │
│  │  │         - Rate limiting                            │            │  │
│  │  │         - Authentication (OAuth 2.0)               │            │  │
│  │  └────────────────────────────────────────────────────┘            │  │
│  │                            │                                        │  │
│  └────────────────────────────┼────────────────────────────────────────┘  │
│                               │                                           │
│                    ═══ VPN / Direct Connect ═══                           │
│                               │                                           │
│  ON-PREMISES COMMAND CENTER                                               │
│  ┌────────────────────────────▼────────────────────────────────────────┐ │
│  │                                                                      │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │ │
│  │  │   FastAPI      │  │   PostgreSQL   │  │     Redis      │        │ │
│  │  │   Backend      │  │   + PostGIS    │  │     Cache      │        │ │
│  │  │                │  │                │  │                │        │ │
│  │  │  - REST API    │  │  - Detections  │  │  - Sessions    │        │ │
│  │  │  - WebSocket   │  │  - Telemetry   │  │  - Rate limit  │        │ │
│  │  │  - MQTT        │  │  - Missions    │  │  - Pub/Sub     │        │ │
│  │  └────────────────┘  └────────────────┘  └────────────────┘        │ │
│  │         │                    │                    │                 │ │
│  │         └────────────────────┼────────────────────┘                 │ │
│  │                              │                                      │ │
│  │  ┌───────────────────────────▼──────────────────────────┐           │ │
│  │  │              Message Broker (MQTT)                   │           │ │
│  │  │              - Eclipse Mosquitto                     │           │ │
│  │  │              - TLS encryption                        │           │ │
│  │  └──────────────────────────────────────────────────────┘           │ │
│  │         │                              │                            │ │
│  │         │                              │                            │ │
│  │  ┌──────▼────────┐            ┌────────▼────────┐                   │ │
│  │  │   Celery      │            │   Dashboard     │                   │ │
│  │  │   Scheduler   │            │   (React)       │                   │ │
│  │  │               │            │                 │                   │ │
│  │  │ - Mission     │            │ - Leaflet Map   │                   │ │
│  │  │   planning    │            │ - Telemetry     │                   │ │
│  │  │ - Task queue  │            │ - Alerts        │                   │ │
│  │  └───────────────┘            └─────────────────┘                   │ │
│  │                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                               │                                           │
│                    ═══ RF Link (RFD900x) ═══                              │
│                               │                                           │
│  EDGE RELAY (Field Deployment)                                            │
│  ┌────────────────────────────▼────────────────────────────────────────┐ │
│  │                                                                      │ │
│  │  ┌────────────────┐                                                  │ │
│  │  │   Edge Relay   │  Intel NUC + RFD900x Base                        │ │
│  │  │   Controller   │                                                  │ │
│  │  │                │  - Command routing                               │ │
│  │  │  - Store &     │  - UAV telemetry aggregation                     │ │
│  │  │    forward     │  - Offline buffering                             │ │
│  │  │  - Compression │  - Data compression                              │ │
│  │  └────────────────┘                                                  │ │
│  │         │                                                            │ │
│  └─────────┼────────────────────────────────────────────────────────────┘ │
│            │                                                              │
│    ═══ RF Mesh (900 MHz / 2.4 GHz) ═══                                   │
│            │                                                              │
│  UAV SWARM                                                                │
│  ┌─────────▼─────────────────────────────────────────────────────────┐  │
│  │                                                                     │  │
│  │  ╔═══════════╗  ╔═══════════╗  ╔═══════════╗  ╔═══════════╗       │  │
│  │  ║   UAV-1   ║  ║   UAV-2   ║  ║   UAV-3   ║  ║  UAV-N    ║       │  │
│  │  ║           ║──║           ║──║           ║──║           ║       │  │
│  │  ║  Jetson   ║  ║  Jetson   ║  ║  Jetson   ║  ║  Jetson   ║       │  │
│  │  ║  Xavier   ║  ║  Xavier   ║  ║  Xavier   ║  ║  Xavier   ║       │  │
│  │  ║  NX       ║  ║  NX       ║  ║  NX       ║  ║  NX       ║       │  │
│  │  ║           ║  ║           ║  ║           ║  ║           ║       │  │
│  │  ║ YOLOv8    ║  ║ YOLOv8    ║  ║ YOLOv8    ║  ║ YOLOv8    ║       │  │
│  │  ║ Inference ║  ║ Inference ║  ║ Inference ║  ║ Inference ║       │  │
│  │  ╚═══════════╝  ╚═══════════╝  ╚═══════════╝  ╚═══════════╝       │  │
│  │                                                                     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Infrastructure as Code (IaC)

```python
# terraform/main.tf (Terraform configuration for cloud resources)
"""
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC for EVENT system
resource "aws_vpc" "event_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "EVENT-VPC"
    Project = "EVENT"
  }
}

# Public subnet for API Gateway
resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.event_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"

  tags = {
    Name = "EVENT-Public-Subnet"
  }
}

# S3 bucket for satellite imagery archive
resource "aws_s3_bucket" "satellite_archive" {
  bucket = "event-satellite-archive-${var.deployment_id}"

  tags = {
    Name = "EVENT-Satellite-Archive"
    Project = "EVENT"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "archive_lifecycle" {
  bucket = aws_s3_bucket.satellite_archive.id

  rule {
    id     = "archive-old-imagery"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 730  # Delete after 2 years
    }
  }
}

# S3 bucket for model artifacts
resource "aws_s3_bucket" "model_registry" {
  bucket = "event-model-registry-${var.deployment_id}"
  
  versioning {
    enabled = true
  }

  tags = {
    Name = "EVENT-Model-Registry"
    Project = "EVENT"
  }
}

# EC2 instance for training pipeline (GPU instance)
resource "aws_instance" "training_server" {
  ami           = var.gpu_ami_id  # Deep Learning AMI
  instance_type = "g4dn.xlarge"   # NVIDIA T4 GPU
  subnet_id     = aws_subnet.public_subnet.id

  root_block_device {
    volume_size = 500  # GB
    volume_type = "gp3"
  }

  tags = {
    Name = "EVENT-Training-Server"
    Project = "EVENT"
  }

  user_data = <<-EOF
              #!/bin/bash
              # Install training pipeline
              git clone https://github.com/event/training-pipeline
              cd training-pipeline
              pip install -r requirements.txt
              EOF
}

# VPN Gateway for secure command center connection
resource "aws_vpn_gateway" "event_vpn" {
  vpc_id = aws_vpc.event_vpc.id

  tags = {
    Name = "EVENT-VPN-Gateway"
  }
}

# Customer Gateway (on-premises command center)
resource "aws_customer_gateway" "command_center" {
  bgp_asn    = 65000
  ip_address = var.command_center_public_ip
  type       = "ipsec.1"

  tags = {
    Name = "EVENT-Command-Center"
  }
}

# Site-to-Site VPN Connection
resource "aws_vpn_connection" "command_to_cloud" {
  vpn_gateway_id      = aws_vpn_gateway.event_vpn.id
  customer_gateway_id = aws_customer_gateway.command_center.id
  type                = "ipsec.1"
  static_routes_only  = true

  tags = {
    Name = "EVENT-VPN-Connection"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "event_logs" {
  name              = "/aws/event/system"
  retention_in_days = 30

  tags = {
    Name = "EVENT-Logs"
  }
}

# IAM Role for EC2 instances
resource "aws_iam_role" "event_ec2_role" {
  name = "EVENT-EC2-Role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# Attach S3 access policy
resource "aws_iam_role_policy_attachment" "s3_access" {
  role       = aws_iam_role.event_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}
"""

# docker-compose.prod.yml (Production deployment)
```yaml
version: '3.8'

services:
  # PostgreSQL with PostGIS
  postgres:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: event_db
      POSTGRES_USER: event_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infra/init_postgis.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U event_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis cache
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD} --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: always
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # MQTT Broker
  mosquitto:
    image: eclipse-mosquitto:2
    volumes:
      - ./infra/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - mosquitto_data:/mosquitto/data
      - mosquitto_logs:/mosquitto/log
    ports:
      - "1883:1883"
      - "8883:8883"
    restart: always

  # MinIO object storage
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  # FastAPI backend
  api:
    build:
      context: ./services/api
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://event_user:${POSTGRES_PASSWORD}@postgres:5432/event_db
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      MQTT_BROKER: mosquitto
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: ${MINIO_ROOT_USER}
      MINIO_SECRET_KEY: ${MINIO_ROOT_PASSWORD}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - mosquitto
      - minio
    restart: always
    deploy:
      replicas: 2  # Load balanced
      resources:
        limits:
          cpus: '2'
          memory: 4G

  # Celery scheduler
  scheduler:
    build:
      context: ./services/scheduler
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://event_user:${POSTGRES_PASSWORD}@postgres:5432/event_db
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      MQTT_BROKER: mosquitto
    depends_on:
      - postgres
      - redis
      - mosquitto
    restart: always
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G

  # React dashboard
  dashboard:
    build:
      context: ./services/dashboard
      dockerfile: Dockerfile
    environment:
      REACT_APP_API_URL: http://localhost:8000
      REACT_APP_WS_URL: ws://localhost:8000
    ports:
      - "3000:80"
    depends_on:
      - api
    restart: always

  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    volumes:
      - ./infra/nginx.conf:/etc/nginx/nginx.conf
      - ./infra/ssl:/etc/nginx/ssl
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api
      - dashboard
    restart: always

volumes:
  postgres_data:
  redis_data:
  mosquitto_data:
  mosquitto_logs:
  minio_data:

networks:
  default:
    name: event_network
```

---

### 10.3 Training Data Pipeline & Model Updates

Continuous model improvement through automated training pipeline.

#### Training Pipeline Architecture

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from ultralytics import YOLO
import albumentations as A
from pathlib import Path
from typing import List, Dict, Tuple
import boto3
import mlflow

class TrainingPipeline:
    """
    Automated training pipeline for detection models.
    """
    
    def __init__(self, config: dict):
        self.config = config
        
        # MLflow tracking
        mlflow.set_tracking_uri(config['mlflow_uri'])
        mlflow.set_experiment(config['experiment_name'])
        
        # S3 client for data/model storage
        self.s3_client = boto3.client('s3',
            aws_access_key_id=config['aws_access_key'],
            aws_secret_access_key=config['aws_secret_key']
        )
        
        self.bucket_name = config['s3_bucket']
        
        # Model registry
        self.model_registry = config['model_registry_path']
    
    def collect_training_data(self) -> Path:
        """
        Collect and prepare training data from production detections.
        
        Strategy:
        1. Query PostgreSQL for high-confidence detections
        2. Query for corrected false positives/negatives
        3. Download associated images from MinIO
        4. Create annotation files in YOLO format
        """
        from sqlalchemy import create_engine
        import pandas as pd
        
        engine = create_engine(self.config['database_url'])
        
        # Fetch verified detections (human-reviewed)
        query = """
        SELECT 
            d.detection_id,
            d.image_path,
            d.bbox_x, d.bbox_y, d.bbox_w, d.bbox_h,
            d.class_name,
            d.confidence,
            d.verified_label,
            d.is_correct
        FROM detections d
        WHERE d.verified_label IS NOT NULL
        AND d.created_at > NOW() - INTERVAL '30 days'
        ORDER BY d.created_at DESC
        """
        
        df = pd.read_sql(query, engine)
        
        print(f"Collected {len(df)} verified detections for training")
        
        # Download images and create annotations
        dataset_path = Path('/tmp/training_data')
        dataset_path.mkdir(exist_ok=True)
        
        images_path = dataset_path / 'images'
        labels_path = dataset_path / 'labels'
        images_path.mkdir(exist_ok=True)
        labels_path.mkdir(exist_ok=True)
        
        for idx, row in df.iterrows():
            # Download image from MinIO
            image_file = images_path / f"{row['detection_id']}.jpg"
            # self.minio_client.download_file(row['image_path'], image_file)
            
            # Create YOLO annotation
            label_file = labels_path / f"{row['detection_id']}.txt"
            
            # Convert bbox to YOLO format (normalized x_center, y_center, width, height)
            # Assuming bbox is in pixel coordinates
            class_id = self._get_class_id(row['verified_label'])
            
            with open(label_file, 'w') as f:
                f.write(f"{class_id} {row['bbox_x']} {row['bbox_y']} {row['bbox_w']} {row['bbox_h']}\n")
        
        return dataset_path
    
    def _get_class_id(self, class_name: str) -> int:
        """Map class name to ID."""
        class_mapping = {
            'person': 0,
            'vehicle': 1,
            'animal': 2
        }
        return class_mapping.get(class_name, 0)
    
    def prepare_augmentation_pipeline(self) -> A.Compose:
        """
        Create augmentation pipeline for training robustness.
        """
        transform = A.Compose([
            A.RandomRotate90(p=0.5),
            A.Flip(p=0.5),
            A.OneOf([
                A.MotionBlur(blur_limit=5, p=0.3),
                A.MedianBlur(blur_limit=5, p=0.3),
                A.GaussianBlur(blur_limit=5, p=0.3),
            ], p=0.5),
            A.OneOf([
                A.OpticalDistortion(p=0.3),
                A.GridDistortion(p=0.3),
            ], p=0.3),
            A.OneOf([
                A.HueSaturationValue(p=0.3),
                A.RGBShift(p=0.3),
                A.RandomBrightnessContrast(p=0.3),
            ], p=0.5),
            A.CLAHE(p=0.3),
            A.RandomGamma(p=0.3),
            A.Cutout(num_holes=8, max_h_size=32, max_w_size=32, p=0.3),
        ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))
        
        return transform
    
    def train_model(self, dataset_path: Path) -> Tuple[str, Dict]:
        """
        Train YOLOv8 model on collected data.
        """
        with mlflow.start_run():
            # Log parameters
            mlflow.log_params({
                'model_type': 'yolov8n',
                'epochs': self.config['epochs'],
                'batch_size': self.config['batch_size'],
                'image_size': self.config['image_size'],
                'learning_rate': self.config['learning_rate']
            })
            
            # Initialize model
            model = YOLO('yolov8n.pt')  # Start from pretrained
            
            # Create data.yaml
            data_yaml = dataset_path / 'data.yaml'
            with open(data_yaml, 'w') as f:
                f.write(f"""
train: {dataset_path / 'images/train'}
val: {dataset_path / 'images/val'}
nc: 3
names: ['person', 'vehicle', 'animal']
""")
            
            # Train
            results = model.train(
                data=str(data_yaml),
                epochs=self.config['epochs'],
                imgsz=self.config['image_size'],
                batch=self.config['batch_size'],
                lr0=self.config['learning_rate'],
                device='0',  # GPU
                workers=8,
                project=str(dataset_path / 'runs'),
                name='yolov8_training',
                exist_ok=True,
                
                # Augmentation
                hsv_h=0.015,
                hsv_s=0.7,
                hsv_v=0.4,
                degrees=0.0,
                translate=0.1,
                scale=0.5,
                shear=0.0,
                perspective=0.0,
                flipud=0.0,
                fliplr=0.5,
                mosaic=1.0,
                mixup=0.0,
            )
            
            # Log metrics
            mlflow.log_metrics({
                'mAP50': results.results_dict['metrics/mAP50(B)'],
                'mAP50-95': results.results_dict['metrics/mAP50-95(B)'],
                'precision': results.results_dict['metrics/precision(B)'],
                'recall': results.results_dict['metrics/recall(B)'],
            })
            
            # Export to ONNX for production
            model_path = model.export(format='onnx', imgsz=self.config['image_size'])
            
            # Log model artifact
            mlflow.log_artifact(model_path)
            
            # Version and upload to S3
            model_version = self._create_model_version()
            s3_key = f"models/yolov8n_v{model_version}.onnx"
            
            self.s3_client.upload_file(
                model_path,
                self.bucket_name,
                s3_key
            )
            
            print(f"Model uploaded to s3://{self.bucket_name}/{s3_key}")
            
            return model_version, results.results_dict
    
    def _create_model_version(self) -> str:
        """Generate semantic version for model."""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def validate_model(self, model_path: Path, test_dataset_path: Path) -> Dict:
        """
        Validate model performance on held-out test set.
        """
        model = YOLO(model_path)
        
        results = model.val(
            data=str(test_dataset_path / 'data.yaml'),
            split='test',
            imgsz=self.config['image_size'],
            batch=self.config['batch_size'],
            device='0'
        )
        
        metrics = {
            'test_mAP50': results.results_dict['metrics/mAP50(B)'],
            'test_mAP50-95': results.results_dict['metrics/mAP50-95(B)'],
            'test_precision': results.results_dict['metrics/precision(B)'],
            'test_recall': results.results_dict['metrics/recall(B)'],
        }
        
        # Check if model meets production criteria
        meets_criteria = (
            metrics['test_mAP50'] >= 0.90 and
            metrics['test_precision'] >= 0.85 and
            metrics['test_recall'] >= 0.90
        )
        
        metrics['production_ready'] = meets_criteria
        
        return metrics
    
    def deploy_model(self, model_version: str):
        """
        Deploy model to production (update model registry).
        """
        # Update model registry
        registry_entry = {
            'version': model_version,
            'uploaded_at': str(datetime.now()),
            's3_path': f"s3://{self.bucket_name}/models/yolov8n_v{model_version}.onnx",
            'status': 'production'
        }
        
        # Update registry YAML
        import yaml
        
        registry_path = Path(self.model_registry)
        if registry_path.exists():
            with open(registry_path) as f:
                registry = yaml.safe_load(f)
        else:
            registry = {'models': []}
        
        registry['models'].append(registry_entry)
        registry['active_version'] = model_version
        
        with open(registry_path, 'w') as f:
            yaml.dump(registry, f)
        
        print(f"Model v{model_version} deployed to production")
        
        # Notify UAVs to update (via MQTT)
        import paho.mqtt.publish as publish
        
        publish.single(
            'uav/model_update',
            payload=f"v{model_version}",
            hostname=self.config['mqtt_broker']
        )
```

---

### 10.4 Field Deployment SOP

Standard Operating Procedure for deploying EVENT system in field operations.

#### Deployment Checklist

```markdown
# EVENT FIELD DEPLOYMENT CHECKLIST

## PRE-DEPLOYMENT (2 weeks before)

### Personnel
- [ ] Identify 2 certified UAV pilots
- [ ] Identify 1 technical operator (system admin)
- [ ] Complete EVENT system training (3 days)
- [ ] Obtain necessary flight permissions/waivers
- [ ] Conduct medical fitness checks

### Equipment Inspection
- [ ] Test all UAV airframes (flight test minimum 10 minutes each)
- [ ] Verify Jetson Xavier NX modules (run benchmark test)
- [ ] Check camera sensors (capture test images, verify quality)
- [ ] Test radio systems (range test minimum 5km)
- [ ] Verify battery health (capacity test, expect >80% original)
- [ ] Inspect propellers and landing gear
- [ ] Test ground station server (stress test with dummy data)
- [ ] Verify network equipment (bandwidth test)

### Software Configuration
- [ ] Update all UAV firmware to latest stable version
- [ ] Deploy latest EVENT software stack (docker-compose pull)
- [ ] Load production detection models (verify MD5 checksums)
- [ ] Configure geofences for area of operation
- [ ] Set up operator accounts and access controls
- [ ] Test end-to-end system (detection → alert → dispatch)
- [ ] Backup all configuration files

### Logistics
- [ ] Secure deployment site (fenced compound, shelter)
- [ ] Arrange power supply (grid + backup generator)
- [ ] Set up internet connectivity (Starlink/LTE backup)
- [ ] Prepare spare parts inventory (propellers, batteries, radios)
- [ ] Arrange accommodation for personnel
- [ ] Coordinate with local authorities

## DEPLOYMENT DAY

### Site Setup (4-6 hours)
1. **Power Infrastructure**
   - [ ] Connect to grid power
   - [ ] Test backup generator
   - [ ] Set up UPS for critical systems
   - [ ] Install surge protection

2. **Network Setup**
   - [ ] Mount high-gain antennas (10m mast)
   - [ ] Configure routers and switches
   - [ ] Establish VPN to cloud
   - [ ] Test internet bandwidth (minimum 10 Mbps up/down)

3. **Ground Station**
   - [ ] Rack-mount server and network equipment
   - [ ] Connect displays and workstations
   - [ ] Power on systems and verify boot
   - [ ] Start Docker containers
   - [ ] Check all service health (postgres, redis, mqtt, api)

4. **Edge Relay**
   - [ ] Position relay station (elevated location if possible)
   - [ ] Connect high-gain antenna
   - [ ] Power on and verify connectivity to ground station
   - [ ] Test command routing latency (expect <100ms)

### UAV Preparation (2 hours)
- [ ] Charge all batteries to 100%
- [ ] Install batteries and verify voltage
- [ ] Power on Jetson modules
- [ ] Verify GPS lock (minimum 10 satellites)
- [ ] Check compass calibration
- [ ] Test camera feeds (verify image quality)
- [ ] Verify model inference (run test detection)
- [ ] Test radio link (RSSI > -80 dBm)
- [ ] Conduct control surface checks

### System Integration Test (2 hours)
1. **Communication Test**
   - [ ] Send command to each UAV
   - [ ] Verify telemetry reception
   - [ ] Test mesh network formation
   - [ ] Check offline buffering

2. **Mission Test**
   - [ ] Create test mission in dashboard
   - [ ] Assign to UAV
   - [ ] Verify mission download
   - [ ] Execute short test flight (5 minutes)
   - [ ] Verify real-time tracking on map

3. **Detection Test**
   - [ ] Fly over test targets (people, vehicles)
   - [ ] Verify detections appear in dashboard
   - [ ] Check confidence scores
   - [ ] Test alert generation

### Go/No-Go Decision
**System is READY if:**
- [ ] All UAVs pass pre-flight checks
- [ ] Ground station showing all green status
- [ ] Communication links stable
- [ ] Test detection successful
- [ ] Weather within operating limits (wind <12 m/s, no precipitation)

**Abort criteria:**
- Any UAV showing errors
- Ground station services failing
- Communication link unstable (RSSI < -90 dBm)
- Weather outside limits

## OPERATIONS

### Flight Operations (Daily)
**Pre-Flight (each mission):**
- [ ] Weather check (wind, visibility, precipitation)
- [ ] Battery check (>90% recommended for full mission)
- [ ] GPS lock verification
- [ ] Camera test
- [ ] Communication check
- [ ] Airspace clearance

**In-Flight Monitoring:**
- [ ] Monitor telemetry (altitude, speed, battery)
- [ ] Watch for alerts
- [ ] Track mission progress
- [ ] Maintain visual line of sight (VLOS) or observer
- [ ] Log any anomalies

**Post-Flight:**
- [ ] Download flight logs
- [ ] Check for errors or warnings
- [ ] Battery capacity check
- [ ] Propeller inspection
- [ ] Wipe camera lens
- [ ] Charge batteries

### Maintenance Schedule
**Daily:**
- Propeller inspection
- Battery health check
- Radio antenna inspection
- Clean camera lens

**Weekly:**
- Motor bearing check
- Firmware update check
- Ground station disk space check
- Backup database

**Monthly:**
- Full UAV inspection (landing gear, frame)
- Replace worn propellers
- Jetson module health check
- Network equipment firmware update
- Model performance review

## POST-DEPLOYMENT

### Data Collection
- [ ] Download all detection records
- [ ] Export telemetry logs
- [ ] Backup database
- [ ] Generate performance report

### Equipment Recovery
- [ ] Power down all systems
- [ ] Disconnect and stow antennas
- [ ] Pack UAVs in cases
- [ ] Inventory all equipment
- [ ] Check for damage

### Lessons Learned
- [ ] Conduct debrief with team
- [ ] Document issues encountered
- [ ] Recommend improvements
- [ ] Update SOP as needed
```

#### Deployment Script

```bash
#!/bin/bash
# deploy.sh - Automated field deployment script

set -e  # Exit on error

echo "========================================"
echo "   EVENT Field Deployment Script"
echo "========================================"

# Configuration
DEPLOYMENT_ENV=${1:-production}
CONFIG_FILE="./config/${DEPLOYMENT_ENV}.env"

# Load environment variables
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
    echo "✓ Loaded configuration from $CONFIG_FILE"
else
    echo "✗ Configuration file not found: $CONFIG_FILE"
    exit 1
fi

# Pre-deployment checks
echo ""
echo "Running pre-deployment checks..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "✗ Docker not installed"
    exit 1
fi
echo "✓ Docker installed: $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "✗ Docker Compose not installed"
    exit 1
fi
echo "✓ Docker Compose installed: $(docker-compose --version)"

# Check disk space (need at least 50GB)
DISK_AVAIL=$(df -BG / | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$DISK_AVAIL" -lt 50 ]; then
    echo "✗ Insufficient disk space: ${DISK_AVAIL}GB (need 50GB)"
    exit 1
fi
echo "✓ Disk space available: ${DISK_AVAIL}GB"

# Check internet connectivity
if ! ping -c 1 8.8.8.8 &> /dev/null; then
    echo "⚠ No internet connectivity (offline deployment)"
else
    echo "✓ Internet connectivity OK"
fi

# Pull latest images
echo ""
echo "Pulling Docker images..."
docker-compose -f docker-compose.prod.yml pull

# Initialize database
echo ""
echo "Initializing database..."
docker-compose -f docker-compose.prod.yml up -d postgres
sleep 10  # Wait for PostgreSQL to start

# Run database migrations
docker-compose -f docker-compose.prod.yml run --rm api alembic upgrade head

# Seed reference data
echo ""
echo "Seeding reference data..."
docker-compose -f docker-compose.prod.yml run --rm scheduler python /app/seed_tiles.py

# Start all services
echo ""
echo "Starting all services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to be healthy..."
sleep 30

# Health check
echo ""
echo "Running health checks..."

SERVICES=("postgres" "redis" "mosquitto" "minio" "api" "scheduler" "dashboard")
ALL_HEALTHY=true

for service in "${SERVICES[@]}"; do
    if docker-compose -f docker-compose.prod.yml ps | grep "$service" | grep -q "Up"; then
        echo "✓ $service is running"
    else
        echo "✗ $service is not running"
        ALL_HEALTHY=false
    fi
done

# API health check
API_HEALTH=$(curl -s http://localhost:8000/health || echo "failed")
if [ "$API_HEALTH" = "failed" ]; then
    echo "✗ API health check failed"
    ALL_HEALTHY=false
else
    echo "✓ API health check passed"
fi

# Final status
echo ""
echo "========================================"
if [ "$ALL_HEALTHY" = true ]; then
    echo "   ✓ DEPLOYMENT SUCCESSFUL"
    echo "========================================"
    echo ""
    echo "Dashboard: http://localhost:3000"
    echo "API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "Next steps:"
    echo "1. Access dashboard and log in"
    echo "2. Configure geofences"
    echo "3. Register UAVs"
    echo "4. Create first mission"
else
    echo "   ✗ DEPLOYMENT FAILED"
    echo "========================================"
    echo ""
    echo "Check logs with: docker-compose -f docker-compose.prod.yml logs"
    exit 1
fi
```

---

## Key Takeaways

✅ **Per-UAV cost**: $17,000-$19,500 (airframe + Jetson Xavier NX + sensors + radios)  
✅ **Ground infrastructure**: $22,000-$25,000 (server + edge relay + workstations + networking)  
✅ **10-UAV fleet TCO**: ~$500,000 over 5 years (CAPEX + OPEX + maintenance)  
✅ **Hybrid architecture**: Cloud (training, archive) + On-premises (command, real-time ops)  
✅ **Training pipeline**: Automated data collection from production, MLflow tracking, S3 model registry  
✅ **Continuous improvement**: Weekly model updates from verified detections  
✅ **Field deployment**: 8-12 hour setup, pre-flight checklists, daily maintenance, 30-day rotation  
✅ **Infrastructure as Code**: Terraform for cloud resources, Docker Compose for services  

---

## Navigation

- **Previous:** [Evaluation & Metrics](./EVALUATION_METRICS.md)
- **Next:** [Roadmap to Scale](./ROADMAP_TO_SCALE.md)
- **Home:** [Documentation Index](./README.md)

---

**Document Status:** ✅ Complete  
**Last Updated:** November 9, 2025  
**Review Cycle:** Quarterly
