from .celery_app import celery_app
from .database import SessionLocal
from .models import SatelliteAlert, UAV
import paho.mqtt.client as mqtt
import json
import os
import logging
import math

logger = logging.getLogger(__name__)

def get_mqtt_client():
    broker = os.getenv("MQTT_BROKER", "localhost")
    port = int(os.getenv("MQTT_PORT", "1883"))
    client = mqtt.Client(client_id="scheduler_service")
    client.connect(broker, port, 60)
    return client

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers using Haversine formula"""
    R = 6371  # Earth radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

@celery_app.task(name="app.tasks.monitor_uav_status")
def monitor_uav_status():
    """Monitor UAV battery levels and status"""
    db = SessionLocal()
    try:
        uavs = db.query(UAV).all()
        for uav in uavs:
            if uav.battery_level < 20 and uav.status != "charging":
                logger.warning(f"UAV {uav.name} battery low: {uav.battery_level}%")
                uav.status = "charging"
                db.commit()
                
                # Notify via MQTT
                client = get_mqtt_client()
                client.publish(f"uav/{uav.id}/status", json.dumps({
                    "status": "charging",
                    "battery": uav.battery_level
                }))
                client.disconnect()
        
        logger.info(f"Monitored {len(uavs)} UAVs")
        return f"Monitored {len(uavs)} UAVs"
    finally:
        db.close()

@celery_app.task(name="app.tasks.process_pending_alerts")
def process_pending_alerts():
    """Assign UAVs to pending satellite alerts"""
    db = SessionLocal()
    try:
        # Get pending alerts
        pending_alerts = db.query(SatelliteAlert).filter(
            SatelliteAlert.status == "pending"
        ).all()
        
        # Get available UAVs
        available_uavs = db.query(UAV).filter(
            UAV.status == "idle",
            UAV.battery_level > 30
        ).all()
        
        assigned_count = 0
        for alert in pending_alerts:
            if not available_uavs:
                break
            
            # Find nearest UAV
            best_uav = None
            min_distance = float('inf')
            
            for uav in available_uavs:
                if uav.current_latitude and uav.current_longitude:
                    distance = calculate_distance(
                        alert.latitude, alert.longitude,
                        uav.current_latitude, uav.current_longitude
                    )
                    if distance < min_distance:
                        min_distance = distance
                        best_uav = uav
            
            if best_uav:
                # Assign UAV to alert
                alert.assigned_uav_id = best_uav.id
                alert.status = "assigned"
                best_uav.status = "assigned"
                db.commit()
                
                # Send mission command via MQTT
                client = get_mqtt_client()
                client.publish(f"uav/{best_uav.id}/mission", json.dumps({
                    "alert_id": alert.id,
                    "target_latitude": alert.latitude,
                    "target_longitude": alert.longitude,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity
                }))
                client.disconnect()
                
                available_uavs.remove(best_uav)
                assigned_count += 1
                logger.info(f"Assigned UAV {best_uav.name} to alert {alert.id}")
        
        logger.info(f"Processed {len(pending_alerts)} alerts, assigned {assigned_count} UAVs")
        return f"Assigned {assigned_count} UAVs to alerts"
    finally:
        db.close()

@celery_app.task(name="app.tasks.simulate_battery_drain")
def simulate_battery_drain():
    """Simulate battery drain for flying UAVs"""
    db = SessionLocal()
    try:
        flying_uavs = db.query(UAV).filter(UAV.status.in_(["assigned", "flying"])).all()
        
        for uav in flying_uavs:
            # Drain battery by 1-5% per cycle
            uav.battery_level = max(0, uav.battery_level - 2)
            db.commit()
        
        return f"Drained battery for {len(flying_uavs)} UAVs"
    finally:
        db.close()
