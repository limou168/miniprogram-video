markdown
<div align="center">

# 🎬 微信小程序视频在线播放系统 - 接口自动化测试框架

**一个基于 Python + Pytest 的企业级 API 自动化测试实战项目**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Pytest](https://img.shields.io/badge/Framework-Pytest-orange.svg)
![Requests](https://img.shields.io/badge/Library-Requests-green.svg)
![Allure](https://img.shields.io/badge/Report-Allure-red.svg)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub_Actions-lightgrey.svg)

</div>

---

## 📖 项目简介

本项目是针对【**个人全栈开发 - 微信小程序视频在线播放系统**】后端 API 搭建的接口自动化测试框架。

作为一名测试开发工程师，不仅要会“找 Bug”，更要会“造轮子”。本项目采用**面向对象（OOP）**思想与**分层架构**设计，摒弃了简单的脚本堆砌，实现了一套高内聚、低耦合、易维护的自动化测试解决方案。

## 🛠️ 技术栈

| 技术/工具 | 作用说明 |
| :--- | :--- |
| **Python 3** | 核心编程语言，利用 OOP 思想进行封装 |
| **Requests** | 发送 HTTP 请求，模拟客户端调用 |
| **Pytest** | 核心测试框架，利用 `Fixture` 进行会话管理与参数注入 |
| **PyYAML** | 读取外部 YAML 文件，实现**数据驱动测试 (DDT)** |
| **Allure** | 生成高度可视化的测试报告，支持层级展示与步骤追踪 |
| **Git / GitHub** | 代码版本控制与多人协作管理 |

---

## 📂 项目结构

```text
auto_test/
 ├── api/                    # 【接口封装层】隔离底层 HTTP 实现，只暴露业务方法
 │    └── user_api.py        
 ├── config/                 # 【配置层】管理全局变量、环境地址等
 │    └── setting.py         
 ├── data/                   # 【数据层】测试数据与代码分离
 │    └── users.yaml         
 ├── testcases/              # 【测试用例层】纯业务断言与测试逻辑
 │    └── test_user.py       
 ├── common/                 # 【公共工具层】如读取 YAML、加解密工具等
 │    └── util.py            
 ├── conftest.py             # Pytest 全局配置 / 预置 Fixture (如 Token 管理)
 ├── pytest.ini              # 框架全局配置文件
 └── requirements.txt        # 项目依赖清单
✨ 框架核心亮点
1. 分层架构设计 (分层解耦)
API 层 (api/)：对 requests 进行二次封装，处理 URL 拼接、公共请求头等。若接口字段发生变更，仅需修改 API 层，完美实现“对修改关闭，对扩展开放”。

Case 层 (testcases/)：测试脚本极度轻薄，测试人员仅需关注“输入数据、调用方法、断言结果”三步。

2. 数据驱动测试 (DDT)
测试用例不再写死参数。通过 @pytest.mark.parametrize 结合 PyYAML，将数据抽离至 data/users.yaml。后续增加测试场景零代码修改。

3. 可视化测试报告 (Allure)
全面接入 Allure，引入 @allure.epic、@allure.story 和 with allure.step。

测试报告呈现树状业务层级（Epic -> Feature -> Story），精准还原测试步骤，失败时自带详细堆栈日志，极大提升了缺陷排查效率。

4. 真实缺陷发现 (Bug Finding)
💡 实战记录：在框架调试期间，成功利用接口脚本发现后端系统缺陷——“重复用户注册时，后端未捕获数据库唯一索引冲突异常，直接抛出 500 系统内部错误”，体现了测试实战能力。

🚀 快速开始
1. 环境准备
确保本地已安装 Python 3.8+，并配置好 Allure 环境。

2. 安装依赖
bash
pip install -r requirements.txt
3. 执行测试用例
bash
# 运行所有用例并生成测试数据
python -m pytest --alluredir=./allure-results
4. 生成并查看可视化报告
bash
allure serve ./allure-results
🗺️ 后续演进路线 (Roadmap)
☑ 基础 Requests 封装与用例编写
☑ 引入 YAML 数据驱动
☑ 接入 Allure 测试报告体系
□ 引入 conftest.py 实现全局 Token 自动获取与注入
□ 引入 Logging 模块实现日志落盘管理
□ 接入 GitHub Actions 实现 CI/CD 持续集成 (Push 代码自动跑测试)
□ 引入企业级通知机制 (如钉钉/飞书机器人通知测试结果)
<div align="center"> <b>Made with ❤️ by limou</b><br> <i>持续学习，用技术保障质量。</i> </div> ```