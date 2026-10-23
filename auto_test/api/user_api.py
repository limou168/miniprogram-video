import requests
from config.setting import Config
from common.logger import logger
class UserAPI:
    def __init__(self,url,session=None):
        self.url = url
        self.session= session if  session else requests.Session()

        
    def register(self, username, password):
        response = self.session.post(f"http://{self.url}/api/user/register", json={"username": username, "password": password})

        logger.info(f"【发送注册请求】 URL: http://{self.url}/api/user/register, 参数: {username},{password}")

        return response.json()

    def login(self, username, password):
        response = self.session.post(f"http://{self.url}/api/user/login", json={"username": username, "password": password})


        logger.info(f"【发送登录请求】 URL: http://{self.url}/api/user/register, 参数: {username},{password}")
        return response.json()