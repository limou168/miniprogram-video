import time
import hashlib


def build_timestamp(offset: int = 0) -> str:
    """构建时间戳，默认返回当前时间戳，offset为偏移量，单位为秒（负数表示过去）"""
    return str(int(time.time()) + offset)


def build_sign(username: str, timestamp: str, secret_key: str) -> str:
    """构建签名，使用MD5加密"""
    sign_str = username + timestamp + secret_key
    md5_obj = hashlib.md5(sign_str.encode())
    return md5_obj.hexdigest()


def build_auth_header(token: str, name: str, secret_key: str, timestamp: str = None) -> dict:
    """构建请求头，包含Authorization、timestamp、sign

    timestamp 不传时自动使用当前时间，保证 token/timestamp/sign 三者对应
    """
    ts = timestamp if timestamp is not None else build_timestamp()
    return {
        "Authorization": f"Bearer {token}",
        "timestamp": ts,
        "sign": build_sign(name, ts, secret_key)
    }