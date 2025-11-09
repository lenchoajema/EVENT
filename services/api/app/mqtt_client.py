import paho.mqtt.client as mqtt
import json
import os
import logging

logger = logging.getLogger(__name__)


class MQTTClient:
    def __init__(self):
        self.broker = os.getenv("MQTT_BROKER", "mosquitto")
        self.port = int(os.getenv("MQTT_PORT", "1883"))
        self.client = mqtt.Client(client_id="api_service", clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.connected = False

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info(f"✅ Connected to MQTT broker at {self.broker}:{self.port}")
            # Subscribe to relevant topics
            self.client.subscribe("telemetry/#")
            self.client.subscribe("detections/#")
        else:
            self.connected = False
            logger.error(f"❌ Failed to connect to MQTT broker, return code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            logger.debug(f"Received message on topic {msg.topic}: {payload}")
            
            # Handle telemetry updates
            if msg.topic.startswith("telemetry/"):
                self.handle_telemetry(msg.topic, payload)
            
            # Handle detection events
            elif msg.topic.startswith("detections/"):
                self.handle_detection(msg.topic, payload)
                
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def handle_telemetry(self, topic, payload):
        """Handle incoming telemetry data."""
        # This could update UAV status in database
        pass

    def handle_detection(self, topic, payload):
        """Handle incoming detection events."""
        # This could create detection records in database
        pass

    def connect(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            logger.info(f"MQTT client connecting to {self.broker}:{self.port}...")
        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        logger.info("MQTT client disconnected")

    def publish_alert(self, alert_id: int, alert_data: dict):
        """Publish satellite alert to priority queue for scheduler."""
        topic = "satellite/alerts"
        message = {
            "alert_id": alert_id,
            "timestamp": alert_data.get("created_at", ""),
            **alert_data
        }
        
        if self.connected:
            result = self.client.publish(topic, json.dumps(message), qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"📡 Published alert {alert_id} to topic {topic}")
            else:
                logger.error(f"Failed to publish alert {alert_id}")
        else:
            logger.warning("MQTT not connected, cannot publish alert")

    def publish_command(self, uav_id: str, command: dict):
        """Publish command to specific UAV."""
        topic = f"commands/{uav_id}"
        message = {
            "timestamp": command.get("timestamp", ""),
            **command
        }
        
        if self.connected:
            result = self.client.publish(topic, json.dumps(message), qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"🚁 Published command to UAV {uav_id} on topic {topic}")
            else:
                logger.error(f"Failed to publish command to UAV {uav_id}")
        else:
            logger.warning("MQTT not connected, cannot publish command")

    def publish_uav_command(self, uav_id: str, command: dict):
        """Alias for backward compatibility."""
        self.publish_command(uav_id, command)

