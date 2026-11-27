
from common.util import read_yaml
import requests
import os

class UploadAPI():

    def __init__(self,url,session=None):
        self.url = url
        self.session= session if  session else requests.Session()

    def upload_cover(self,path):
        with open(path, "rb") as f:
            files = {
                "file": (os.path.basename(path), f, "image/jpeg")
            }
            response = self.session.post(f"http://{self.url}/api/file/upload/cover",files=files,timeout=30)

                                     
        return response.json()