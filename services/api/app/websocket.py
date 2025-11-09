"""
WebSocket Server for Real-Time Updates.

Implements WebSocket protocol for telemetry, detections, and alerts
as specified in Appendix C: API & Message Protocols.
"""

import json
import asyncio
from typing import Dict, Set, List
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect, Depends, status
from sqlalchemy.orm import Session
import logging

from .auth import decode_access_token, AuthenticationError
from .database import get_db

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections and message broadcasting.
    """
    
    def __init__(self):
        # Active connections: {websocket: {"user_id": str, "channels": set}}
        self.active_connections: Dict[WebSocket, Dict] = {}
        
        # Channel subscriptions: {channel_name: set of websockets}
        self.channel_subscriptions: Dict[str, Set[WebSocket]] = {
            "telemetry": set(),
            "detections": set(),
            "alerts": set(),
            "missions": set(),
            "system": set(),
        }
        
        # Heartbeat tracking
        self.last_ping: Dict[WebSocket, float] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept WebSocket connection."""
        await websocket.accept()
        self.active_connections[websocket] = {
            "user_id": None,
            "channels": set(),
            "authenticated": False
        }
        logger.info("WebSocket connection accepted")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        # Unsubscribe from all channels
        if websocket in self.active_connections:
            channels = self.active_connections[websocket].get("channels", set())
            for channel in channels:
                if channel in self.channel_subscriptions:
                    self.channel_subscriptions[channel].discard(websocket)
            
            del self.active_connections[websocket]
        
        if websocket in self.last_ping:
            del self.last_ping[websocket]
        
        logger.info("WebSocket connection closed")
    
    async def authenticate(self, websocket: WebSocket, token: str) -> bool:
        """Authenticate WebSocket connection."""
        try:
            payload = decode_access_token(token)
            self.active_connections[websocket]["user_id"] = payload.get("sub")
            self.active_connections[websocket]["username"] = payload.get("username")
            self.active_connections[websocket]["authenticated"] = True
            
            await self.send_personal_message(websocket, {
                "type": "auth_success",
                "message": "Authentication successful"
            })
            
            logger.info(f"WebSocket authenticated for user {payload.get('username')}")
            return True
            
        except AuthenticationError as e:
            await self.send_personal_message(websocket, {
                "type": "auth_error",
                "message": str(e.detail)
            })
            return False
    
    def subscribe(self, websocket: WebSocket, channels: List[str]):
        """Subscribe WebSocket to channels."""
        if websocket not in self.active_connections:
            return
        
        for channel in channels:
            if channel in self.channel_subscriptions:
                self.channel_subscriptions[channel].add(websocket)
                self.active_connections[websocket]["channels"].add(channel)
        
        logger.info(f"WebSocket subscribed to channels: {channels}")
    
    def unsubscribe(self, websocket: WebSocket, channels: List[str]):
        """Unsubscribe WebSocket from channels."""
        if websocket not in self.active_connections:
            return
        
        for channel in channels:
            if channel in self.channel_subscriptions:
                self.channel_subscriptions[channel].discard(websocket)
                self.active_connections[websocket]["channels"].discard(channel)
        
        logger.info(f"WebSocket unsubscribed from channels: {channels}")
    
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """Send message to specific WebSocket."""
        try:
            message["timestamp"] = datetime.utcnow().isoformat()
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_channel(self, channel: str, message: dict):
        """Broadcast message to all subscribers of a channel."""
        if channel not in self.channel_subscriptions:
            return
        
        message["timestamp"] = datetime.utcnow().isoformat()
        
        disconnected = []
        for websocket in self.channel_subscriptions[channel]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to channel {channel}: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def broadcast_telemetry(self, uav_id: str, data: dict):
        """Broadcast UAV telemetry update."""
        await self.broadcast_to_channel("telemetry", {
            "type": "telemetry",
            "uav_id": uav_id,
            "data": data
        })
    
    async def broadcast_detection(self, detection_data: dict):
        """Broadcast detection event."""
        await self.broadcast_to_channel("detections", {
            "type": "detection",
            "data": detection_data
        })
    
    async def broadcast_alert(self, alert_data: dict):
        """Broadcast alert event."""
        await self.broadcast_to_channel("alerts", {
            "type": "alert",
            "data": alert_data
        })
    
    async def broadcast_mission_update(self, mission_data: dict):
        """Broadcast mission status update."""
        await self.broadcast_to_channel("missions", {
            "type": "mission_update",
            "data": mission_data
        })
    
    async def broadcast_system_status(self, status_data: dict):
        """Broadcast system status update."""
        await self.broadcast_to_channel("system", {
            "type": "system_status",
            "data": status_data
        })
    
    async def handle_ping(self, websocket: WebSocket):
        """Handle heartbeat ping."""
        self.last_ping[websocket] = datetime.utcnow().timestamp()
        await self.send_personal_message(websocket, {"type": "pong"})
    
    async def start_heartbeat_monitor(self):
        """Monitor WebSocket connections for heartbeat timeout."""
        while True:
            await asyncio.sleep(30)  # Check every 30 seconds
            
            current_time = datetime.utcnow().timestamp()
            timeout_threshold = 60  # 60 seconds timeout
            
            disconnected = []
            for websocket, last_ping_time in self.last_ping.items():
                if current_time - last_ping_time > timeout_threshold:
                    logger.warning("WebSocket heartbeat timeout detected")
                    disconnected.append(websocket)
            
            for websocket in disconnected:
                try:
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                except:
                    pass
                self.disconnect(websocket)
    
    def get_statistics(self) -> dict:
        """Get WebSocket connection statistics."""
        return {
            "total_connections": len(self.active_connections),
            "authenticated_connections": sum(
                1 for conn in self.active_connections.values()
                if conn.get("authenticated")
            ),
            "channel_subscriptions": {
                channel: len(subscribers)
                for channel, subscribers in self.channel_subscriptions.items()
            }
        }


