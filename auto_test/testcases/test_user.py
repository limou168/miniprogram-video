import pytest
import allure
from api.user_api import UserAPI
from common.util import read_yaml
from common.logger import logger
from common.db_util import DBUtil
import random
import time

user_data =read_yaml("data/users.yaml")

@allure.epic("小程序视频接口测试")
@allure.feature("用户模块")

class TestUser:

    register_random=[]
    count=5
    while(count):
        register_random.append({"username": f"name{random.randint(100, 999)}", "password":  "pwd123"})
        count=count-1;

    @allure.story("注册接口")
    @allure.title("测试正常用户注册")
    @pytest.mark.parametrize("user", register_random)
    def test_register(self,user,user_api,db_conn):
        with allure.step(f"发送注册请求，用户: {user['username']}"):
            logger.info(f"=== 开始测试注册接口，测试数据: {user} ===") 
            res=user_api.register(user["username"],user["password"])
            
        with allure.step("断言结果"):
            assert res["code"]==200 ,f"❌ 注册失败，后端返回：{res}"
            assert res["message"] == "success"
            assert res["data"] == "注册成功"
        with allure.step("数据库匹配断言结果"):

            logger.info(f"数据库连接配置: {db_conn.conn}")
            sql=f"select * from sys_user where username='{user['username']}'"
            logger.info(f"====== 真实执行的 SQL 语句: {sql}")

            time.sleep(0.5)
            res=db_conn.query_one(sql)
            logger.info(f"======数据库获取到的注册信息{res}")
            assert res["username"]==user['username']
           

    @allure.story("登录接口")
    @allure.title("测试正常用户登录")
    @pytest.mark.parametrize("user", user_data["login_users"])
    def test_login(self,user,user_api):
        with allure.step(f"发送登录请求，用户: {user['username']}"):
            logger.info(f"=== 开始测试登录接口，测试数据: {user} ===") 
            res=user_api.login(user["username"],user["password"])
            # global_token(user["username"],user["password"])
            
        with allure.step("断言结果"):
            assert res["code"]==200 
            assert res["message"] == "success"
            assert res["data"]["token"] !=None 