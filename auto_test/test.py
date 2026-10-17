import pytest
import requests
import allure



class User:
    def __init__(self, name,password):
        self.name = name
        self.password = password
    def __repr__(self):
        return f"User({self.name})"
    
@allure.epic("小程序视频接口测试")
@allure.feature("用户登录模块")
class TestUser:
    url="http://127.0.0.1:8080"
    USERS = [
        User("admin", "admin1"),
        User("user1", "password1"),
        User("user2", "password2"),
    ]

    text=["/api/user","/api/video","/api/video/1","/api/video/1/comment","/api/video/1/comment/1"]

    @pytest.mark.parametrize("user", USERS)
    @allure.story("注册接口")
    @allure.title("测试不同用户")
    def test_video_api(self,user):

        with allure.step("发送注册请求"):
            res=requests.post(self.url+self.text[0]+"/register",json={"username":user.name,"password":user.password})
            response=res.json()
            print(response)

        with allure.step("断言注册结果"):
            assert response["code"]==200
            assert response["message"]=="success"
            assert response["data"]=="注册成功"
        
    @pytest.mark.parametrize("user", USERS)
    @allure.story("登录接口")
    @allure.title("测试不同用户登录")
    def test_video_logging(self,user):
        with allure.step("发送登录请求"):
            res=requests.post(self.url+self.text[0]+"/login",json={"username":user.name,"password":user.password})
            response=res.json()
            print(response,"登录结果"+user.name)
        with allure.step("断言登录结果"):
            assert response["code"]==200
            assert response["message"]=="success"
    
