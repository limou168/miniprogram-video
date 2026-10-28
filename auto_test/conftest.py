import pytest
import requests
from config.setting import Config
from api.video_api import VideoApi
from api.user_api import UserAPI
from common.logger import logger
from common.db_util import DBUtil

def pytest_addoption(parser):
    parser.addoption("--env",action="store",default="test",help="指定运行环境:dev/test")

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
def global_token(request,env_url):

    env = request.config.getoption("--env")
    if env == "github":
        pytest.skip("GitHub Actions 环境无本地后端服务，跳过依赖登录的用例")

    logger.info(f"========== 开始执行全局登录，当前环境: http://{env_url} ==========")
    session=requests.Session()
    res=session.post(f"http://{env_url}/api/user/login",
                 json={"username": "user1", "password": "password1"}).json()

    if res["code"]==200:  
        token = res["data"]["token"]
        # 统一把 Token 塞进 Session 的请求头里
        session.headers.update({"Authorization": f"Bearer {token}"})
        logger.info("全局登录成功，已获取 Token")
        return session
    else:
        logger.error(f"全局登录失败！返回结果: {res}")
        raise Exception("获取token失败")
    
@pytest.fixture(scope="session")
def video_api(env_url,global_token):
    """返回一个自带 Token 的视频 API 实例"""
    return VideoApi(env_url,session=global_token)

@pytest.fixture(scope="session")
def user_api(env_url):
    """返回一个自带 Token 的视频 API 实例"""
    return UserAPI(env_url)

@pytest.fixture(scope='class')
def db_conn(request):

    env = request.config.getoption("--env")

    # 如果是 GitHub Actions 环境，直接跳过这个 fixture
    if env == "github":
        pytest.skip("GitHub Actions 环境无法连接本地数据库，跳过该用例")
        logger.error("环境无法连接本地数据库，跳过该用例")

    print("=== 开启数据库连接 (Setup) ===")
    db=DBUtil()

    yield db
    
    print("=== 关闭数据库连接 (Setup) ===")
    db.close()

@pytest.fixture(scope="session", autouse=True)
def init_test_data():
    db=DBUtil()

    db.execute("DELETE FROM sys_video WHERE id = 1")

    insert_sql = """
        INSERT INTO sys_video (id, title, category_id, cover_url, year) 
        VALUES (1, '自动化测试专用视频', 1, 'http://test.jpg', 2025)
    """
    db.execute(insert_sql)
    logger.info("✅ 自动化造数完成：已插入测试视频数据")

    yield
    db.close