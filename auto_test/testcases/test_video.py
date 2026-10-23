import pytest
import allure
from common.logger import logger
@allure.epic("小程序视频接口测试")
@allure.feature("视频模块")
class TestVideo:

    @allure.story("获取视频接口")
    @allure.title("测试正常获取")
    def test_get_list(self,video_api):
        res=video_api.getlist()
        with allure.step("断言结果"):
            assert res["code"]==200
            assert "data" in res
            logger.info(f"获取视频接口获取成功,数据返回：{res}")
    @allure.story("获取对应id视频接口")
    @allure.title("测试正常获取")
    def test_getListById(self,video_api):
        res=video_api.getListById("1")
        logger.info(f"对应id视频接口获取成功,数据返回：{res}")
        with allure.step("断言结果"):
            assert res["data"]["title"] =="阿龙2025"
    @allure.story("获取热门视频接口")
    @allure.title("测试正常获取")
    def test_getHot(self,video_api):
        res=video_api.getHot()
        logger.info(f"获取热门视频接口获取成功,数据返回：{res}")
        with allure.step("断言结果"):
            assert "data" in res
    @allure.story("获取搜索视频接口")
    @allure.title("测试正常获取")
    def test_register(self,video_api):
        res=video_api.getregister("我")
        logger.info(f"搜索视频接口获取成功,数据返回：{res}")
        with allure.step("断言结果"):
            assert "data" in res
    @allure.story("获取搜索窗口推荐文字接口")
    @allure.title("测试正常获取")
    def test_suggest(self,video_api):
        res=video_api.suggest("我")
        logger.info(f"获取搜索窗口推荐文字接口获取成功,数据返回：{res}")
        with allure.step("断言结果"):
            assert "data" in res
    @allure.story("获取视频对应集数接口")
    @allure.title("测试正常获取")
    def test_episodes(self,video_api):
        res=video_api.episodes(2)
        logger.info(f"获取视频对应集数接口成功,数据返回：{res}")
        with allure.step("断言结果"):
            assert "data" in res
    @allure.story("获取分类接口")
    @allure.title("测试正常获取")
    def test_tags(self,video_api):
        res = video_api.tags(1)
        logger.info(f"获取分类接口获取成功,数据返回：{res}")
        with allure.step("断言结果"):
            assert "data" in res
