import os
import time
import logging
import signal
import sys
from app.simulated_uav import SimulatedUAV
from app.real_uav import RealUAV

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    uav_id = os.getenv("UAV_ID", "1")
    uav_name = os.getenv("UAV_NAME", f"UAV-{uav_id}")
    broker_host = os.getenv("MQTT_BROKER", "mosquitto")
    broker_port = int(os.getenv("MQTT_PORT", "1883"))
    
    # Mode selection
    use_real = os.getenv("REAL_UAV", "false").lower() in ("true", "1", "yes")
    
    if use_real:
        logger.info(f"Starting UAV Service in REAL HARDWARE mode for {uav_name}")
        uav = RealUAV(uav_id, uav_name, broker_host, broker_port)
    else:
        logger.info(f"Starting UAV Service in SIMULATION mode for {uav_name}")
        uav = SimulatedUAV(uav_id, uav_name, broker_host, broker_port)
    
    uav.connect()
    
    running = True
    def signal_handler(sig, frame):
        nonlocal running
        logger.info("Shutting down...")
        running = False
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    while running:
        uav.loop()
        time.sleep(1)

if __name__ == "__main__":
    main()
