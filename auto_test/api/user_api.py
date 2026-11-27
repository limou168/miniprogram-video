import requests
from config.setting import Config
from common.logger import logger
from common.sgin import build_auth_header
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


        logger.info(f"【发送登录请求】 URL: http://{self.url}/api/user/login, 参数: {username},{password}")
        return response.json()


    def get_info(self,token,name):
        auth_headers = build_auth_header(token, name, Config.SECRET_KEY)
        self.session.headers.update(auth_headers)
        response = self.session.get(f"http://{self.url}/api/user/info")
        return response.json()
    
    def updateInfo(self,name,nickname):
        response = self.session.put(f"http://{self.url}/api/user/info",json={"username": name, "nickname": nickname})
        return response.json()
    
    def changePassword(self,password):
        response = self.session.put(f"http://{self.url}/api/user/password",json={"password":password})
        return response.json()