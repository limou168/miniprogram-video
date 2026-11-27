import pytest
import allure
from common.logger import logger

@allure.epic("业务全链路测试")
class TestBusinessFlow:
    
    @allure.feature("用户与收藏模块")
    @allure.story("收藏与取消收藏全流程")
    @allure.title("测试：登录 -> 收藏 -> 查列表 -> 取消收藏")
    def test_favorite_flow(self,favorite_api):
        id='10'

        with allure.step("步骤1：登录获取 Token（前置准备）"):
            logger.info("已登录，准备开始收藏流程")


        with allure.step(f"步骤2：收藏视频 ID={id}"):
            res=favorite_api.toggle_favorite(id)

            assert res["code"]==200
            assert res["message"] =="success"
        with allure.step("步骤3：确定已经收藏"):
            if_check=favorite_api.if_check(id)
            assert if_check["code"]==200
            assert if_check["message"] =="success"

        with allure.step("步骤4：查询收藏列表，验证刚才的视频在里面"):
            res_list=favorite_api.get_list()
            assert res_list["code"]==200
            assert res_list["message"] =="success"

            favorite_video_ids = [str(item["videoId"]) for item in res_list["data"]]
            assert id in favorite_video_ids, f"收藏列表里没找到视频 {id}"

        with allure.step("步骤5：取消收藏视频"):
            res_unfav = favorite_api.toggle_favorite(id) 
            assert res_unfav["code"] == 200
            
        with allure.step("步骤5：再次查询收藏列表，验证视频已被移除"):
            res_list_after = favorite_api.get_list()
            favorite_video_ids_after = [(item["videoId"]) for item in res_list["data"]]
            assert id not in favorite_video_ids_after, " 取消收藏后，视频依然在列表中！"
            
        logger.info("收藏全流程测试通过")

    @pytest.mark.parametrize("name, paw", [("test1","paw123456")])
    def test_login_flow(self,user_api,name,paw,db_conn):
        try:
            
            with allure.step(f"步骤1:注册用户"):
                res=user_api.register(name,paw)
                assert res["code"]==200
                assert res["message"] =="success"
            with allure.step(f"步骤:登录注册用户"):
            
                res_lg=user_api.login(name,paw)
                assert res_lg["code"]==200
                assert res_lg["message"] =="success"
                token=res_lg["data"]["token"]

                
            with allure.step(f"步骤3:获取册用户信息"):
                info=user_api.get_info(token,name)

                assert info["code"]==200
                assert info["message"] =="success"
                assert info["data"]["username"] ==name

            with allure.step(f"步骤4:修改用户信息"):
                up=user_api.updateInfo(name="修改名字测试",nickname="修改昵称测试")

                logger.info(f"修改用户信息{up}")
                assert up["code"]==200
                assert up["message"] =="success"

            with allure.step(f"步骤5:检查是否修改"):
                info_up=user_api.get_info(token,name)
                assert info_up["data"]["nickname"] =="修改昵称测试"

        finally:
            with allure.step(f"删除测试信息"):
                
                db_conn.execute(f"delete from sys_user where username='{name}'")
        