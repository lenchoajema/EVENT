import paho.mqtt.client as mqtt
import json
import os
import logging

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self):
        self.broker = os.getenv("MQTT_BROKER", "localhost")
        self.port = int(os.getenv("MQTT_PORT", "1883"))
        self.client = mqtt.Client(client_id="api_service")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {self.broker}:{self.port}")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")

    def on_message(self, client, userdata, msg):
        logger.info(f"Received message on topic {msg.topic}: {msg.payload.decode()}")

    def connect(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def publish_alert(self, alert_id: int, alert_data: dict):
        topic = "satellite/alerts"
        message = {
            "alert_id": alert_id,
            **alert_data
        }
        self.client.publish(topic, json.dumps(message))
        logger.info(f"Published alert {alert_id} to topic {topic}")

    def publish_uav_command(self, uav_id: int, command: dict):
        topic = f"uav/{uav_id}/command"
        self.client.publish(topic, json.dumps(command))
        logger.info(f"Published command to UAV {uav_id}")
