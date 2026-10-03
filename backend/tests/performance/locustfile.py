from locust import HttpUser, between, task


class TripMateUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def list_destinations(self):
        self.client.get(
            "/api/v1/destinations?page=1&limit=20",
            name="GET /api/v1/destinations",
        )
