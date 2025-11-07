import paho.mqtt.client as mqtt
import json
import time
import logging
import os
import random
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UAVSimulator:
    def __init__(self, uav_id, name):
        self.uav_id = uav_id
        self.name = name
        self.broker = os.getenv("MQTT_BROKER", "localhost")
        self.port = int(os.getenv("MQTT_PORT", "1883"))
        
        # UAV state
        self.latitude = 37.7749 + random.uniform(-0.1, 0.1)  # SF area
        self.longitude = -122.4194 + random.uniform(-0.1, 0.1)
        self.battery = 100.0
        self.status = "idle"
        self.mission = None
        
        # MQTT client
        self.client = mqtt.Client(client_id=f"uav_{self.uav_id}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"UAV {self.name} connected to MQTT broker")
            # Subscribe to mission and status topics
            client.subscribe(f"uav/{self.uav_id}/mission")
            client.subscribe(f"uav/{self.uav_id}/command")
        else:
            logger.error(f"Failed to connect, return code {rc}")
    
    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"UAV {self.name} received message on {msg.topic}: {payload}")
            
            if "mission" in msg.topic:
                self.handle_mission(payload)
            elif "command" in msg.topic:
                self.handle_command(payload)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def handle_mission(self, mission_data):
        """Handle new mission assignment"""
        self.mission = mission_data
        self.status = "flying"
        logger.info(f"UAV {self.name} assigned to mission: Alert {mission_data.get('alert_id')}")
        
        # Publish status update
        self.publish_status()
    
    def handle_command(self, command):
        """Handle UAV commands"""
        cmd_type = command.get("type")
        if cmd_type == "return":
            self.mission = None
            self.status = "idle"
            logger.info(f"UAV {self.name} returning to base")
    
    def publish_status(self):
        """Publish current UAV status"""
        status = {
            "uav_id": self.uav_id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "battery": self.battery,
            "status": self.status,
            "mission": self.mission
        }
        self.client.publish(f"uav/{self.uav_id}/status", json.dumps(status))
    
    def publish_telemetry(self):
        """Publish telemetry data"""
        telemetry = {
            "uav_id": self.uav_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": random.uniform(50, 150),
            "speed": random.uniform(10, 30),
            "battery": self.battery,
            "timestamp": time.time()
        }
        self.client.publish(f"uav/{self.uav_id}/telemetry", json.dumps(telemetry))
    
    def simulate_movement(self):
        """Simulate UAV movement towards mission target"""
        if self.mission and self.status == "flying":
            target_lat = self.mission.get("target_latitude")
            target_lon = self.mission.get("target_longitude")
            
            # Move towards target
            delta_lat = target_lat - self.latitude
            delta_lon = target_lon - self.longitude
            distance = math.sqrt(delta_lat**2 + delta_lon**2)
            
            if distance > 0.001:  # Still moving
                # Move 10% of the way each step
                self.latitude += delta_lat * 0.1
                self.longitude += delta_lon * 0.1
                self.battery = max(0, self.battery - 0.5)
            else:
                # Reached target
                logger.info(f"UAV {self.name} reached target for alert {self.mission.get('alert_id')}")
                self.status = "investigating"
                
                # Publish detection event
                self.publish_detection()
                
                # Complete mission after investigation
                time.sleep(2)
                self.mission = None
                self.status = "idle"
        
        # Recharge if battery is low
        if self.battery < 20:
            self.status = "charging"
            self.battery = min(100, self.battery + 5)
            if self.battery >= 100:
                self.status = "idle"
    
    def publish_detection(self):
        """Publish detection event when investigating an alert"""
        if self.mission:
            detection = {
                "uav_id": self.uav_id,
                "alert_id": self.mission.get("alert_id"),
                "latitude": self.latitude,
                "longitude": self.longitude,
                "object_class": random.choice(["fire", "smoke", "vehicle", "person", "building"]),
                "confidence": random.uniform(0.7, 0.99),
                "timestamp": time.time()
            }
            self.client.publish("detections", json.dumps(detection))
            logger.info(f"UAV {self.name} published detection: {detection['object_class']}")
    
    def run(self):
        """Main simulation loop"""
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()
        
        logger.info(f"UAV {self.name} simulation started")
        
        try:
            while True:
                self.simulate_movement()
                self.publish_status()
                self.publish_telemetry()
                time.sleep(5)  # Update every 5 seconds
        except KeyboardInterrupt:
            logger.info(f"UAV {self.name} simulation stopped")
        finally:
            self.client.loop_stop()
            self.client.disconnect()

def main():
    """Run multiple UAV simulations"""
    simulators = []
    num_uavs = int(os.getenv("NUM_UAVS", "3"))
    
    for i in range(1, num_uavs + 1):
        sim = UAVSimulator(i, f"UAV-{i}")
        simulators.append(sim)
    
    # Start all simulators in separate threads
    import threading
    threads = []
    for sim in simulators:
        thread = threading.Thread(target=sim.run)
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down all UAV simulators")

if __name__ == "__main__":
    main()
