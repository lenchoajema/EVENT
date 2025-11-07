from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import logging

from .database import engine, Base, get_db
from .models import SatelliteAlert, UAV, Detection
from .schemas import (
    SatelliteAlertCreate, SatelliteAlertResponse,
    UAVCreate, UAVResponse, UAVStatusUpdate,
    DetectionCreate, DetectionResponse
)
from .mqtt_client import MQTTClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="UAV-Satellite Event Analysis API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MQTT client
mqtt_client = MQTTClient()

@app.on_event("startup")
async def startup_event():
    mqtt_client.connect()
    logger.info("Application started and MQTT client connected")

@app.on_event("shutdown")
async def shutdown_event():
    mqtt_client.disconnect()
    logger.info("Application shutdown and MQTT client disconnected")

@app.get("/")
async def root():
    return {"message": "UAV-Satellite Event Analysis API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Satellite Alerts endpoints
@app.post("/api/alerts", response_model=SatelliteAlertResponse)
def create_alert(alert: SatelliteAlertCreate, db: Session = Depends(get_db)):
    db_alert = SatelliteAlert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    # Publish alert to MQTT for UAV assignment
    mqtt_client.publish_alert(db_alert.id, alert.dict())
    logger.info(f"Created alert {db_alert.id} and published to MQTT")
    
    return db_alert

@app.get("/api/alerts", response_model=List[SatelliteAlertResponse])
def get_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alerts = db.query(SatelliteAlert).offset(skip).limit(limit).all()
    return alerts

@app.get("/api/alerts/{alert_id}", response_model=SatelliteAlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(SatelliteAlert).filter(SatelliteAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

# UAV endpoints
@app.post("/api/uavs", response_model=UAVResponse)
def create_uav(uav: UAVCreate, db: Session = Depends(get_db)):
    db_uav = UAV(**uav.dict())
    db.add(db_uav)
    db.commit()
    db.refresh(db_uav)
    logger.info(f"Created UAV {db_uav.id}")
    return db_uav

@app.get("/api/uavs", response_model=List[UAVResponse])
def get_uavs(db: Session = Depends(get_db)):
    uavs = db.query(UAV).all()
    return uavs

@app.get("/api/uavs/{uav_id}", response_model=UAVResponse)
def get_uav(uav_id: int, db: Session = Depends(get_db)):
    uav = db.query(UAV).filter(UAV.id == uav_id).first()
    if not uav:
        raise HTTPException(status_code=404, detail="UAV not found")
    return uav

@app.patch("/api/uavs/{uav_id}", response_model=UAVResponse)
def update_uav_status(uav_id: int, status_update: UAVStatusUpdate, db: Session = Depends(get_db)):
    uav = db.query(UAV).filter(UAV.id == uav_id).first()
    if not uav:
        raise HTTPException(status_code=404, detail="UAV not found")
    
    for key, value in status_update.dict(exclude_unset=True).items():
        setattr(uav, key, value)
    
    db.commit()
    db.refresh(uav)
    logger.info(f"Updated UAV {uav_id} status")
    return uav

# Detection endpoints
@app.post("/api/detections", response_model=DetectionResponse)
def create_detection(detection: DetectionCreate, db: Session = Depends(get_db)):
    db_detection = Detection(**detection.dict())
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)
    logger.info(f"Created detection {db_detection.id}")
    return db_detection

@app.get("/api/detections", response_model=List[DetectionResponse])
def get_detections(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    detections = db.query(Detection).offset(skip).limit(limit).all()
    return detections

@app.get("/api/detections/uav/{uav_id}", response_model=List[DetectionResponse])
def get_detections_by_uav(uav_id: int, db: Session = Depends(get_db)):
    detections = db.query(Detection).filter(Detection.uav_id == uav_id).all()
    return detections

@app.get("/api/detections/alert/{alert_id}", response_model=List[DetectionResponse])
def get_detections_by_alert(alert_id: int, db: Session = Depends(get_db)):
    detections = db.query(Detection).filter(Detection.alert_id == alert_id).all()
    return detections
