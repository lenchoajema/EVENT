import paho.mqtt.client as mqtt
import json
import logging
import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np
import torch

# Patch torch.load to disable weights_only for PyTorch 2.6+ compatibility
_original_torch_load = torch.load

def _torch_load_patch(f, *args, **kwargs):
    """Patch torch.load to use weights_only=False by default for backwards compatibility."""
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _original_torch_load(f, *args, **kwargs)

torch.load = _torch_load_patch

# Now import YOLO after patching torch.load
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EdgeInference:
    def __init__(self):
        self.broker = os.getenv("MQTT_BROKER", "localhost")
        self.port = int(os.getenv("MQTT_PORT", "1883"))
        
        # Database connection
        db_url = os.getenv("DATABASE_URL", "postgresql://event_user:event_pass@localhost:5432/event_db")
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Load YOLOv8 model
        model_path = os.getenv("MODEL_PATH", "yolov8n.pt")
        logger.info(f"Loading YOLOv8 model: {model_path}")
        try:
            self.model = YOLO(model_path)
            logger.info("YOLOv8 model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            logger.info("Downloading YOLOv8 nano model...")
            self.model = YOLO("yolov8n.pt")
        
        # MQTT client
        self.client = mqtt.Client(client_id="edge_inference")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Edge inference service connected to MQTT broker")
            # Subscribe to detection requests
            client.subscribe("detections")
            client.subscribe("uav/+/telemetry")
        else:
            logger.error(f"Failed to connect, return code {rc}")
    
    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            
            if msg.topic == "detections":
                self.handle_detection(payload)
            elif "telemetry" in msg.topic:
                # Simulate inference on telemetry data
                self.simulate_inference(payload)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def handle_detection(self, detection_data):
        """Process detection data and store in database"""
        try:
            from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
            from sqlalchemy.ext.declarative import declarative_base
            from datetime import datetime
            from geoalchemy2 import Geometry
            
            Base = declarative_base()
            
            class Detection(Base):
                __tablename__ = "detections"
                id = Column(Integer, primary_key=True, index=True)
                uav_id = Column(Integer, ForeignKey("uavs.id"), nullable=False)
                alert_id = Column(Integer, ForeignKey("satellite_alerts.id"), nullable=True)
                object_class = Column(String, nullable=False)
                confidence = Column(Float, nullable=False)
                latitude = Column(Float, nullable=False)
                longitude = Column(Float, nullable=False)
                location = Column(Geometry('POINT', srid=4326))
                image_path = Column(String, nullable=True)
                metadata = Column(Text, nullable=True)
                created_at = Column(DateTime, default=datetime.utcnow)
            
            db = self.SessionLocal()
            try:
                detection = Detection(
                    uav_id=detection_data.get("uav_id"),
                    alert_id=detection_data.get("alert_id"),
                    object_class=detection_data.get("object_class"),
                    confidence=detection_data.get("confidence"),
                    latitude=detection_data.get("latitude"),
                    longitude=detection_data.get("longitude"),
                    metadata=json.dumps(detection_data)
                )
                db.add(detection)
                db.commit()
                logger.info(f"Stored detection: {detection_data.get('object_class')} from UAV {detection_data.get('uav_id')}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error storing detection: {e}")
    
    def simulate_inference(self, telemetry_data):
        """Simulate running inference on simulated camera feed"""
        # In a real system, this would process actual camera frames
        # For now, we'll simulate detections periodically
        import random
        
        if random.random() < 0.1:  # 10% chance of detection
            # Simulate detection using YOLOv8 classes
            classes = ["person", "car", "truck", "bicycle", "motorcycle", "fire hydrant", "stop sign"]
            
            detection = {
                "uav_id": telemetry_data.get("uav_id"),
                "object_class": random.choice(classes),
                "confidence": random.uniform(0.6, 0.95),
                "latitude": telemetry_data.get("latitude"),
                "longitude": telemetry_data.get("longitude"),
                "timestamp": time.time()
            }
            
            # Publish inference result
            self.client.publish("inference/results", json.dumps(detection))
            logger.info(f"Inference result: {detection['object_class']} (conf: {detection['confidence']:.2f})")
    
    def run_inference_on_image(self, image_path):
        """Run YOLOv8 inference on an image"""
        try:
            results = self.model(image_path)
            detections = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    detection = {
                        "class": self.model.names[int(box.cls)],
                        "confidence": float(box.conf),
                        "bbox": box.xyxy.tolist()
                    }
                    detections.append(detection)
            
            return detections
        except Exception as e:
            logger.error(f"Error running inference: {e}")
            return []
    
    def run(self):
        """Main service loop"""
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()
        
        logger.info("Edge inference service started")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Edge inference service stopped")
        finally:
            self.client.loop_stop()
            self.client.disconnect()

def main():
    service = EdgeInference()
    service.run()

if __name__ == "__main__":
    main()
