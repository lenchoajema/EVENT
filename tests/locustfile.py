from locust import HttpUser, task, between
import random

class APIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login
        response = self.client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

    @task(3)
    def get_alerts(self):
        self.client.get("/api/satellite/alerts", headers=self.headers)

    @task(1)
    def create_uav_and_check(self):
        uav_data = {
            "name": f"Locust-UAV-{random.randint(1000, 9999)}",
            "current_latitude": 37.7,
            "current_longitude": -122.4,
            "status": "idle"
        }
        self.client.post("/api/uavs", json=uav_data, headers=self.headers)
