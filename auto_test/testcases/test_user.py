import pytest
import allure
from api.user_api import UserAPI
from common.util import read_yaml


user_data =read_yaml("data/users.yaml")

@allure.epic("小程序视频接口测试")
@allure.feature("用户模块")
class TestUser:
    def setup_method(self):
        self.user_api =UserAPI()


    @allure.story("注册接口")
    @allure.title("测试正常用户注册")
    @pytest.mark.parametrize("user", user_data["register_users"])
    def test_register(self,user):
        with allure.step(f"发送注册请求，用户: {user['username']}"):
            res=self.user_api.register(user["username"],user["password"])
            print(res)
        with allure.step("断言结果"):
            assert res["code"]==200
            assert res["message"] == "success"
            assert res["data"] == "注册成功"

    @allure.story("登录接口")
    @allure.title("测试正常用户登录")
    @pytest.mark.parametrize("user", user_data["login_users"])
    def test_login(self,user):
        with allure.step(f"发送登录请求，用户: {user['username']}"):
            res=self.user_api.login(user["username"],user["password"])
            
        with allure.step("断言结果"):
            assert res["code"]==200 
            assert res["message"] == "success"
            