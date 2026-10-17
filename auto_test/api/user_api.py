import requests
from config.setting import Config

class UserAPI:
    def __init__(self):
        self.url = Config.URL

    def register(self, username, password):
        response = requests.post(f"http://{self.url}/api/user/register", json={"username": username, "password": password})
        return response.json()

    def login(self, username, password):
        response = requests.post(f"http://{self.url}/api/user/login", json={"username": username, "password": password})
        return response.json()