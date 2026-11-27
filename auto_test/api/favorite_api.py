import requests
from config.setting import Config

class FavoriteAPI():
    def __init__(self,url,session=None):
        self.url = url
        self.session= session if  session else requests.Session()


    ##收藏/取消
    def toggle_favorite(self, video_id):
        response = self.session.post(f"http://{self.url}/api/favorite/toggle/{video_id}")
        return response.json()


    ## 是否已收藏
    def if_check(self,video_id):
        response = self.session.get(f"http://{self.url}/api/favorite/check/{video_id}")
        return response.json()

    ## 获取收藏列表
    def get_list(self):
        response = self.session.get(f"http://{self.url}/api/favorite/list")
        return response.json()
        