import pytest
import allure
from common.logger import logger


@allure.epic("用户收藏接口测试")
@allure.feature("收藏模块")
class TestFavorite:

    @allure.story("收藏")
    @allure.title("测试正常获取")
    def test_toggle(self,favorite_api):
        res=favorite_api.toggle_favorite("2")
        logger.info(f"返回数据{res}",res)

        with allure.step("断言结果"):
            assert res["message"]=='success'
            assert res["code"]==200
         

    @allure.title("测试收藏错误获取")
    def test_toggle_error(self,favorite_api):
        res=favorite_api.toggle_favorite("c")
        logger.info(f"返回数据{res}",res)

        with allure.step("断言结果"):
            assert res["message"]=='服务器内部错误'
            assert res["code"]==500

    @allure.title("测试收藏正常获取")
    def test_if_check(self,favorite_api):
        res=favorite_api.if_check("1")
        logger.info(f"返回数据{res}",res)

        with allure.step("断言结果"):
            assert res["message"]=='success'
            assert res["code"]==200
            assert res["data"]==True

    @allure.title("测试收藏错误获取")
    def test_if_check_error(self,favorite_api):
        res=favorite_api.if_check("3")

        logger.info(f"返回数据{res}",res)
        with allure.step("断言结果"):
            assert res["message"]=='success'
            assert res["code"]==200
            assert res["data"]==False

    @allure.title("测试获取对应收藏列表")
    def test_getlist(self,favorite_api):
        res=favorite_api.get_list()

        with allure.step("断言结果"):
                assert res["message"]=='success'
                assert res["code"]==200
                