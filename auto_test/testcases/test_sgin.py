import pytest
import allure
import requests
from config.setting import Config
from api.video_api import VideoApi
from common.sgin import build_timestamp, build_sign, build_auth_header

SECRET = Config.SECRET_KEY
USER = "admin"


def make_api(env_url, token=None, extra_headers=None, remove_headers=None, ts=None, sign=None):
    """构造一个只带指定鉴权头的独立 session，避免污染全局 session"""
    s = requests.Session()
    headers = build_auth_header(token, USER, SECRET, timestamp=ts)
    if sign is not None:
        headers["sign"] = sign
    if remove_headers:
        for k in remove_headers:
            headers.pop(k, None)
    if extra_headers:
        headers.update(extra_headers)
    s.headers.update(headers)
    return VideoApi(env_url, s)


@pytest.fixture(scope="module")
def token(global_token):
    return global_token.headers["Authorization"].split(" ")[1]


@allure.feature("鉴权签名校验")
class TestSign:
    @allure.story("缺失鉴权头")
    @pytest.mark.parametrize("missing", ["Authorization", "sign", "timestamp"])
    def test_missing_header(self, env_url, token, missing):
        api = make_api(env_url, token, remove_headers=[missing])
        res = api.get_raw("/api/video/list")
        assert res.status_code ==401, f"缺少 {missing} 时未被拦截: {res.status_code}"

    @allure.story("签名值非法")
    @pytest.mark.parametrize("bad_sign", [
        "",                       # 空sign
        "00000000000000000000000000000000",  # 伪造 32 位
        "abc",                    # 长度不对
        "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ",  # 非 hex
    ])
    def test_invalid_sign(self, env_url, token, bad_sign):
        api = make_api(env_url, token, sign=bad_sign)
        res = api.get_raw("/api/video/list")
        assert res.status_code ==403

    @allure.story("签名与时间戳不匹配（重放/篡改）")
    def test_sign_timestamp_mismatch(self, env_url, token):
        # 用旧 timestamp 算出 sign，再篡改 timestamp 传上去
        old_ts = build_timestamp(-60)
        stolen_sign = build_sign(USER, old_ts, SECRET)
        api = make_api(env_url, token, ts=build_timestamp(), sign=stolen_sign)
        res = api.get_raw("/api/video/list")
        assert res.status_code in (401, 403)

    @allure.story("时间戳过期")
    def test_expired_timestamp(self, env_url, token):
        old_ts = build_timestamp(-3600)  # 1 小时前
        api = make_api(env_url, token, ts=old_ts)  # sign 按旧 ts 正确计算
        res = api.get_raw("/api/video/list")
        assert res.status_code == 402, f"过期时间戳被拦截: {res.status_code}"

    @allure.story("正确签名可通过（对照组）")
    def test_valid_sign_passed(self, env_url, token):
        api = make_api(env_url, token)
        assert api.get_raw("/api/video/list").status_code == 200

        
    @allure.story("无token")
    def test_valid_sign_passed(self, env_url):
        api = make_api(env_url)
        assert api.get_raw("/api/video/list").status_code == 401