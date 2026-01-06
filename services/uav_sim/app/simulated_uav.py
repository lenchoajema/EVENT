from .uav_interface import UAVInterface
import paho.mqtt.client as mqtt
import json
import random
import math
import time
import logging

logger = logging.getLogger(__name__)

class SimulatedUAV(UAVInterface):
    def __init__(self, uav_id, name, broker_host, broker_port):
        super().__init__(uav_id, name, broker_host, broker_port)
        
        self.latitude = 37.7749 + random.uniform(-0.1, 0.1)
        self.longitude = -122.4194 + random.uniform(-0.1, 0.1)
        self.client = mqtt.Client(client_id=f"uav_{self.uav_id}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self):
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            logger.info(f"Simulated UAV {self.name} connected to MQTT broker")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT: {e}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"UAV {self.name} MQTT connection successful")
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
        self.mission = mission_data
        self.status = "flying"
        logger.info(f"UAV {self.name} assigned to mission: Alert {mission_data.get('alert_id')}")
        self.publish_status()

    def handle_command(self, command):
        cmd_type = command.get("type")
        if cmd_type == "return":
            self.mission = None
            self.status = "idle"
            logger.info(f"UAV {self.name} returning to base")
            self.publish_status()

    def publish_status(self):
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

    def loop(self):
        """Simulate movement and battery drain"""
        if self.mission and self.status == "flying":
            target_lat = self.mission.get("target_latitude")
            target_lon = self.mission.get("target_longitude")
            
            delta_lat = target_lat - self.latitude
            delta_lon = target_lon - self.longitude
            distance = math.sqrt(delta_lat**2 + delta_lon**2)
            
            if distance > 0.001:
                self.latitude += delta_lat * 0.1
                self.longitude += delta_lon * 0.1
                self.battery = max(0, self.battery - 0.1)
            else:
                logger.info(f"UAV {self.name} reached target")
                # Could trigger arrival event here
        
        self.publish_telemetry()