# Global connection manager instance
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    Main WebSocket endpoint handler.
    
    Handles authentication, subscriptions, and message routing.
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "auth":
                # Authenticate connection
                token = data.get("token")
                if not token:
                    await manager.send_personal_message(websocket, {
                        "type": "error",
                        "message": "Token required for authentication"
                    })
                    continue
                
                await manager.authenticate(websocket, token)
            
            elif message_type == "subscribe":
                # Subscribe to channels
                if not manager.active_connections[websocket].get("authenticated"):
                    await manager.send_personal_message(websocket, {
                        "type": "error",
                        "message": "Authentication required"
                    })
                    continue
                
                channels = data.get("channels", [])
                manager.subscribe(websocket, channels)
                
                await manager.send_personal_message(websocket, {
                    "type": "subscribed",
                    "channels": channels
                })
            
            elif message_type == "unsubscribe":
                # Unsubscribe from channels
                channels = data.get("channels", [])
                manager.unsubscribe(websocket, channels)
                
                await manager.send_personal_message(websocket, {
                    "type": "unsubscribed",
                    "channels": channels
                })
            
            elif message_type == "ping":
                # Handle heartbeat ping
                await manager.handle_ping(websocket)
            
            elif message_type == "command":
                # Handle UAV command (requires authentication and permissions)
                if not manager.active_connections[websocket].get("authenticated"):
                    await manager.send_personal_message(websocket, {
                        "type": "error",
                        "message": "Authentication required"
                    })
                    continue
                
                # TODO: Implement command handling with RBAC
                logger.info(f"Command received: {data}")
            
            else:
                await manager.send_personal_message(websocket, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected normally")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Helper functions for broadcasting from other parts of the application

async def broadcast_telemetry(uav_id: str, telemetry_data: dict):
    """Broadcast telemetry from external source."""
    await manager.broadcast_telemetry(uav_id, telemetry_data)


async def broadcast_detection(detection_data: dict):
    """Broadcast detection from external source."""
    await manager.broadcast_detection(detection_data)


async def broadcast_alert(alert_data: dict):
    """Broadcast alert from external source."""
    await manager.broadcast_alert(alert_data)


async def broadcast_mission_update(mission_data: dict):
    """Broadcast mission update from external source."""
    await manager.broadcast_mission_update(mission_data)
