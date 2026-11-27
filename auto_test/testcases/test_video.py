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
            assert res["message"]=="success"
            assert "data" in res
           
    @allure.story("获取视频接口-分页")
    @allure.title("测试正常获取")
    @pytest.mark.parametrize("page, size", [
    (1, 10),(2, 40), (1, 100), (10, 30)])
    def test_get_lists(self,video_api,page,size):
        res=video_api.getlist(page,size)
        with allure.step("断言结果"):
            assert res["code"]==200
            assert res["message"]=="success"
            assert "data" in res

       
    @allure.story("获取视频接口-分页")
    @allure.title("测试错误获取")
    @pytest.mark.parametrize("page, size", [
    (0, 10),(-1,-10 ), (9999999999999999, 404), ("abc", 400) # 异常、越界、类型错误
])
    def test_get_lists_error(self,video_api,page,size):
        res=video_api.getlist(page,size)
        with allure.step("断言结果"):
            assert res["code"]==500
            assert res["message"]=="服务器内部错误"
            assert "data" in res


    @allure.story("获取对应id视频接口")
    @allure.title("测试正常获取")
    @pytest.mark.parametrize("video_id, expected_code", [
    (1, 200), (2, 200), (100, 200),   
    (-1, 404), (999999, 404), ("abc", 500) 
])
    def test_getListById(self,video_api,video_id,expected_code):
        res=video_api.getListById(video_id)
        # logger.info(f"对应id视频接口获取成功,数据返回：{res}")
        with allure.step("断言结果"):
            assert res["code"]== expected_code
  


    @allure.story("获取热门视频接口")
    @allure.title("测试正常获取")
    def test_getHot(self,video_api):
        res=video_api.getHot()
        # logger.info(f"获取热门视频接口获取成功,数据返回：{res}")
        with allure.step("断言结果"):
            assert "data" in res
            assert res["message"]=="success"


    @allure.story("获取搜索视频接口")
    @allure.title("测试正常获取")
    def test_register(self,video_api):
        res=video_api.getregister("我")
        # logger.info(f"搜索视频接口获取成功,数据返回：{res}")
        with allure.step("断言结果"):
            assert "data" in res
            assert res["message"]=="success"


    @allure.story("获取搜索窗口推荐文字接口")
    @allure.title("测试正常获取")
    def test_suggest(self,video_api):
        res=video_api.suggest("我")
        # logger.info(f"获取搜索窗口推荐文字接口获取成功,数据返回：{res}")
        with allure.step("断言结果"):
            assert "data" in res
            assert res["message"]=="success"


    @allure.story("获取视频对应集数接口")
    @allure.title("测试正常获取")
    def test_episodes(self,video_api):
        res=video_api.episodes(2)
        # logger.info(f"获取视频对应集数接口成功,数据返回：{res}")
        with allure.step("断言结果"):
            assert "data" in res
            assert res["message"]=="success"

            
    @allure.story("获取分类接口")
    @allure.title("测试正常获取")
    def test_tags(self,video_api):
        res = video_api.tags(3)
        # logger.info(f"获取分类接口获取成功,数据返回：{res}")
        with allure.step("断言结果"):
            assert "data" in res
            assert res["message"]=="success"

