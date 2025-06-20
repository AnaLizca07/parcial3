from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)  

    @task(1)
    def load_root(self):
        self.client.get("/")

    @task(1)
    def load_health(self):
        self.client.get("/health")
