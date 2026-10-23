import requests
from config.setting import Config

class VideoApi:
    def __init__(self,url,session=None):
        self.url = url
        self.session= session if session else requests.Session()

    def getlist(self):
        response = self.session.get(f"http://{self.url}/api/video/list")
        return response.json()

    def getListById(self, video_id):
        response = self.session.get(f"http://{self.url}/api/video/{video_id}")
        return response.json()
    def getHot(self):
        response = self.session.get(f"http://{self.url}/api/video/hot")
        return response.json()

    
    def getregister(self,keyword):
        params ={"keyword":keyword}
        response = self.session.get(f"http://{self.url}/api/video/search",params=params)
        return response.json()
    def suggest(self,keyword):
        params ={"keyword":keyword}
        response = self.session.get(f"http://{self.url}/api/video/search/suggest",params=params)
        return response.json()
    
    def episodes(self,id): 
        response = self.session.get(f"http://{self.url}/api/video/{id}/episodes")

        # print(f"\n>>> 实际请求的URL: {response.url}")
        return response.json()

    def tags(self,categoryId):
        params ={"categoryId":categoryId}
        response = self.session.get(f"http://{self.url}/api/video/tags",params=params)
        return response.json()