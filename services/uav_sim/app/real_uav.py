from .uav_interface import UAVInterface
import paho.mqtt.client as mqtt
import json
import time
import logging
import os

logger = logging.getLogger(__name__)

# Try importing dronekit, handle failure if not installed
try:
    from dronekit import connect, VehicleMode, LocationGlobalRelative
    DRONEKIT_AVAILABLE = True
except ImportError:
    DRONEKIT_AVAILABLE = False
    logger.warning("DroneKit not installed. Real UAV mode will fail if attempted.")

class RealUAV(UAVInterface):
    def __init__(self, uav_id, name, broker_host, broker_port):
        super().__init__(uav_id, name, broker_host, broker_port)
        
        self.connection_string = os.getenv("UAV_CONNECTION_STRING", "/dev/ttyUSB0")
        self.baud_rate = int(os.getenv("UAV_BAUD_RATE", "57600"))
        self.vehicle = None
        
        self.client = mqtt.Client(client_id=f"uav_{self.uav_id}_real")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self):
        # 1. Connect MQTT
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            logger.info(f"Real UAV MQTT connected to {self.broker_host}")
        except Exception as e:
            logger.error(f"MQTT Connect failed: {e}")

        # 2. Connect to Flight Controller
        if DRONEKIT_AVAILABLE:
            try:
                logger.info(f"Connecting to vehicle on {self.connection_string}...")
                self.vehicle = connect(self.connection_string, wait_ready=True, baud=self.baud_rate)
                logger.info(f"Vehicle connected. Mode: {self.vehicle.mode.name}")
                
                # Add listeners
                self.vehicle.add_attribute_listener('location.global_frame', self.location_callback)
                self.vehicle.add_attribute_listener('battery', self.battery_callback)
                self.vehicle.add_attribute_listener('mode', self.mode_callback)
                
            except Exception as e:
                logger.error(f"Failed to connect to vehicle: {e}")
        else:
            logger.error("DroneKit unavailable. Cannot connect to real hardware.")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            client.subscribe(f"uav/{self.uav_id}/mission")
            client.subscribe(f"uav/{self.uav_id}/command")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            if "mission" in msg.topic:
                self.handle_mission(payload)
            elif "command" in msg.topic:
                self.handle_command(payload)
        except Exception as e:
            logger.error(f"Message error: {e}")

    def handle_mission(self, mission_data):
        if not self.vehicle:
            logger.error("No vehicle connected")
            return

        logger.info(f"Received mission: {mission_data}")
        target_lat = mission_data.get("target_latitude")
        target_lon = mission_data.get("target_longitude")
        alt = mission_data.get("altitude", 30)

        # Basic DroneKit mission logic
        # 1. Arm and Takeoff
        if self.vehicle.mode.name != "GUIDED":
            self.vehicle.mode = VehicleMode("GUIDED")
        
        if not self.vehicle.armed:
            self.vehicle.armed = True
            time.sleep(1)
            self.vehicle.simple_takeoff(alt)
        
        # 2. Go to location
        point = LocationGlobalRelative(target_lat, target_lon, alt)
        self.vehicle.simple_goto(point)
        self.status = "flying"
        self.mission = mission_data
        self.publish_status()

    def handle_command(self, command):
        if not self.vehicle:
            return

        cmd_type = command.get("type")
        if cmd_type == "return":
            self.vehicle.mode = VehicleMode("RTL")
            self.status = "returning"
            self.mission = None
            logger.info("RTL triggered")
        elif cmd_type == "land":
            self.vehicle.mode = VehicleMode("LAND")
            self.status = "landing"

    def location_callback(self, self_, attr_name, value):
        self.latitude = value.lat
        self.longitude = value.lon
        self.publish_telemetry()

    def battery_callback(self, self_, attr_name, value):
        self.battery = value.level
        
    def mode_callback(self, self_, attr_name, value):
        self.status = value.name

    def publish_status(self):
        status = {
            "uav_id": self.uav_id,
            "status": self.status,
            "connected": self.vehicle is not None
        }
        self.client.publish(f"uav/{self.uav_id}/status", json.dumps(status))

    def publish_telemetry(self):
        if not self.vehicle:
            return
            
        telem = {
            "uav_id": self.uav_id,
            "latitude": self.vehicle.location.global_frame.lat,
            "longitude": self.vehicle.location.global_frame.lon,
            "altitude": self.vehicle.location.global_relative_frame.alt,
            "speed": self.vehicle.groundspeed,
            "battery": self.vehicle.battery.level,
            "timestamp": time.time()
        }
        self.client.publish(f"uav/{self.uav_id}/telemetry", json.dumps(telem))

    def loop(self):
        # DroneKit callbacks handle updates, just sleep to keep thread alive?
        # Actually in main we loop, so here we might just do heartbeat checks
        pass
