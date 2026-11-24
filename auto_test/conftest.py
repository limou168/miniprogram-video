import pytest
import requests
from config.setting import Config
from api.video_api import VideoApi
from api.user_api import UserAPI
from common.logger import logger
from common.db_util import DBUtil
import hashlib
import time
from common.sgin import build_auth_header

def pytest_addoption(parser):
    parser.addoption("--env",action="store",default="test",help="指定运行环境:dev/test/github")

@pytest.fixture(scope="session")
def env_url(request):
    env=request.config.getoption("--env")
    if env == "dev":
        return "127.0.0.1:8081" # 开发环境
    elif env == "test":
        return "127.0.0.1:8080" # 测试环境
    elif env == "github":
        return "127.0.0.1:8080"
    
@pytest.fixture(scope="session")
def global_token(env_url):

    logger.info(f"========== 开始执行全局登录，当前环境: http://{env_url} ==========")
    session=requests.Session()
    res=session.post(f"http://{env_url}/api/user/login",
                 json={"username": "admin", "password": "admin1"}).json()

    if res["code"]==200:  
        token = res["data"]["token"]
        timeone=str(int(time.time()))
      
        # 统一把 Token 塞进 Session 的请求头里
        auth_headers = build_auth_header(token, "admin", Config.SECRET_KEY)
        session.headers.update(auth_headers)

        logger.info(f"全局登录成功，已获取 Token 和散列值，并注入到 Session 请求头中。sign值为: {auth_headers['sign']}")
        logger.info(f"Authorization  {session.headers.get('Authorization')}")
        logger.info(f"timestamp  {session.headers.get('timestamp')}")
        logger.info(f"sign  {session.headers.get('sign')}")

        return session
    else:
        logger.error(f"全局登录失败！返回结果: {res}")
        raise Exception("获取token失败")
    
@pytest.fixture(scope="session")
def video_api(env_url,global_token):
    """返回一个自带 Token 的视频 API 实例"""
    return VideoApi(env_url,global_token)

@pytest.fixture(scope="session")
def user_api(env_url):

    return UserAPI(env_url)

@pytest.fixture(scope='class')
def db_conn():

    print("=== 开启数据库连接 (Setup) ===")
    db=DBUtil()

    yield db
    
    print("=== 关闭数据库连接 (Setup) ===")
    db.close()

@pytest.fixture(scope="session", autouse=True)
def init_test_data(request,env_url):


    env = request.config.getoption("--env")
    
    # 2. 如果不是 github 环境，直接放行，不执行造数逻辑
    if env != "github":
        logger.info(f"当前环境为 {env}，跳过云端全局造数。")
        yield
        return

    logger.info("✅ 检测到 GitHub 环境，开始执行自动化造数...")
    db = DBUtil()
    db=DBUtil()

    db.execute("DELETE FROM sys_video WHERE id = 1")
    db.execute("DELETE FROM sys_user WHERE username = 'admin'")
    insert_sql = """
        INSERT INTO sys_video (id, title, category_id, cover_url, year) 
        VALUES (1, '自动化测试专用视频', 1, 'http://test.jpg', 2025)
    """
    
    db.execute(insert_sql)
    api = UserAPI(url=env_url)
    api.register("admin", "admin1") 

    logger.info("✅ 自动化造数完成：已插入测试视频数据")

    yield
    db.close()