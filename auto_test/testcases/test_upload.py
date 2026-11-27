from common.logger import logger
from api.upload_api import UploadAPI
import allure


class TestUpload:
    @allure.title("测试文件上传")
    def test_up(self,upload_api):
        path =("data/测试图片.jpg")
        res=upload_api.upload_cover(path)

        logger.info("三方服务依赖测试,本地服务未配置")
        with allure.step("断言结果"):
            assert res["code"]==500
            assert res["data"]==None
