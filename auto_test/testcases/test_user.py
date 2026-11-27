import pytest
import allure
import requests
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


    @allure.story("登录接口")
    @allure.title("测试登录失败情况")
    def test_login_fail(self,user_api):
        with allure.step(f"发送登录请求，用户: 错误用户名"):
            logger.info(f"=== 开始测试登录接口，测试数据: 错误用户名 ===") 
            res=user_api.login("wronguser","wrongpassword")
            
        with allure.step("断言结果"):
            assert res["code"]==403 
            assert res["message"] == "用户名错误"

    @allure.story("注册接口")
    @allure.title("测试注册失败情况")
    def test_register_fail(self,user_api):
        with allure.step(f"发送注册请求，用户: 已存在用户名"):
            logger.info(f"=== 开始测试注册接口，测试数据: 已存在用户名 ===") 
            res=user_api.register("admin","admin1")
            
        with allure.step("断言结果"):
            assert res["code"]==500 
            assert res["message"] == "用户名已被注册"

    @allure.story("注册接口")
    @allure.title("测试注册空用户名情况")
    def test_register_empty(self,user_api):
        with allure.step(f"发送注册请求，用户: 空用户名"):     
            res=user_api.register(None,"123111")
            logger.info(f"=== 开始测试注册接口，测试数据: 空用户名 ===  {res}") 
        with allure.step("断言结果"):
            assert res["code"]==400 
            logger.info(f"这是一个BUG") 
            assert res["message"] == "用户名不能为空"


    @allure.story("登录接口")
    @allure.title("测试登录空密码情况")
    def test_login_empty_password(self,user_api):
        with allure.step(f"发送登录请求，用户: 空密码"):
            logger.info(f"=== 开始测试登录接口，测试数据: 空密码 ===") 
            res=user_api.login("admin","")
            
        with allure.step("断言结果"):
            assert res["code"]==400 
            assert res["message"] == "密码不能为空" 


    ## 边界测试
    @allure.story("注册接口")
    @allure.title("测试注册超长用户名情况")
    def test_register_long_username(self,user_api):
        long_username = "a" * 256  # 超过255个字符的用户名
        with allure.step(f"发送注册请求，用户: 超长用户名"):
            logger.info(f"=== 开始测试注册接口，测试数据: 超长用户名 ===") 
            res=user_api.register(long_username,"password123")
            
        with allure.step("断言结果"):
            assert res["code"]==400 
            assert res["message"] == "用户名长度为3-20个字符"

    ## name长度不低于3

    @allure.story("注册接口")
    @allure.title("测试注册短用户名情况")
    def test_register_short_username(self,user_api):
        short_username = "ab"  # 少于3个字符的用户名
        with allure.step(f"发送注册请求，用户: 短用户名"):
            logger.info(f"=== 开始测试注册接口，测试数据: 短用户名 ===") 
            res=user_api.register(short_username,"password123")
            
        with allure.step("断言结果"):
            assert res["code"]==400 
            assert res["message"] == "用户名长度为3-20个字符"
