from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class UAVInterface(ABC):
    def __init__(self, uav_id, name, broker_host, broker_port):
        self.uav_id = uav_id
        self.name = name
        self.broker_host = broker_host
        self.broker_port = broker_port
        
        # Common state
        self.latitude = 0.0
        self.longitude = 0.0
        self.battery = 100.0
        self.status = "idle"
        self.mission = None

    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def loop(self):
        """Main loop called periodically"""
        pass
        
    @abstractmethod
    def handle_mission(self, mission_data):
        pass
        
    @abstractmethod
    def handle_command(self, command):
        pass
    
    @abstractmethod
    def publish_status(self):
        pass

    @abstractmethod
    def publish_telemetry(self):
        pass
